from .person import Person


class Economy:
    def __init__(self, population_size=1000):
        self.people = [Person() for _ in range(population_size)]
        self.food_price = 1.0
        self.total_food = 0.0
        self.food_supply = 0.0
        self.firms = []
        self.day = 0
        # last tick transaction stats
        self.transactions = 0
        self.quantity_sold = 0.0

    # --- Helpers ---
    def average_wage(self):
        if not self.firms:
            return 0.5
        return sum(firm.wage_offer for firm in self.firms) / len(self.firms)

    # --- Markets ---
    def add_food(self, amount: float):
        self.total_food = amount
        self.food_supply += amount
