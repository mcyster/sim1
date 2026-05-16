import random
from .enums import Role
from .brain import DefaultBrain, Brain


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
        self.brain: Brain = DefaultBrain()

    # --- Decisions ---
    def decide_role(self, economy, avg_wage: float):
        self.role = self.brain.choose_role(self, economy, avg_wage)
        self.employed = False
        self.firm = None

    def buy(self, requested_amount: float, economy) -> float:
        price = economy.food_price
        if price <= 0 or requested_amount <= 0:
            return 0.0
        affordable = self.money / price
        amount = min(requested_amount, affordable, economy.food_supply)
        if amount <= 0:
            return 0.0
        cost = amount * price
        self.money -= cost
        self.food += amount
        economy.food_supply -= amount
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

    def tick(self, economy) -> None:
        # consumption + physiological updates
        ate = self.consume()
        if ate >= 1.0:
            self.health = min(100.0, self.health + 1.0)
            self.happiness = min(100.0, self.happiness + 0.5)
        else:
            self.health = max(0.0, self.health - 2.0)
            self.happiness = max(0.0, self.happiness - 1.0)
        # unemployment penalty
        if not self.employed:
            self.happiness = max(0.0, self.happiness - 0.2)
