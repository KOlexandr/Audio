import matplotlib.pyplot as plot

__author__ = 'Olexandr'


def plot_data(data, title):
        """
        plot list with some data
        @param data: list with data
        @param title: title of figure
        """
        plot.plot(range(len(data)), data)
        plot.grid(True)
        plot.title(title)
        plot.show()