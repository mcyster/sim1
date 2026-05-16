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
        owner_income = person.productivity * economy.food_price
        if person.hunger > 1.0:
            return Role.WORKER
        return Role.WORKER if worker_income >= owner_income else Role.OWNER

    def choose_purchase(self, person, economy) -> float:
        return person.hunger

    def choose_employment(self, person, economy):
        if not economy.firms:
            return None
        best_firm = max(economy.firms, key=lambda firm: firm.wage_offer)
        # compare wage vs self-production value
        worker_income = person.productivity * best_firm.wage_offer
        owner_income = person.productivity * economy.food_price
        if worker_income >= owner_income:
            return best_firm
        return None


    def choose_wage(self, person, firm, economy) -> float:
        # deprecated: use offer_wage
        return self.offer_wage(person, firm, economy)

    def offer_wage(self, person, firm, economy) -> float:
        # default: target a fraction of price with slight adjustment
        target = 0.6 * economy.food_price
        if len(firm.workers) == 0:
            target *= 1.05
        else:
            target *= 0.98
        return max(0.01, min(target, economy.food_price))
