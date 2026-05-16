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
        self.fig, self.axs = plt.subplots(4, 1, figsize=(8, 12))
        # improve spacing to avoid overlap
        try:
            # increase vertical spacing between subplots
            self.fig.tight_layout(pad=2.0)
            self.fig.subplots_adjust(hspace=0.6)
        except Exception:
            pass
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

        ax_econ, ax_people, ax_firms, ax_person = self.axs

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

        # Person (tracked)
        ax_person.clear()
        plotted = False
        if getattr(metrics, "person_history", None):
            hist_p = metrics.person_history[-365:]
            xs_p = list(range(len(hist_p)))
            if hist_p:
                ax_person.plot(xs_p, [m.get("money", 0.0) for m in hist_p], label="money")
                ax_person.plot(xs_p, [m.get("health", 0.0) for m in hist_p], label="health")
                ax_person.plot(xs_p, [m.get("hunger", 0.0) for m in hist_p], label="hunger")
                plotted = True
        # include tracked person id in title if available
        person_id = getattr(metrics, "tracked_person_id", None)
        if person_id is not None:
            ax_person.set_title(f"person {person_id}")
        else:
            ax_person.set_title("person")
        ax_person.set_xlabel("day")
        if plotted:
            ax_person.legend()
        plt.draw()
        plt.pause(0.01)

    def plot_person(self, metrics):
        if not metrics.person_history:
            return
        # ensure interactive mode and separate figure
        plt.ion()
        hist = metrics.person_history[-365:]
        xs = list(range(len(hist)))
        fig = plt.figure("person")
        try:
            fig.canvas.manager.set_window_title("Person")
        except Exception:
            pass
        fig.clf()
        ax = fig.add_subplot(111)
        ax.plot(xs, [m["money"] for m in hist], label="money")
        ax.plot(xs, [m["health"] for m in hist], label="health")
        ax.plot(xs, [m["hunger"] for m in hist], label="hunger")
        ax.set_xlabel("day")
        ax.legend()
        plt.draw()
        plt.pause(0.01)
