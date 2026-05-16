class Firm:
    def __init__(self, owner):
        self.owner = owner
        self.workers = []
        self.wage_offer = 0.5
        self.cash = 0.0
        # efficiency model
        self.base_eff = owner.productivity
        self.efficiency = self.base_eff
        self.health = 1.0
        # explicit production flag for this tick
        self.produced = False

    # --- Hiring API ---
    def can_hire(self, person, economy) -> bool:
        # Profitability gate: do not hire if wage exceeds price (negative margin)
        if self.wage_offer > economy.food_price:
            return False

        # Liquidity gate: avoid hiring when already cash-negative
        if self.cash < 0.0:
            return False

        # Basic affordability: must cover this worker's expected wage
        expected_wage = person.productivity * self.wage_offer
        if self.cash < expected_wage:
            return False

        return True

    def hire(self, person, economy) -> bool:
        # Enforce constraints here; do not rely on callers
        # Ensure firm has enough cash; top up from owner if possible
        expected_wage = person.productivity * self.wage_offer

        if self.cash < expected_wage:
            needed = expected_wage - self.cash
            transfer = min(needed, self.owner.money)
            if transfer > 0:
                self.owner.money -= transfer
                self.cash += transfer

        # Re-check constraints after potential funding
        if not self.can_hire(person, economy):
            return False

        # Final affordability check for this worker
        if self.cash < expected_wage:
            return False

        self.workers.append(person)
        return True
