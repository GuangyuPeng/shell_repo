import os
import filecmp
import copy
import itertools
import numpy as np
import matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.markers import MarkerStyle
from matplotlib.markers import CapStyle
from matplotlib.markers import JoinStyle

import utils.stat as mystat


markers = ('o', 'x', '>', '+', '*')
mstyles = []
for marker in markers:
    mstyle = MarkerStyle(
        marker,
        joinstyle=JoinStyle.round,
        capstyle=CapStyle.round,
    )
    # mstyle._joinstyle = 'round'
    # mstyle._capstyle = 'round'
    mstyles.append(mstyle)

colors = (
    '#a00000', '#00a000',
    '#5060d0', '#f25900',
    '#500050', '#ffb700',
    '#000000', '#808080',
)

markerstyles = (
    {
        'marker': mstyles[0],
        'markevery': 1,
        'markersize': 15,
        'markerfacecolor': 'None',
    },
    {
        'marker': mstyles[1],
        'markevery': 1,
        'markerfacecolor': 'None',

    },
    {
        'marker': mstyles[2],
        'markersize': 15,
        'markevery': 1,

    },
    {
        'marker': mstyles[3],
        'markevery': 1,
        'markersize': 20,
        'markerfacecolor': 'None',
    },
    {
        'marker': mstyles[4],
        'markevery': 1,
        'markersize': 20,
    }
)

fillstyles = [
    {
        'linewidth': 2,
        'facecolor': colors[0],
        'edgecolor': colors[0],
    },
    {
        'linewidth': 2,
        # 'facecolor': '#E1B1B1',
        # 'edgecolor': '#E1B1B1',
        'facecolor': '#A0A0A0',
        'edgecolor': '#A0A0A0',
    },
    {
        'edgecolor': colors[1],
        'linewidth': 2,
        'fill': False,
        'hatch': '////',
    },
    {
        'edgecolor': colors[2],
        'fill': False,
        'linewidth': 2,
        'hatch': '//\\\\',
    },
    {
        'edgecolor': colors[3],
        'fill': False,
        'linewidth': 2,
        'hatch': '--',
    },
    {
        'edgecolor': colors[4],
        'fill': False,
        'linewidth': 2,
        'hatch': '/.',
    },
]


# dashstyles = (
#     (2, 0),
#     (2, 2),
#     (0.1, 2),
#     (2, 2, 0.1, 2),
#     (2, 2, 0.1, 1.5, 0.1, 2),
# )

dashstyles = (
    {
        'dashes': (2, 0),
    },
    {
        'dashes': (2, 2),
    },
    {
        'dashes': (0.1, 2),
        'linewidth': 5,
    },
    {
        'dashes': (2, 2, 0.1, 2),
    },
    {
        'dashes': (2, 2, 0.1, 1.5, 0.1, 2),
    },
)

style_fname = 'paper.mplstyle'


def check_style_file():
    ''' Check whether the contents of the matplotlib style file are the same
    as that in this repo.

    Returns:
        True if the contents are identical.
    '''
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    style_dir = os.path.join(
        matplotlib.get_configdir(),
        'stylelib'
    )
    style_file_system = os.path.join(style_dir, style_fname)
    style_file = os.path.join(cur_dir, style_fname)
    if not os.path.exists(style_file_system):
        print('WARN: "%s" not exists.' % style_file_system)
        print('INFO: Try to fix this by linking "%s" to "%s".' % (
            style_file, style_file_system
        ))
        # if not os.path.exists(style_dir):
        #     os.mkdir(style_dir)
        # os.symlink(style_file, style_file_system)
        return False
    if not filecmp.cmp(style_file, style_file_system):
        print(
            'WARN: "%s" has different contents from "%s".' % (
                style_file_system, style_file
            )
        )
        print('INFO: Try to fix this by linking "%s" to "%s".' % (
            style_file, style_file_system
        ))
        return False
    return True


class Plot(object):
    ''' Plot figures with matplotlib

    Attributes:
        fig, ax: Figure and Axes objects of matplotlib
    '''
    def __init__(self, nplots=1):
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        plt.style.use(
            os.path.join(cur_dir, style_fname)
        )
        self.fig, axes = plt.subplots(nrows=nplots, ncols=1, sharex=True)
        if nplots == 1:
            self.axes = (axes, )
        else:
            self.axes = axes
        self.ax = self.axes[0]
        self.set_ax_style()

    def set_ax_style(self):
        for ax in self.axes:
            ax.minorticks_on()
            ax.grid(
                visible=True, axis='both', which='major',
                ls=(0, (0.5, 1.5)), linewidth=2, alpha=0.9,
            )
            ax.grid(
                visible=True, axis='both', which='minor',
                linestyle=(0, (0.5, 1.5)), linewidth=1.5, alpha=0.3,
            )
            for axis in (ax.xaxis, ax.yaxis):
                lines = itertools.chain(
                    axis.get_majorticklines(),
                    axis.get_minorticklines(),
                )
                # for line in lines:
                #     line._marker._capstyle = 'round'
                #     line._marker._joinstyle = 'round'

    def get_plot_args(self, axid=0):
        return {'zorder': 100}

    def set_matplotlibrc(self, param, value):
        mpl.rcParams[param] = value


class LinePlot(Plot):
    ''' Plot lines

    Attributes:
        n_lines: # of plotted lines
        colors: A list of line colors
    '''
    def __init__(self, nplots=1):
        super().__init__(nplots)
        self.n_lines = [0] * len(self.axes)
        self.colors = copy.deepcopy(colors)

    def get_plot_args(self, axid=0):
        ''' Get plotting arguments
        '''
        plot_args = super().get_plot_args(axid)
        if self.n_lines[axid] < len(self.colors):
            plot_args['color'] = self.colors[self.n_lines[axid]]
        return plot_args

    def plot(self, x, y, axid=0, **kwargs):
        ''' Plot data

        Args:
            x, y: A list of values for plotting
        '''
        plot_args = self.get_plot_args(axid)
        plot_args.update(kwargs)
        lines = self.axes[axid].plot(x, y, **plot_args)
        self.n_lines[axid] += 1
        if 'label' in plot_args:
            self.axes[axid].legend(loc='best')
        return lines

    def set_colors(self, colors):
        self.colors = copy.deepcopy(colors)


class LinePointPlot(LinePlot):
    ''' Plot data with line points

    Attributes:
        markerstyles:
            A list of marker styles.
            Each item is a dictionary representing the marker-style-related
            arguments passed to the plot function.
    '''
    def __init__(self, nplots=1):
        super().__init__(nplots)
        self.markerstyles = copy.deepcopy(markerstyles)

    def get_plot_args(self, axid=0):
        ''' Get plotting arguments
        '''
        plot_args = super().get_plot_args(axid)
        if self.n_lines[axid] < len(self.markerstyles):
            plot_args.update(self.markerstyles[self.n_lines[axid]])
        return plot_args

    def set_markerstyles(self, markerstyles):
        self.markerstyles = copy.deepcopy(markerstyles)


class LineDashPlot(LinePlot):
    ''' Plot data with dotted lines

    Attributes:
        dashstyles: A list of dash patterns.
    '''
    def __init__(self, nplots=1):
        super().__init__(nplots)
        self.dashstyles = copy.deepcopy(dashstyles)

    def get_plot_args(self, axid=0):
        ''' Get plotting arguments
        '''
        plot_args = super().get_plot_args(axid)
        if self.n_lines[axid] < len(self.dashstyles):
            plot_args.update(self.dashstyles[self.n_lines[axid]])
        return plot_args

    def set_dashstyles(self, dashstyles):
        self.dashstyles = copy.deepcopy(dashstyles)


class CDFPlot(LineDashPlot):
    ''' Plotting CDF
    '''
    def __init__(self):
        super().__init__()

    def set_ax_style(self, axid=0):
        super().set_ax_style()
        self.axes[axid].set_ylim([0, 1])
        self.axes[axid].set_ylabel('CDF')

    def get_plot_args(self, axid=0):
        ''' Get plotting arguments
        '''
        plot_args = super().get_plot_args(axid)
        plot_args['where'] = 'post'
        if self.n_lines[axid] < len(self.dashstyles):
            plot_args.update(self.dashstyles[self.n_lines[axid]])
        return plot_args

    def plot(self, data, cdf=None, axid=0, **kwargs):
        ''' Plot CDF (Cumulative Distribution Function)

        Args:
            data: A list of data for plotting CDF
            kwargs: Other arguments for matplotlib.axes.Axes.step
        '''
        if cdf is None:
            x_values, cdf = mystat.get_cdf(data)
        else:
            x_values = data
        plot_args = self.get_plot_args(axid)
        plot_args.update(kwargs)
        lines = self.axes[axid].step(x_values, cdf, **plot_args)
        self.n_lines[axid] += 1
        if 'label' in plot_args:
            self.axes[axid].legend(loc='best')
        return lines


class PiePlot(Plot):
    def __init__(self):
        super().__init__()

    def plot(self, data, labels, axid=0, **kwargs):
        ''' Plot pie chart

        Args:
            data: an array of wedge sizes
            label: a list containing labels of all wedges
        '''
        plot_args = {}
        if len(colors) < len(data) and 'colors' not in kwargs:
            print(
                'Need to provide the color argument.'
                'Build-in color types are too few.',
            )
            return
        plot_args['colors'] = colors[:len(data)]
        plot_args.update(kwargs)
        ret = self.axes[axid].pie(data, labels=labels, **plot_args)
        return ret


class StackPlot(Plot):
    def __init__(self):
        super().__init__()

    def plot(self, x, *ys, labels=(), axid=0, **kwargs):
        plot_args = {}
        if len(colors) < len(ys) and 'colors' not in kwargs:
            print(
                '[Warning] It\'s better to provide the color argument.'
                'Build-in color types are too few.',
            )
        plot_args['colors'] = colors[:len(ys)]
        plot_args['alpha'] = 0.8
        plot_args.update(kwargs)
        stacks = self.axes[axid].stackplot(
            x, *ys,
            labels=labels,
            **plot_args,
        )
        yval = (0, ) * len(ys[0])
        for y, color in zip(ys, plot_args['colors']):
            yval = np.sum((yval, y), axis=0)
            self.axes[axid].plot(x, yval, color=color)
        return stacks


class StackBarPlot(Plot):
    ''' Plot stacked bars

    Attributes:
        n_groups: # of bars
        n_bars: # of bars (# of xvals)
        yvals: A list of y values
    '''
    def __init__(self):
        super().__init__()
        self.n_groups = 0
        self.n_bars = -1
        self.yvals = []
        self.plot_args = []
        self.bar_width = 1

    def get_plot_args(self):
        ''' Get plotting arguments
        '''
        plot_args = super().get_plot_args(0)
        plot_args.update(fillstyles[self.n_groups])
        plot_args['capstyle'] = 'round'
        plot_args['joinstyle'] = 'round'
        return plot_args

    def insert_yvals(self, yvals, **plot_kwargs):
        ''' Insert y values (bar heights)
        This does not actually plot.

        Args:
            yvals: A list of y values
            plot_kwargs: args for plotting
        '''
        self.yvals.append(yvals)
        plot_args = self.get_plot_args()
        plot_args.update(plot_kwargs)
        self.plot_args.append(plot_args)
        self.n_groups += 1
        if self.n_bars < 0:
            self.n_bars = len(yvals)
        if self.n_bars != len(yvals):
            print('ERROR: Number of y values does not consistent.')

    def plot(self, xlabels=None, **kwargs):
        ''' Plotting data

        Args:
            xlabels: A list of labels to show on x axis
            kwargs: global plotting args
        '''
        barcontainers = []
        xval = np.arange(self.n_bars)
        prev_yval = (0,) * self.n_bars
        for idx in range(0, self.n_groups):
            yval = self.yvals[idx]
            plot_args = {
                'bottom': prev_yval,
                'width': 0.8*self.bar_width,
            }
            plot_args.update(self.plot_args[idx])
            plot_args.update(kwargs)
            container = self.ax.bar(xval, yval, **plot_args)
            barcontainers.append(container)
            prev_yval = yval
            if 'label' in plot_args:
                self.ax.legend(loc='best')
        if xlabels is not None:
            self.set_xticklabels(xlabels)
        return barcontainers

    def set_xticklabels(self, labels, **kwargs):
        ''' Plotting data

        Args:
            labels: A list of labels to show on x axis
            kwargs: other arguments
        '''
        xval = np.arange(len(labels))
        locs = xval
        self.ax.set_xticks(locs, labels, **kwargs)



class BarPlot(Plot):
    ''' Plot bars

    Attributes:
        n_groups: # of groups
        yvals: A list of y values
        n_bars: # of bars per group (# of xvals)
    '''
    def __init__(self):
        super().__init__(1)
        self.n_groups = 0
        self.yvals = []
        self.plot_args = []
        self.n_bars = -1
        self.total_bar_width = 0.8

    def get_plot_args(self):
        ''' Get plotting arguments
        '''
        plot_args = super().get_plot_args(0)
        plot_args.update(fillstyles[self.n_groups])
        plot_args['capstyle'] = 'round'
        plot_args['joinstyle'] = 'round'
        return plot_args

    def insert_yvals(self, yvals, **plot_kwargs):
        ''' Insert y values (bar heights)
        This does not actually plot.
        As plotting needs to know the number of groups

        Args:
            yvals: A list of y values
            plot_kwargs: args for plotting
        '''
        self.yvals.append(yvals)
        plot_args = self.get_plot_args()
        plot_args.update(plot_kwargs)
        self.plot_args.append(plot_args)
        self.n_groups += 1
        if self.n_bars < 0:
            self.n_bars = len(yvals)
        if self.n_bars != len(yvals):
            print('ERROR: Number of y values does not consistent.')

    def plot(self, xlabels=None, **kwargs):
        ''' Plotting data

        Args:
            xlabels: A list of labels to show on x axis
            kwargs: global plotting args
        '''
        barcontainers = []
        self.bar_width = self.total_bar_width / self.n_groups
        xval = np.arange(self.n_bars)
        for idx in range(0, self.n_groups):
            yval = self.yvals[idx]
            plot_args = self.plot_args[idx]
            plot_args.update(kwargs)
            container = self.ax.bar(
                xval+idx*self.bar_width, yval,
                width=0.8*self.bar_width,
                **plot_args,
            )
            barcontainers.append(container)
            if 'label' in plot_args:
                self.ax.legend(loc='best')
        if xlabels is not None:
            self.set_xticklabels(xlabels)
        return barcontainers

    def set_xticklabels(self, labels, **kwargs):
        ''' Plotting data

        Args:
            labels: A list of labels to show on x axis
            kwargs: other arguments
        '''
        xval = np.arange(len(labels))
        locs = xval + (self.n_groups - 1) * self.bar_width / 2
        self.ax.set_xticks(locs, labels, **kwargs)


def main():
    lp = LineDashPlot()
    x = np.linspace(0, 20, 100)
    y = np.sin(x)
    z = np.cos(x)
    lp.plot(x, y)
    lp.plot(x, z)
    plt.show()


if __name__ == '__main__':
    main()
