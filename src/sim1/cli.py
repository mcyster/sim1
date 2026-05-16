import random
import argparse
from .economy import Economy
from .simulation import tick
from .metrics import Metrics
from .plot import LivePlot
import sys
import select
from datetime import datetime
from pathlib import Path
from .enums import Command


def summary(economy: Economy, step: int):
    working = sum(1 for p in economy.people if (p.employed or p.role == "owner"))
    avg_money = sum(p.money for p in economy.people) / len(economy.people)
    avg_health = sum(p.health for p in economy.people) / len(economy.people)
    avg_happiness = sum(p.happiness for p in economy.people) / len(economy.people)
    if economy.firms:
        avg_wage = sum(f.wage_offer for f in economy.firms) / len(economy.firms)
    else:
        avg_wage = 0.0
    line = (
        f"day={step} working={working} avg_money={avg_money:.2f} total_food={economy.total_food:.2f} "
        f"avg_health={avg_health:.2f} avg_happiness={avg_happiness:.2f} price={economy.food_price:.3f} avg_wage={avg_wage:.3f}"
    )
    return line


def main():
    parser = argparse.ArgumentParser(description="Sim1 economy simulation")
    parser.add_argument("--population", type=int, default=1000, help="number of people")
    parser.add_argument("--ticks", type=int, default=10, help="number of ticks (days)")
    parser.add_argument("--seed", type=int, default=42, help="random seed")
    parser.add_argument("--summary-every", type=int, default=1, help="print summary every N ticks")
    parser.add_argument("--once", action="store_true", help="run fixed number of ticks")
    parser.add_argument("--ai-brain", action="store_true", help="add one AI-controlled person")

    args = parser.parse_args()

    random.seed(args.seed)
    economy = Economy(population_size=args.population)
    metrics = Metrics()
    plotter = LivePlot()
    # optionally replace one person's brain with OpenAI brain
    if args.ai_brain and economy.people:
        from .brain import OpenAIBrain
        economy.people[0].brain = OpenAIBrain()
        log_path = Path("output") / f"person_{economy.people[0].id}.log"
        print(f"AI brain enabled for person id={economy.people[0].id}")
        print(f"Logging person to {log_path}")
    # create timestamped log file
    ts = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    out_dir = Path("output")
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / f"sim1-{ts}.log"
    logf = open(log_path, "w", buffering=1)
    print(f"Logging to {log_path}")
    print("Help for help")
    print("> ", end="", flush=True)
    state = {"running": True}

    def handle_commands():
        # non-blocking stdin check
        if select.select([sys.stdin], [], [], 0.0)[0]:
            raw = sys.stdin.readline()
            cmd = (raw or "").strip().lower()
            if cmd == "":
                print("> ", end="", flush=True)
                return None
            if cmd in (Command.Q, Command.QUIT):
                return "quit"
            elif cmd == Command.STOP:
                state["running"] = False
                print("stopped")
                print("> ", end="", flush=True)
            elif cmd == Command.START:
                state["running"] = True
                print("running")
                print("> ", end="", flush=True)
            elif cmd in (Command.H, Command.HELP):
                print("commands:")
                print("  h/help  - show this help message")
                print("  q/quit  - exit the simulation")
                print("  stop    - pause the simulation (time stops)")
                print("  start   - resume the simulation")
                print("  firms   - show firm stats")
                print("  people  - show people stats")
                print("  economy - show economy stats")
                print("  wealthiest - top 10 by money")
                print("  poorest    - bottom 10 by money")
                print("  person <id> - show person stats (index)")
                print("> ", end="", flush=True)
            elif cmd == Command.FIRMS:
                firms = economy.firms
                count = len(firms)
                if count == 0:
                    print("firms=0")
                else:
                    avg_workers = sum(len(f.workers) for f in firms) / count
                    avg_cash = sum(f.cash for f in firms) / count
                    avg_wage = sum(f.wage_offer for f in firms) / count
                    producing = sum(1 for f in firms if getattr(f, "produced", False))
                    not_producing = count - producing
                    print(
                        f"firms={count} producing={producing} idle={not_producing} "
                        f"avg_workers={avg_workers:.2f} avg_cash={avg_cash:.2f} avg_wage={avg_wage:.3f}"
                    )
                print("> ", end="", flush=True)
            elif cmd == Command.PEOPLE:
                people = economy.people
                count = len(people)
                if count == 0:
                    print("people=0")
                else:
                    employed = sum(1 for person in people if person.employed)
                    avg_money = sum(person.money for person in people) / count
                    avg_health = sum(person.health for person in people) / count
                    avg_hunger = sum(person.hunger for person in people) / count
                    avg_happiness = sum(person.happiness for person in people) / count
                    wages = [
                        person.productivity * person.firm.wage_offer
                        for person in people
                        if person.employed and person.firm is not None
                    ]
                    avg_wage = (sum(wages) / len(wages)) if wages else 0.0
                    print(
                        f"people={count} employed={employed} avg_money={avg_money:.2f} "
                        f"avg_health={avg_health:.2f} avg_hunger={avg_hunger:.2f} "
                        f"avg_happiness={avg_happiness:.2f} avg_wage={avg_wage:.3f}"
                    )
                print("> ", end="", flush=True)
            elif cmd == Command.ECONOMY:
                price = economy.food_price
                supply = economy.food_supply
                total_food = economy.total_food
                transactions = getattr(economy, "transactions", 0)
                quantity_sold = getattr(economy, "quantity_sold", 0.0)
                # include food held by people
                total_food_people = sum(person.food for person in economy.people)
                avg_food = (total_food_people / len(economy.people)) if economy.people else 0.0
                print(
                    f"price={price:.3f} supply={supply:.2f} produced={total_food:.2f} "
                    f"food_people={total_food_people:.2f} avg_food={avg_food:.2f} "
                    f"transactions={transactions} quantity_sold={quantity_sold:.2f}"
                )
                print("> ", end="", flush=True)
            elif cmd == Command.WEALTHIEST:
                people = economy.people
                top = sorted(people, key=lambda person: person.money, reverse=True)[:10]
                print(f"{'id':>5} {'money':>8} {'health':>6} {'hunger':>6} {'emp':>5} role")
                for person in top:
                    print(f"{person.id:5d} {person.money:8.2f} {person.health:6.2f} {person.hunger:6.2f} {str(person.employed):>5s} {person.role}")
                print("> ", end="", flush=True)
            elif cmd == Command.POOREST:
                people = economy.people
                bottom = sorted(people, key=lambda person: person.money)[:10]
                print(f"{'id':>5} {'money':>8} {'health':>6} {'hunger':>6} {'emp':>5} role")
                for person in bottom:
                    print(f"{person.id:5d} {person.money:8.2f} {person.health:6.2f} {person.hunger:6.2f} {str(person.employed):>5s} {person.role}")
                print("> ", end="", flush=True)
            elif cmd.startswith(Command.PERSON.value):
                parts = cmd.split(maxsplit=1)
                if len(parts) != 2 or not parts[1].isdigit():
                    print("usage: person <id>")
                    print("> ", end="", flush=True)
                else:
                    target_id = int(parts[1])
                    people = economy.people
                    person = next((p for p in people if p.id == target_id), None)
                    if person is None:
                        print("invalid id")
                    else:
                        # switch tracked person and reset history
                        metrics.tracked_person_id = target_id
                        metrics.person_history = []
                        brain_name = person.brain.__class__.__name__
                        print(
                            f"id={person.id} brain={brain_name} money={person.money:.2f} food={person.food:.2f} "
                            f"health={person.health:.2f} happiness={person.happiness:.2f} "
                            f"hunger={person.hunger:.2f} employed={person.employed} role={person.role}"
                        )
                    print("> ", end="", flush=True)
            else:
                print("> ", end="", flush=True)
        return None

    step = 0
    if args.once:
        for step in range(args.ticks):
            if state["running"]:
                tick(economy)
                if step % args.summary_every == 0:
                    line = summary(economy, step)
                    logf.write(line + "\n")
                metrics.record(economy)
                plotter.update(metrics)
                plotter.plot_person(metrics)
                step += 1
            if handle_commands() == "quit":
                break
    else:
        while True:
            if state["running"]:
                tick(economy)
                if step % args.summary_every == 0:
                    line = summary(economy, step)
                    logf.write(line + "\n")
                metrics.record(economy)
                plotter.update(metrics)
                step += 1
            if handle_commands() == "quit":
                break

    logf.close()


if __name__ == "__main__":
    main()
