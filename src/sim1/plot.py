import matplotlib
# Try a GUI backend for realtime plots
try:
    matplotlib.use("TkAgg")
except Exception:
    pass
import matplotlib.pyplot as plt


class LivePlot:
    def __init__(self):
        plt.ion()
        self.fig, self.axs = plt.subplots(3, 1, figsize=(8, 10))
        try:
            self.fig.canvas.manager.set_window_title("Economy")
        except Exception:
            pass

    def update(self, metrics):
        if not metrics.history:
            return

        window = 365
        hist = metrics.history[-window:]
        xs = list(range(len(hist)))

        def get(key):
            return [m.get(key, 0.0) for m in hist]

        ax_econ, ax_people, ax_firms = self.axs

        # Economy
        ax_econ.clear()
        ax_econ.plot(xs, get("food"), label="food")
        ax_econ.plot(xs, get("price"), label="price")
        if "wage" in hist[0]:
            ax_econ.plot(xs, get("wage"), label="wage")
        ax_econ.set_title("economy")
        ax_econ.legend()

        # People
        ax_people.clear()
        for key in ["avg_happiness", "avg_money", "avg_health", "avg_hunger", "avg_wage"]:
            if key in hist[0]:
                ax_people.plot(xs, get(key), label=key)
        ax_people.set_title("people")
        ax_people.legend()

        # Firms
        ax_firms.clear()
        for key in ["num_firms", "avg_workers", "avg_cash", "wage"]:
            if key in hist[0]:
                ax_firms.plot(xs, get(key), label=key)
        ax_firms.set_title("firms")
        ax_firms.set_xlabel("day")
        ax_firms.legend()
        plt.draw()
        plt.pause(0.01)
