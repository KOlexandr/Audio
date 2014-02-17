import matplotlib.pyplot as plot

__author__ = 'Olexandr'


class Plotter:
    def __init__(self):
        self.data_x, self.data_y, self.title, self.color, self.style = [], [], [], [], []

    def add_sub_plot_data(self, title, data_y, data_x=None, color="blue", line_style="-"):
        self.data_y.append(data_y)
        if data_x is None:
            self.data_x.append(range(len(data_y)))
        else:
            self.data_x.append(data_x)
        self.color.append(color)
        self.style.append(line_style)
        self.title.append(title)

    def add_current_plot_data(self):
        pass

    def sub_plot_all_horizontal(self):
        if len(self.data_x) == 0:
            raise Exception("Data for plot not exists")
        for i in range(len(self.data_y)):
            plot.subplot(len(self.data_y), 1, i+1)
            plot.plot(self.data_x[i], self.data_y[i], color=self.color[i], linestyle=self.style[i])
            plot.title(self.title[i])
            plot.grid(True)
        plot.show()


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