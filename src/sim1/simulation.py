import random
from .economy import Economy
from .firms import Firm
from .enums import Role


def choose_roles(economy: Economy):
    average_wage = economy.average_wage()
    for person in economy.people:
        person.decide_role(economy, average_wage)
    # ensure at least one owner exists
    if not any(p.role == Role.OWNER for p in economy.people):
        max(economy.people, key=lambda p: p.productivity).role = Role.OWNER


def average_wage(economy: Economy):
    if not economy.firms:
        return 0.5
    return sum(firm.wage for firm in economy.firms) / len(economy.firms)


def create_firms(economy: Economy):
    economy.firms = []
    for person in economy.people:
        if person.role == Role.OWNER:
            # initial wage_offer (will be updated by owner brain)
            initial_wage = economy.food_price * 0.5
            # enforce minimum owner capital to start firm
            min_capital = 2.0 * initial_wage + 1.0
            if person.money < min_capital:
                person.role = Role.WORKER
                continue
            firm = Firm(owner=person)
            firm.wage_offer = initial_wage
            # seed firm with owner capital
            initial_capital = min(person.money * 0.2, person.money)
            person.money -= initial_capital
            firm.cash += initial_capital
            economy.firms.append(firm)
            person.firm = firm


def match_labor(economy: Economy):
    # clear previous assignments
    for firm in economy.firms:
        firm.workers = []
    for person in economy.people:
        person.employed = False
        person.firm = None

    # owners set wage offers
    for firm in economy.firms:
        owner = firm.owner
        # allow owner to inject capital
        amount = owner.brain.allocate_capital(owner, firm, economy)
        if amount > 0:
            owner.money -= amount
            firm.cash += amount
        offered_wage = owner.brain.offer_wage(owner, firm, economy)
        firm.wage_offer = max(0.01, min(offered_wage, economy.food_price * 2.0))

    # each person chooses employment
    for person in economy.people:
        if person.role != Role.WORKER:
            continue
        employer = person.brain.choose_employment(person, economy)
        if employer is not None:
            if employer.hire(person, economy):
                person.employed = True
                person.firm = employer

    # update firm efficiencies after hiring (diminishing returns with size)
    alpha = 0.2
    for firm in economy.firms:
        worker_count = len(firm.workers)
        firm.efficiency = firm.base_eff / (1.0 + alpha * worker_count)


def produce_food(economy: Economy):
    total = 0.0
    # firms produce with efficiency applied to total labor
    for firm in economy.firms:
        # owner decides whether to produce
        produce = firm.owner.brain.should_produce(firm.owner, firm, economy)
        firm.produced = bool(produce)
        if not firm.produced:
            continue
        labor = firm.owner.productivity + sum(worker.productivity for worker in firm.workers)
        output = labor * firm.efficiency
        total += output
    economy.add_food(total)


def pay_wages(economy: Economy):
    for firm in economy.firms:
        # only pay wages if firm produced this tick
        if not firm.produced:
            continue
        # pay workers
        for worker in firm.workers:
            wage = worker.productivity * firm.wage_offer
            worker.money += wage
            firm.cash -= wage
        # do NOT assign revenue here; revenue comes from actual sales in trading()


def calc_supply(economy: Economy):
    # existing food carried over + newly produced
    carried = sum(p.food for p in economy.people)
    return carried + economy.total_food


def calc_demand(economy: Economy):
    # affordability-based demand: sum of what people can pay for
    price = max(economy.food_price, 1e-6)
    total = 0.0
    for person in economy.people:
        # desired amount from brain (e.g., hunger)
        desired = person.brain.choose_purchase(person, economy)
        # cap by affordability
        affordable = person.money / price
        total += max(0.0, min(desired, affordable))
    return total


def update_price(economy: Economy, supply: float, demand: float):
    # transaction-based pricing using realized sales
    price = max(economy.food_price, 1e-6)
    sold = getattr(economy, "quantity_sold", 0.0)
    # if nothing traded, price is too high -> decay
    if sold <= 0.0:
        economy.food_price = max(0.01, price * 0.95)
        return

    # compare sold vs available supply to adjust price
    # if sold > supply -> excess demand -> price up
    # if sold < supply -> excess supply -> price down
    alpha = 0.02
    denom = max(supply, 1e-6)
    delta = alpha * (sold - supply) / denom
    # cap movement per tick
    delta = max(-0.05, min(0.05, delta))
    economy.food_price = max(0.01, price * (1.0 + delta))


def update_wage(economy: Economy):
    # adjust wage based on labor supply vs demand
    supply = sum(1 for p in economy.people if getattr(p, "_willing", False))
    demand = sum(1 for p in economy.people if p.employed)

    if supply == 0:
        return

    pressure = (supply - demand) / supply
    beta = 0.05
    economy.wage = max(0.01, economy.wage * (1.0 - beta * pressure))


def trading(economy: Economy):
    price = economy.food_price
    total_spent = 0.0
    transaction_count = 0
    quantity_sold = 0.0

    for person in economy.people:
        requested = person.brain.choose_purchase(person, economy)
        cost = person.buy(requested, economy)
        total_spent += cost
        if cost > 0.0:
            transaction_count += 1
            quantity_sold += cost / max(price, 1e-6)

    # distribute actual sales revenue to firms proportional to output
    total_output = 0.0
    firm_outputs = {}

    for firm in economy.firms:
        labor = firm.owner.productivity + sum(worker.productivity for worker in firm.workers)
        output = labor * firm.efficiency
        firm_outputs[firm] = output
        total_output += output

    if total_output > 0 and total_spent > 0:
        for firm, output in firm_outputs.items():
            share = output / total_output
            firm.cash += total_spent * share

    # distribute firm profits/losses to owners after sales
    surviving_firms = []
    for firm in economy.firms:
        profit = firm.cash
        # update health based on profit
        if profit < 0:
            firm.health -= 0.1
        else:
            firm.health += 0.05
        firm.health = max(0.0, min(2.0, firm.health))

        # transfer profit/loss to owner
        firm.owner.money += firm.cash
        firm.cash = 0.0

        # cull unhealthy firms (owner becomes worker)
        if firm.health > 0.0:
            surviving_firms.append(firm)
        else:
            # use enum, not raw string
            firm.owner.role = Role.WORKER
            firm.owner.firm = None

    economy.firms = surviving_firms
    # record transaction stats
    economy.transactions = transaction_count
    economy.quantity_sold = quantity_sold




def tick(economy: Economy):
    economy.day += 1
    choose_roles(economy)
    create_firms(economy)
    match_labor(economy)
    produce_food(economy)
    pay_wages(economy)
    supply = calc_supply(economy)
    demand = calc_demand(economy)
    update_price(economy, supply, demand)
    trading(economy)
    # per-person updates
    for person in economy.people:
        person.tick(economy)
