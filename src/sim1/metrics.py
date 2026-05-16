from statistics import mean
from .enums import Role


class Metrics:
    def __init__(self):
        self.history = []
        self.tracked_person_id = None
        self.person_history = []

    def record(self, economy):
        people = economy.people
        if not people:
            return
        firms = economy.firms
        data = {
            # economy
            "price": economy.food_price,
            "food": economy.food_supply,
            "wage": mean(f.wage_offer for f in firms) if firms else 0.0,

            # people
            "avg_happiness": mean(p.happiness for p in people),
            "avg_money": mean(p.money for p in people),
            "avg_health": mean(p.health for p in people),
            "avg_hunger": mean(p.hunger for p in people),
            # statistics.mean has no default; handle empty explicitly
            # derive worker wages from firm wage_offer
            "avg_wage": (
                mean([
                    person.productivity * person.firm.wage_offer
                    for person in people
                    if person.employed and person.firm is not None
                ])
                if any(person.employed and person.firm is not None for person in people)
                else 0.0
            ),

            # firms
            "num_firms": len(firms),
            "avg_workers": mean(len(f.workers) for f in firms) if firms else 0.0,
            "avg_cash": mean(f.cash for f in firms) if firms else 0.0,
        }
        self.history.append(data)

        # track single person if set
        if self.tracked_person_id is not None:
            # find person by stable id
            for person in people:
                if person.id == self.tracked_person_id:
                    self.person_history.append({
                        "money": person.money,
                        "health": person.health,
                        "hunger": person.hunger,
                    })
                    break
