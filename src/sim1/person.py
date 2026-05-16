import random
from .enums import Role


class Person:
    def __init__(self):
        self.money = 10.0
        self.food = 1.0
        self.happiness = 50.0
        self.health = 50.0
        self.productivity = random.uniform(0.5, 1.5)
        self.employed = False
        self.role = Role.WORKER
        self.firm = None
        self.hunger = 0.0

    # --- Decisions ---
    def decide_role(self, economy, avg_wage: float):
        worker_income = self.productivity * avg_wage
        owner_income = self.productivity * economy.food_price
        if self.hunger > 1.0:
            self.role = Role.WORKER
        else:
            self.role = Role.WORKER if worker_income >= owner_income else Role.OWNER
        self.employed = False
        self.firm = None

    def decide_purchase(self, economy):
        price = economy.food_price
        if price <= 0:
            return 0.0
        need = self.hunger
        if need <= 0:
            return 0.0
        affordable = self.money / price
        buy = min(need, affordable, economy.food_supply)
        if buy <= 0:
            return 0.0
        cost = buy * price
        self.money -= cost
        self.food += buy
        economy.food_supply -= buy
        return cost

    def consume(self):
        eat = min(1.0, self.food)
        self.food -= eat
        # update hunger
        self.hunger += 1.0
        self.hunger -= eat
        if self.hunger < 0.0:
            self.hunger = 0.0
        if self.hunger > 3.0:
            self.hunger = 3.0
        return eat
