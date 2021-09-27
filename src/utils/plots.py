import matplotlib.pyplot as plt


def create_plot_with_subplots(rows, columns, *, xlabel, ylabel, sharex=True, sharey=True):
    """
    Create a plot with rows x columns subplots and labels on the outer axes

    Parameters:
        rows (int): Number of rows
        columns (int): Number of columns
        xlabel (str): Label for the x-axis
        ylabel (str): Label for the y-axis

    Returns:
        figure: Created figure
        axes: Created axes
    """
    # Create a figure with subplots and set the correct spacing
    width = 6.5 * columns ** (1/3)
    height = 5 * rows ** (1/3)
    figure, axes = plt.subplots(nrows=rows, ncols=columns, sharex=sharex, sharey=sharey, figsize=(width, height))
    figure.subplots_adjust(wspace=0.05, hspace=0.15 * rows)
        
    # Set the labels on the outer x and y axis
    if(rows > 1 and columns > 1):
        for vertical_axe in axes:
            vertical_axe[0].set(ylabel=ylabel)
        for horizontal_axe in axes[len(axes) - 1]:
            horizontal_axe.set(xlabel=xlabel)
    elif rows > 1:
        for vertical_axe in axes:
            vertical_axe.set(ylabel=ylabel)
        axes[len(axes) - 1].set(xlabel=xlabel)
    elif columns > 1:
        for horizontal_axe in axes:
            horizontal_axe.set(xlabel=xlabel)
        axes[0].set(ylabel=ylabel)

    # Return the created figure
    return figure, axes


def savefig(filepath):
    """
    Print the values of an object nicely on a single line

    Parameters:
        filepath (str): Path where the figure should be saved
    """
    plt.savefig(filepath, dpi=250, bbox_inches='tight', pad_inches=0.2)

