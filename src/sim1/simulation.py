import random
from .economy import Economy
from .firms import Firm
from .enums import Role


def choose_roles(economy: Economy):
    avg = economy.avg_wage()
    for p in economy.people:
        p.decide_role(economy, avg)
    # ensure at least one owner exists
    if not any(p.role == Role.OWNER for p in economy.people):
        max(economy.people, key=lambda p: p.productivity).role = Role.OWNER


def avg_wage(economy: Economy):
    if not economy.firms:
        return 0.5
    return sum(f.wage for f in economy.firms) / len(economy.firms)


def create_firms(economy: Economy):
    economy.firms = []
    for p in economy.people:
        if p.role == Role.OWNER:
            f = Firm(owner=p)
            # initial wage tied to price
            f.wage = economy.food_price * 0.5
            economy.firms.append(f)
            p.firm = f


def hire_workers(economy: Economy):
    workers = [p for p in economy.people if p.role == Role.WORKER]

    # workers choose best wage firm
    for p in workers:
        if not economy.firms:
            continue
        best = max(economy.firms, key=lambda f: f.wage)
        # always hire; profitability handled via firm cash (owner absorbs losses)
        best.workers.append(p)
        p.employed = True
        p.firm = best

    # update firm efficiencies after hiring (diminishing returns with size)
    alpha = 0.2
    for f in economy.firms:
        n = len(f.workers)
        f.efficiency = f.base_eff / (1.0 + alpha * n)

    # adapt wages based on hiring outcome
    for f in economy.firms:
        if len(f.workers) == 0:
            # couldn't attract workers -> raise wage
            f.wage *= 1.05
        else:
            # has workers -> slight downward pressure
            f.wage *= 0.99
        # keep wage reasonable
        f.wage = max(0.01, min(f.wage, economy.food_price * 2.0))


def produce_food(economy: Economy):
    total = 0.0
    # firms produce with efficiency applied to total labor
    for f in economy.firms:
        labor = f.owner.productivity + sum(w.productivity for w in f.workers)
        output = labor * f.efficiency
        total += output
    economy.add_food(total)


def pay_wages(economy: Economy):
    for f in economy.firms:
        # pay workers
        for w in f.workers:
            wage = w.productivity * f.wage
            w.money += wage
            f.cash -= wage
        # do NOT assign revenue here; revenue comes from actual sales in trading()


def calc_supply(economy: Economy):
    # existing food carried over + newly produced
    carried = sum(p.food for p in economy.people)
    return carried + economy.total_food


def calc_demand(economy: Economy):
    # each person wants 1 unit per tick
    return float(len(economy.people))


def update_price(economy: Economy, supply: float, demand: float):
    # small, damped adjustment to avoid explosions
    alpha = 0.01
    denom = max(supply, 1e-6)
    delta = alpha * (demand - supply) / denom
    # cap movement per tick
    delta = max(-0.05, min(0.05, delta))
    economy.food_price = max(0.01, economy.food_price * (1.0 + delta))


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

    for p in economy.people:
        cost = p.decide_purchase(economy)
        total_spent += cost

    # distribute actual sales revenue to firms proportional to output
    total_output = 0.0
    firm_outputs = {}

    for f in economy.firms:
        labor = f.owner.productivity + sum(w.productivity for w in f.workers)
        output = labor * f.efficiency
        firm_outputs[f] = output
        total_output += output

    if total_output > 0 and total_spent > 0:
        for f, output in firm_outputs.items():
            share = output / total_output
            f.cash += total_spent * share

    # distribute firm profits/losses to owners after sales
    surviving_firms = []
    for f in economy.firms:
        profit = f.cash
        # update health based on profit
        if profit < 0:
            f.health -= 0.1
        else:
            f.health += 0.05
        f.health = max(0.0, min(2.0, f.health))

        # transfer profit/loss to owner
        f.owner.money += f.cash
        f.cash = 0.0

        # cull unhealthy firms (owner becomes worker)
        if f.health > 0.0:
            surviving_firms.append(f)
        else:
            f.owner.role = "worker"
            f.owner.firm = None

    economy.firms = surviving_firms


def consumption(economy: Economy):
    for p in economy.people:
        p._ate = p.consume()


def update_health(economy: Economy):
    for p in economy.people:
        if getattr(p, "_ate", 0.0) >= 1.0:
            p.health = min(100.0, p.health + 1.0)
        else:
            p.health = max(0.0, p.health - 2.0)


def update_happiness(economy: Economy):
    for p in economy.people:
        if getattr(p, "_ate", 0.0) >= 1.0:
            p.happiness = min(100.0, p.happiness + 0.5)
        else:
            p.happiness = max(0.0, p.happiness - 1.0)
        # slight penalty for unemployment
        if not p.employed:
            p.happiness = max(0.0, p.happiness - 0.2)
        # cleanup temp field
        if hasattr(p, "_ate"):
            delattr(p, "_ate")


def tick(economy: Economy):
    choose_roles(economy)
    create_firms(economy)
    hire_workers(economy)
    produce_food(economy)
    pay_wages(economy)
    supply = calc_supply(economy)
    demand = calc_demand(economy)
    update_price(economy, supply, demand)
    trading(economy)
    consumption(economy)
    update_health(economy)
    update_happiness(economy)
