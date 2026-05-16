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
        self.fig, self.ax = plt.subplots()
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
            return [m[key] for m in hist]

        self.ax.clear()
        self.ax.plot(xs, get("price"), label="price")
        self.ax.plot(xs, get("food"), label="food")
        self.ax.plot(xs, get("avg_money"), label="money")
        self.ax.plot(xs, get("avg_hunger"), label="hunger")
        self.ax.set_xlabel("day")
        self.ax.legend()
        plt.draw()
        plt.pause(0.01)
