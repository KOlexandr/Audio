import matplotlib.pyplot as plot

__author__ = 'Olexandr'


class Plotter:
    def __init__(self):
        self.data, self.additional_data = {}, {}
        self.sub_plot_num = 1

    def add_sub_plot_data(self, title, data_y, data_x=None, color="blue", ls="-", scale_x=None, scale_y=None):
        """
        adds new data for plot in new sub plot frame
        @param title: title of subplot
        @param data_y: list with y coordinates
        @param data_x: list with x coordinates
        @param color: color of graph
        @param ls: style of line for this graph
        """
        if data_x is None:
            data_x = range(len(data_y))
        if self.additional_data.get(title) is None:
            self.additional_data[title] = []
        self.data[title] = (data_x, data_y, color, ls, self.sub_plot_num, scale_x, scale_y)
        self.sub_plot_num += 1

    def add_current_plot_data(self, title, data_y, data_x=None, color="green", ls="o", lw=1):
        """
        adds new 2D graph to current subplot
        @param title: title of subplot which should contains this graph
        @param data_y: list with y coordinates
        @param data_x: list with x coordinates
        @param color: color of graph
        @param ls: style of line for this graph
        @param lw: weight of line
        """
        if data_x is None:
            data_x = range(len(data_y))
        self.additional_data[title].append(("xy", data_x, data_y, color, ls, lw))

    def add_line_at(self, title, x, axis, color="green", ls="-", lw=1):
        """
        adds one or few vertical or horizontal lines to current subplot
        @param title: title of subplot which should contains this graph
        @param x: main coordinates of lines
        @param axis: name of axis ["x"|"y"]
        @param color: color of graph
        @param ls: style of line for this graph
        @param lw: weight of line
        """
        self.additional_data[title].append((axis, x, color, ls, lw))

    def sub_plot_all_horizontal(self):
        """
        plots all subplots and their additional data in one window
        """
        data_len = len(self.data)
        if data_len == 0:
            raise Exception("Data for plot not exists")
        for i in self.data.keys():
            plot.subplot(data_len, 1, self.data[i][4])
            if not (self.data[i][5] is None):
                plot.xscale(self.data[i][5])
            if not (self.data[i][6] is None):
                plot.yscale(self.data[i][6])
            plot.plot(self.data[i][0], self.data[i][1], color=self.data[i][2], linestyle=self.data[i][3])
            if not self.additional_data.get(i) is None:
                y_min, y_max = min(self.data[i][1]), max(self.data[i][1])
                x_min, x_max = min(self.data[i][0]), max(self.data[i][0])
                for j in self.additional_data.get(i):
                    if j[0] == "xy":
                        plot.plot(j[1], j[2], color=j[3], linestyles=j[4], lw=j[5])
                    elif j[0] == "x":
                        plot.vlines(j[1], y_min, y_max, color=j[2], linestyles=j[3], lw=j[4])
                    elif j[0] == "y":
                        plot.hlines(j[1], x_min, x_max, color=j[2], linestyles=j[3], lw=j[4])
                plot.xlim((x_min, x_max))
            plot.title(i)
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