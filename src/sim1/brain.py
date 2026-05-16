from .enums import Role


class Brain:
    def choose_role(self, person, economy, avg_wage: float) -> Role:
        raise NotImplementedError

    def choose_purchase(self, person, economy) -> float:
        raise NotImplementedError

    def choose_employment(self, person, economy):
        raise NotImplementedError

    def choose_wage(self, person, firm, economy) -> float:
        raise NotImplementedError

    def offer_wage(self, person, firm, economy) -> float:
        raise NotImplementedError


class DefaultBrain(Brain):
    def choose_role(self, person, economy, avg_wage: float) -> Role:
        worker_income = person.productivity * avg_wage
        # expected per-unit margin as simple profit signal
        expected_profit = economy.food_price - avg_wage
        owner_income = person.productivity * max(expected_profit, 0.0)
        # panic: if no food for N ticks, force action
        panic_threshold = 3
        if getattr(person, "no_food_ticks", 0) >= panic_threshold:
            # if no firms, try to start one; otherwise work
            if not economy.firms:
                return Role.OWNER
            return Role.WORKER
        if person.hunger > 1.0:
            return Role.WORKER
        # adaptive entry threshold based on affordability (urgency)
        base_threshold = 2.0 * avg_wage + 1.0
        price = max(economy.food_price, 1e-6)
        afford_ratio = person.money / price
        # urgency: 0 (comfortable) -> 1 (cannot afford food)
        urgency = max(0.0, 1.0 - afford_ratio)
        owner_threshold = base_threshold * (1.0 - 0.8 * urgency)
        if person.money < owner_threshold:
            return Role.WORKER
        # become owner when expected profit is positive and beats worker option
        if expected_profit > 0 and owner_income > worker_income:
            return Role.OWNER
        return Role.WORKER

    def choose_purchase(self, person, economy) -> float:
        # maintain a small buffer of food instead of only reacting to hunger
        target_food = 2.0
        needed = max(0.0, target_food - person.food)
        return needed

    def choose_employment(self, person, economy):
        if not economy.firms:
            return None
        best_firm = max(economy.firms, key=lambda firm: firm.wage_offer)
        # if starving, accept any available job
        if person.hunger > 1.0:
            return best_firm
        # reservation wage: must cover subsistence food
        subsistence = 0.5
        reservation_wage = economy.food_price * subsistence
        if best_firm.wage_offer < reservation_wage:
            return None
        # employment decision: accept any positive-paying job
        worker_income = person.productivity * best_firm.wage_offer
        if worker_income > 0.0:
            return best_firm
        return None


    def choose_wage(self, person, firm, economy) -> float:
        # deprecated: use offer_wage
        return self.offer_wage(person, firm, economy)

    def offer_wage(self, person, firm, economy) -> float:
        # profit/health-based adjustment (decoupled from price)
        base = firm.wage_offer or (0.5 * economy.food_price)
        if getattr(firm, "health", 1.0) > 1.0:
            base *= 1.02
        else:
            base *= 0.98
        return max(0.01, base)

    def allocate_capital(self, person, firm, economy) -> float:
        # reinvest if firm struggling or small
        if getattr(firm, "health", 1.0) < 1.0:
            return min(person.money * 0.2, person.money)
        return 0.0

    def should_produce(self, person, firm, economy) -> bool:
        # produce only if expected margin is positive
        return economy.food_price > firm.wage_offer
