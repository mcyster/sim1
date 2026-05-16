class Firm:
    def __init__(self, owner):
        self.owner = owner
        self.workers = []
        self.wage = 0.5
        self.cash = 0.0
        # efficiency model
        self.base_eff = owner.productivity
        self.efficiency = self.base_eff
        self.health = 1.0
