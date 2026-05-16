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


class OpenAIBrain(DefaultBrain):
    """Experimental brain that queries OpenAI for decisions.
    Falls back to DefaultBrain on any failure.
    """

    def _call(self, prompt: str) -> str:
        try:
            from openai import OpenAI
            client = OpenAI()
            resp = client.chat.completions.create(
                model="gpt-5.3-chat-latest",
                messages=[{"role": "user", "content": prompt}],
            )
            return (resp.choices[0].message.content or "").strip().upper()
        except Exception as error:
            # return error text so it shows up in logs for debugging
            return f"ERROR: {error}"

    def __init__(self):
        super().__init__()
        # simple caching to reduce API calls
        self._last_role_day = -10
        self._cached_role = None
        self._last_employment_day = -5
        self._cached_employment = None
        # cooldowns (days)
        self.role_cooldown = 10
        self.employment_cooldown = 5

    def _log(self, person, economy, message: str):
        try:
            from datetime import datetime
            from pathlib import Path
            out_dir = Path("output")
            out_dir.mkdir(parents=True, exist_ok=True)
            fname = out_dir / f"person_{person.id}.log"
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(fname, "a") as f:
                f.write(f"---- day={economy.day} {ts}\n{message}\n\n")
        except Exception:
            pass

    def choose_role(self, person, economy, avg_wage: float):
        # cache: reuse recent decision
        if (
            self._cached_role is not None
            and economy.day - self._last_role_day < self.role_cooldown
        ):
            return self._cached_role
        # build simple deltas from recent metrics if available
        hist = getattr(economy, "_metrics_history", [])
        def delta(key, n):
            if len(hist) > n:
                return hist[-1].get(key, 0.0) - hist[-1-n].get(key, 0.0)
            return 0.0

        num_firms = len(economy.firms)
        prompt = (
            "Goal: stay healthy, happy, and wealthy. Avoid running out of money.\n"
            "You can be WORKER (earn wages) or OWNER (run a firm, hire workers, earn profit).\n"
            "Starting a firm requires money and risk; hiring workers costs wages but can increase output.\n"
            f"State: money={person.money:.2f} food={person.food:.2f} hunger={person.hunger:.2f} prod={person.productivity:.2f}.\n"
            f"Economy: price={economy.food_price:.3f} avg_wage={avg_wage:.3f} firms={num_firms}.\n"
            f"Trends: d_price_1={delta('price',1):.3f} d_price_3={delta('price',3):.3f} d_price_5={delta('price',5):.3f} d_price_10={delta('price',10):.3f}.\n"
            "Decide role: WORKER or OWNER. Answer one word."
        )
        ans = self._call(prompt)
        decision = None
        if "OWNER" in ans:
            decision = Role.OWNER
        elif "WORKER" in ans:
            decision = Role.WORKER
        else:
            decision = super().choose_role(person, economy, avg_wage)
        self._log(
            person,
            economy,
            (
                f"person id={person.id} money={person.money:.2f} food={person.food:.2f} hunger={person.hunger:.2f}\n"
                f"REQUEST:\n{prompt}\n"
                f"RESPONSE:\n{ans}\n"
                f"ACTION: role -> {decision}"
            ),
        )
        # cache decision
        self._cached_role = decision
        self._last_role_day = economy.day
        return decision

    def choose_employment(self, person, economy):
        if not economy.firms:
            return None
        # cache: reuse recent decision
        if (
            self._cached_employment is not None
            and economy.day - self._last_employment_day < self.employment_cooldown
        ):
            return self._cached_employment
        best_firm = max(economy.firms, key=lambda firm: firm.wage_offer)
        hist = getattr(economy, "_metrics_history", [])
        def delta(key, n):
            if len(hist) > n:
                return hist[-1].get(key, 0.0) - hist[-1-n].get(key, 0.0)
            return 0.0

        prompt = (
            "Goal: stay healthy, happy, and solvent (money > 0).\n"
            "Working earns wages; not working risks running out of money and food.\n"
            f"State: money={person.money:.2f} food={person.food:.2f} hunger={person.hunger:.2f}.\n"
            f"Offer: wage={best_firm.wage_offer:.3f}, price={economy.food_price:.3f}, firms={len(economy.firms)}.\n"
            f"Trends: d_price_1={delta('price',1):.3f} d_price_3={delta('price',3):.3f} d_price_5={delta('price',5):.3f} d_price_10={delta('price',10):.3f}.\n"
            "Take job? YES or NO. Answer one word."
        )
        ans = self._call(prompt)
        chosen = None
        if "YES" in ans:
            chosen = best_firm
        elif "NO" in ans:
            chosen = None
        else:
            chosen = super().choose_employment(person, economy)
        firm_id = getattr(chosen.owner, "id", None) if chosen else None
        self._log(
            person,
            economy,
            (
                f"person id={person.id} money={person.money:.2f} food={person.food:.2f} hunger={person.hunger:.2f}\n"
                f"REQUEST:\n{prompt}\n"
                f"RESPONSE:\n{ans}\n"
                f"ACTION: employment -> {'YES' if chosen else 'NO'} firm_owner_id={firm_id}"
            ),
        )
        # cache decision
        self._cached_employment = chosen
        self._last_employment_day = economy.day
        return chosen
