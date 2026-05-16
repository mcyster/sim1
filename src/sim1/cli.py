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

    args = parser.parse_args()

    random.seed(args.seed)
    economy = Economy(population_size=args.population)
    metrics = Metrics()
    plotter = LivePlot()
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
