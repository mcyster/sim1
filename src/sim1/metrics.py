from statistics import mean
from .enums import Role


class Metrics:
    def __init__(self):
        self.history = []

    def record(self, economy):
        people = economy.people
        if not people:
            return
        data = {
            "price": economy.food_price,
            "food": economy.food_supply,
            "avg_money": mean(p.money for p in people),
            "avg_hunger": mean(p.hunger for p in people),
            "working": sum(1 for p in people if (p.employed or p.role == Role.OWNER)),
        }
        self.history.append(data)
