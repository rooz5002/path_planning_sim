import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def plot_graph(style, densities, a_star_times, q_learning_times, master=None):
    """
    Generate and display a graph in a pop-up window.

    Parameters:
    - style: The style of the graph ("line", "scatter", "bar").
    - densities: List of density percentages.
    - a_star_times: List of times for A* algorithm.
    - q_learning_times: List of times for Q-Learning.
    - master: The Tkinter master window for the pop-up.
    """
    # Create the plot
    fig, ax = plt.subplots(figsize=(8, 5))

    if style == "line":
        ax.plot(densities, a_star_times, label="A* Time", marker="o")
        ax.plot(densities, q_learning_times, label="Q-Learning Time", marker="o")
    elif style == "scatter":
        ax.scatter(densities, a_star_times, label="A* Time")
        ax.scatter(densities, q_learning_times, label="Q-Learning Time")
    elif style == "bar":
        width = 2
        ax.bar([x - width for x in densities], a_star_times, width=width, label="A* Time")
        ax.bar([x + width for x in densities], q_learning_times, width=width, label="Q-Learning Time")

    # Configure the plot
    ax.set_xlabel("Obstacle Density (%)")
    ax.set_ylabel("Execution Time (s)")
    ax.set_title("Pathfinding Efficiency vs. Occupancy Density")
    ax.legend()
    ax.grid(True)

    # Display the plot in a Tkinter pop-up window
    if master:
        popup = create_popup(master, fig)
    else:
        plt.show()


def create_popup(master, fig):
    """Create a pop-up window to display the graph."""
    popup = tk.Toplevel(master)
    popup.title("Graph Viewer")
    popup.geometry("900x600")

    canvas = FigureCanvasTkAgg(fig, master=popup)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Close Button
    close_button = tk.Button(popup, text="Close", command=popup.destroy)
    close_button.pack(pady=10)

    return popup
