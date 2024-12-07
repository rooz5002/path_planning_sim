"""
        Create a menu bar for the main application.
        :param master: The root window or parent widget.
        :param app: The main application object for callback integration.
        
        Author: Dr. Amir Ali Mokhtarzadeh
        2022- 2024
        No any part of this program can be changed, used, distribute, or copied
        without author's consent.
        
"""




import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter as tk
from graph_styles import plot_graph


class MenuBar:
    def __init__(self, master, app):

        self.master = master
        self.app = app  # Reference to the main app

        self.menu = tk.Menu(master)
        master.config(menu=self.menu)

        # File Menu
        file_menu = tk.Menu(self.menu, tearoff=0)
        file_menu.add_command(label="Open Saved Environment", command=self.open_environment)
        file_menu.add_command(label="Save Environment", command=self.save_environment)
        file_menu.add_command(label="Settings", command=self.open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=master.quit)
        self.menu.add_cascade(label="File", menu=file_menu)

        # Edit Menu
        edit_menu = tk.Menu(self.menu, tearoff=0)
        edit_menu.add_command(label="Set Grid Size", command=self.set_grid_size)
        edit_menu.add_command(label="Set Delay", command=self.set_delay)
        edit_menu.add_command(label="Clear Path", command=app.clear_path_only)
        edit_menu.add_command(label="Transparent Environment", command=self.transparent_environment)
        self.menu.add_cascade(label="Edit", menu=edit_menu)

        # Path Planning Menu
        path_menu = tk.Menu(self.menu, tearoff=0)
        path_menu.add_command(label="Show Neighbouring", command=self.show_neighbouring)
        path_menu.add_command(label="Show Calculations", command=self.show_calculations)
        self.menu.add_cascade(label="Path Planning", menu=path_menu)
        
        # Graphs Menu
        graphs_menu = tk.Menu(self.menu, tearoff=0)
        graphs_menu.add_command(label="Graph Settings", command=self.open_graph_settings)
        graphs_menu.add_command(label="Display Graph", command=self.display_graph)
        self.menu.add_cascade(label="Graphs", menu=graphs_menu)

        # Help Menu
        help_menu = tk.Menu(self.menu, tearoff=0)
        help_menu.add_command(label="Instructions", command=self.show_instructions)
        help_menu.add_command(label="About Dynamic Path Planning", command=self.show_about)
        help_menu.add_command(label="About A*", command=self.show_about_astar)
        self.menu.add_cascade(label="Help", menu=help_menu)


    def open_environment(self):
        file_path = filedialog.askopenfilename(
            title="Open Environment",
            filetypes=(("Environment Files", "*.env"), ("All Files", "*.*"))
        )
        self.app.case = False
        if file_path:
            try:
                with open(file_path, "r") as file:
                    lines = file.readlines()
                    loaded_grid = [[int(cell) for cell in line.strip().split()] for line in lines]

                # Dynamically resize the grid and canvas to match the loaded environment
                loaded_grid_size = len(loaded_grid)
                if loaded_grid_size != self.app.grid_size:
                    self.app.grid_size = loaded_grid_size
                    self.app.grid_size_entry.delete(0, tk.END)
                    self.app.grid_size_entry.insert(0, str(self.app.grid_size))
                    self.app.canvas.config(
                        width=self.app.cell_size * self.app.grid_size,
                        height=self.app.cell_size * self.app.grid_size,
                    )

                # Update the grid and redraw it
                self.app.grid = loaded_grid
                self.app.draw_grid()

                # Populate obstacles and goal cell from the loaded grid
                self.app.goal_cell = None
                for i in range(self.app.grid_size):
                    for j in range(self.app.grid_size):
                        if self.app.grid[i][j] == 1:  # Obstacle
                            self.app.canvas.itemconfig(f"cell_{i}_{j}", fill="black")
                        elif self.app.grid[i][j] == 2:  # Goal cell
                            self.app.goal_cell = (i, j)
                            self.app.canvas.itemconfig(f"cell_{i}_{j}", fill="green")

                messagebox.showinfo("Open Environment", f"Environment loaded successfully from {file_path}.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load environment: {e}")

    '''
    # File Menu Callbacks
    def open_environment(self):
        file_path = filedialog.askopenfilename(
            title="Open Environment",
            filetypes=(("Environment Files", "*.env"), ("All Files", "*.*"))
        )
        if file_path:
            try:
                with open(file_path, "r") as file:
                    lines = file.readlines()
                    self.app.grid = [[int(cell) for cell in line.strip().split()] for line in lines]
                self.app.draw_grid()
                for i in range(self.app.grid_size):
                    for j in range(self.app.grid_size):
                        if self.app.grid[i][j] == 1:  # Obstacle
                            self.app.canvas.itemconfig(f"cell_{i}_{j}", fill="black")
                        elif (i, j) == self.app.goal_cell:
                            self.app.canvas.itemconfig(f"cell_{i}_{j}", fill="green")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load environment: {e}")
    '''
    def save_environment(self):
        file_path = filedialog.asksaveasfilename(
            title="Save Environment",
            defaultextension=".env",
            filetypes=(("Environment Files", "*.env"), ("All Files", "*.*"))
        )
        if file_path:
            try:
                with open(file_path, "w") as file:
                    for row in self.app.grid:
                        file.write(" ".join(map(str, row)) + "\n")
                messagebox.showinfo("Save Environment", f"Environment saved to {file_path}.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save environment: {e}")

    def open_settings(self):
        # Placeholder for settings dialog
        messagebox.showinfo("Settings", "Settings dialog is under construction!")

    # Edit Menu Callbacks
    def set_grid_size(self):
        size = self.ask_for_input("Set Grid Size", "Enter the new grid size:")
        if size:
            try:
                size = int(size)
                if 5 <= size <= 50:
                    self.app.grid_size_entry.delete(0, tk.END)
                    self.app.grid_size_entry.insert(0, str(size))
                    self.app.update_grid_size()
                else:
                    raise ValueError("Grid size must be between 5 and 50.")
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid grid size! {e}")

    def set_delay(self):
        delay = self.ask_for_input("Set Delay", "Enter the delay (in seconds):")
        if delay:
            try:
                delay = float(delay)
                if delay >= 0:
                    self.app.speed_entry.delete(0, tk.END)
                    self.app.speed_entry.insert(0, str(delay))
                else:
                    raise ValueError("Delay must be non-negative.")
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid delay! {e}")

    def transparent_environment(self):
        # Placeholder for transparent environment functionality
        messagebox.showinfo("Transparent Environment", "Transparent environment toggle is under construction!")

    # Path Planning Menu Callbacks
    def show_neighbouring(self):
        # Placeholder for showing neighbouring cells
        messagebox.showinfo("Show Neighbouring", "Show neighbouring cells is under construction!")

    def show_calculations(self):
        # Placeholder for showing path calculations
        messagebox.showinfo("Show Calculations", "Show calculations is under construction!")

    # Help Menu Callbacks
    def show_instructions(self):
        instructions = (
            "Instructions for Using Dynamic Path Planning:\n\n"
            "- Left-click on cells to add/remove obstacles.\n"
            "- Right-click on a cell to set the goal.\n"
            "- Use the menu options to customize the grid size, delay, and other settings."
        )
        messagebox.showinfo("Instructions", instructions)

    def show_about(self):
        about_text = (
            "Dynamic Path Planning\n"
            "Version 1.0\n\n"
            "Developed by Dr. Amir Ai Mokhtarzadeh.\n"
            "A tool for interactive A* path planning with dynamic obstacle handling."
        )
        messagebox.showinfo("About Dynamic Path Planning", about_text)

    def show_about_astar(self):
        try:
            with open("about_astar.txt", "r") as file:
                about_astar = file.read()
            messagebox.showinfo("About A*", about_astar)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load About A* text: {e}")

    # Utility Method for Input Dialog
    def ask_for_input(self, title, prompt):
        input_window = tk.Toplevel(self.master)
        input_window.title(title)
        input_window.geometry("300x100")
        tk.Label(input_window, text=prompt).pack(pady=10)
        entry = tk.Entry(input_window)
        entry.pack(pady=5)
        result = {"value": None}

        def on_ok():
            result["value"] = entry.get()
            input_window.destroy()

        tk.Button(input_window, text="OK", command=on_ok).pack()
        self.master.wait_window(input_window)
        return result["value"]

    def open_graph_settings(self):
        """Open a pop-up window for graph settings."""
        settings_window = tk.Toplevel(self.master)
        settings_window.title("Graph Settings")
        settings_window.geometry("400x300")

        # Graph Style
        tk.Label(settings_window, text="Graph Style:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.graph_style_var = tk.StringVar(value="line")
        style_menu = tk.OptionMenu(settings_window, self.graph_style_var, "line", "scatter", "bar")
        style_menu.grid(row=0, column=1, padx=10, sticky="w")

        # Density
        tk.Label(settings_window, text="Density (%):").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.density_var = tk.DoubleVar(value=10.0)
        tk.Entry(settings_window, textvariable=self.density_var, width=10).grid(row=1, column=1, padx=10, sticky="w")

        # Speed
        tk.Label(settings_window, text="Speed (s):").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.speed_var = tk.DoubleVar(value=1.0)
        tk.Entry(settings_window, textvariable=self.speed_var, width=10).grid(row=2, column=1, padx=10, sticky="w")

        # Close Button
        tk.Button(settings_window, text="Close", command=settings_window.destroy).grid(row=3, column=0, columnspan=2, pady=10)

    def display_graph(self):
        """Display the graph using the current settings."""
        try:
            style = self.graph_style_var.get()
            density = self.density_var.get()
            speed = self.speed_var.get()

            # Example data; replace with actual data collection
            densities = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
            a_star_times = [density * speed * 0.1 for density in densities]
            q_learning_times = [density * speed * 0.15 for density in densities]

            # Call the graph plotting function
            plot_graph(style, densities, a_star_times, q_learning_times, self.master)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to display graph: {e}")
