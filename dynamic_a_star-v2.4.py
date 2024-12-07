"""
        Create a menu bar for the main application.
        :param master: The root window or parent widget.
        :param app: The main application object for callback integration.
        
        Author: Dr. Amir Ali Mokhtarzadeh
        2022- 2024
        No any part of this program can be changed, used, distribute, or copied
        without author's consent.
        
        
        
        Current bugs and issues:
        1- opening and changing a saved map cannot be dsaved as a new map (Done)
        2- some menu items need to be completed
        3- there is an index out of bound error for x which is generated from ne draw_grid function (done)
        4- Q Learning cannot be done for over 19 size grid
        
"""




import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import time
import threading
import path_planning
from path_menu_bar2 import MenuBar
import random
from graph_styles import plot_graph


class AStarGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dynamic Path Planner")
        self.root.geometry("900x500")  # Adjust to your preferred dimensions
        try:
            style = ttk.Style()
            style.theme_use("clam")  # Replace "clam" with your preferred theme
            print("Theme applied successfully.")
        except Exception as e:
            print(f"Error applying theme: {e}")
        # Initialize variables
        self.grid_size = 20
        self.speed = 0.5
        self.dynamic_obstacles_var = tk.BooleanVar(value=False)
        self.show_planning = tk.BooleanVar(value=True)
        self.algorithm_var = tk.StringVar(value="A*")
        self.start_var = tk.StringVar(value="(0, 0)")  # Default start
        self.goal_var = tk.StringVar(value="(0, 0)")  # Default goal
        self.time_var = tk.StringVar(value="0.00 s")  # Default time
        
        # Path colors
        self.path_colors = ["red", "blue", "green", "purple", "orange"]
        self.current_color_index = 0

        self.grid_size = 10
        self.cell_size = 30
        self.speed = 0.1
        self.show_planning = tk.BooleanVar(value=True)
        self.running = False
        self.grid = []
        self.dynamic_grid = []
        self.goal_cell = None
        self.start_cell = (0, 0)
        self.path_lines = []  # To store references to path lines
        self.case = True
        self.setup_ui()
        self.current_cell = (0,0)
        self.create_dynamic_obstacle_settings()
        self.static_obstacle_cells = set()  # Track manually placed block obstacles
        self.dynamic_obstacle_cells = set()  # Track dynamic obstacles
        # Setup UI
        self.setup_ui()
        self.dynamic_grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
    def setup_ui(self):
        # Control Panel
        control_frame = ttk.LabelFrame(self.root, text="Controls")
        control_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nw")
      
        ttk.Label(control_frame, text="Grid Size:").grid(row=0, column=0, padx=5, sticky="w")
        self.grid_size_entry = ttk.Entry(control_frame, width=10)
        self.grid_size_entry.insert(0, str(self.grid_size))
        self.grid_size_entry.grid(row=0, column=1, padx=5)
        # cell size
        ttk.Label(control_frame, text="Cell Size:").grid(row=1, column=0, padx=5, sticky="w")
        self.cell_size_entry = ttk.Entry(control_frame, width=10)
        self.cell_size_entry.insert(0, str(self.cell_size))
        self.cell_size_entry.grid(row=1, column=1, padx=5)

        ttk.Button(control_frame, text="Clear", command=self.clear_grid).grid(row=3, column=0, padx=10, pady=5)
        ttk.Button(control_frame, text="Update", command=self.update_grid_size).grid(row=3, column=1, columnspan=2, padx=10, pady=5)

        # Dynamic Obstacles
        self.create_dynamic_obstacle_settings()

        # Status Frame
        status_frame = ttk.LabelFrame(self.root, text="Path Parameters")
        status_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=0, sticky="nsew")
        ttk.Label(status_frame, text="Start:").grid(row=0, column=0, sticky="w")
        self.start_entry = ttk.Entry(status_frame, width=20)
        self.start_entry.grid(row=0, column=1, sticky="w")
        ttk.Label(status_frame, text="Goal:").grid(row=1, column=0, sticky="w")
        self.goal_entry = ttk.Entry(status_frame, width=20)
        self.goal_entry.grid(row=1, column=1, sticky="w")
        ttk.Label(status_frame, text="Time Taken:").grid(row=2, column=0, sticky="w")
        self.time_entry = ttk.Entry(status_frame, width=20)
        self.time_entry.grid(row=2, column=1, sticky="w")
        ttk.Button(status_frame, text="Start", command=self.start_path).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(status_frame, text="Stop", command=self.stop_path).grid(row=1, column=3, padx=5, pady=5)
        ttk.Button(status_frame, text="Clear Path", command=self.clear_path_only).grid(row=0, column=4, padx=5, pady=5)
        ttk.Label(status_frame, text="Algorithm:").grid(row=0, column=5, padx=5, sticky="w")
        ttk.Checkbutton(status_frame, text="Show Planning", variable=self.show_planning).grid(row=1, column=6, columnspan=2, pady=5)
        algorithm_menu = ttk.OptionMenu(status_frame, self.algorithm_var, "A*", "A*", "Q-Learning")
        algorithm_menu.grid(row=0, column=6, padx=5, sticky="w")
        ttk.Label(status_frame, text="Draw Speed (s):").grid(row=1, column=4, padx=5, sticky="w")
        self.speed_entry = ttk.Entry(status_frame, width=10)
        self.speed_entry.insert(0, str(self.speed))
        self.speed_entry.grid(row=1, column=5, padx=5)

        # Canvas
        self.canvas = tk.Canvas(self.root, width=300, height=300, bg="white")
        self.canvas.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.toggle_obstacle)
        self.canvas.bind("<Button-3>", self.toggle_goal_cell)

        # Footer
        footer = ttk.Label(self.root, text="© 2022-2024, Dynamic Path Planner Ver. 1 - by Dr. Amir Ali Mokhtarzadeh", font=("Arial", 8))
        footer.grid(row=2, column=0, columnspan=2, pady=5, sticky="s")

        self.draw_grid()
        

    def create_dynamic_obstacle_settings(self):
        settings_frame = ttk.LabelFrame(self.root, text="Dynamic Obstacle Settings")
        settings_frame.grid(row=1, column=2, padx=10, pady=10, sticky="nw")

        ttk.Label(settings_frame, text="Density:").grid(row=0, column=0, sticky="w")
        self.density_var = tk.DoubleVar(value=0.1)
        density_slider = ttk.Scale(settings_frame, from_=1, to=20, variable=self.density_var)
        density_slider.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(settings_frame, text="Speed (s):").grid(row=1, column=0, sticky="w")
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_slider = ttk.Scale(settings_frame, from_=1, to=20, variable=self.speed_var)
        speed_slider.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(settings_frame, text="Time Range (s):").grid(row=2, column=0, columnspan=2, sticky="w")
        self.time_min_var = tk.IntVar(value=1)
        self.time_max_var = tk.IntVar(value=10)
        ttk.Label(settings_frame, text="Min:").grid(row=3, column=0, sticky="e")
        ttk.Entry(settings_frame, textvariable=self.time_min_var).grid(row=3, column=1, sticky="w")
        ttk.Label(settings_frame, text="Max:").grid(row=4, column=0, sticky="e")
        ttk.Entry(settings_frame, textvariable=self.time_max_var).grid(row=4, column=1, sticky="w")

        ttk.Label(settings_frame, text="Group Size:").grid(row=5, column=0, sticky="w")
        self.group_size_var = tk.IntVar(value=1)
        group_size_slider = ttk.Scale(settings_frame, from_=1, to=10, variable=self.group_size_var)
        group_size_slider.grid(row=5, column=1, padx=5, pady=0, sticky="ew")

        ttk.Checkbutton(settings_frame, text="Enable Dynamic Obstacles", variable=self.dynamic_obstacles_var, command=self.toggle_dynamic_obstacles).grid(row=6, column=0, columnspan=2, pady=5)

        self.obstacle_type_var = tk.StringVar(value="block")  # Default to block
        ttk.Label(settings_frame, text="Type:").grid(row=7, column=0, padx=5, pady=5, sticky="w")
        obstacle_type_menu = ttk.OptionMenu(settings_frame, self.obstacle_type_var, "block", "block", "moving")
        obstacle_type_menu.grid(row=7, column=1, padx=5, pady=5, sticky="w")
        
  
    def collect_data(self):
        densities = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        a_star_times = []
        q_learning_times = []

        for density in densities:
            self.grid_size = 10  # Example grid size
            self.grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
            self.add_dynamic_obstacles(density=density, speed=1.0)

            # Measure A* time
            start_time = time.time()
            path_planning.run_a_star(self.grid, self.start_cell, self.goal_cell)
            end_time = time.time()
            a_star_times.append(end_time - start_time)

            # Measure Q-Learning time
            start_time = time.time()
            path_planning.run_q_learning(self.grid, self.start_cell, self.goal_cell)
            end_time = time.time()
            q_learning_times.append(end_time - start_time)

        return densities, a_star_times, q_learning_times

    def display_graph(self):
        style = self.graph_style_var.get()
        densities, a_star_times, q_learning_times = self.collect_data()
        plot_graph(style, densities, a_star_times, q_learning_times, self.root)


    # This version works for propery open a saved environment
    def draw_grid(self):
        self.canvas.delete("all")
        if self.case:
            self.grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
            self.dynamic_grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        else:
            #self.grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
            self.start_cell = (0, 0)  # Reset start cell
            self.goal_cell = None  # Reset goal cell
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x0, y0 = i * self.cell_size, j * self.cell_size
                x1, y1 = x0 + self.cell_size, y0 + self.cell_size
                self.canvas.create_rectangle(
                    x0, y0, x1, y1, fill="white", outline="black", tags=f"cell_{i}_{j}"
                )

    def toggle_dynamic_obstacles(self):
        """
        Enable or disable dynamic obstacles based on the checkbox.
        """
        self.dynamic_obstacles_enabled = self.dynamic_obstacles_var.get()
        if self.dynamic_obstacles_enabled:
            # Start adding dynamic obstacles with settings from the GUI
            print("in here again")
            density = self.density_var.get()
            speed = self.speed_var.get()
            time_range = (self.time_min_var.get(), self.time_max_var.get())
            group_size = self.group_size_var.get()

            self.add_dynamic_obstacles(density=density, time_range=time_range, group_size=group_size)
        else:
            # Clear all existing dynamic obstacles
            for x in range(self.grid_size):
                for y in range(self.grid_size):
                    if self.grid[x][y] == 2:  # If the cell is an obstacle
                        self.grid[x][y] = 0  # Remove obstacle
                        self.dynamic_grid = 0
                        print("All removes")
                        self.canvas.itemconfig(f"cell_{x}_{y}", fill="white")
                    
   
    def toggle_obstacle(self, event):
        """
        Toggle a static obstacle (block) at the clicked cell.
        """
        x, y = event.x // self.cell_size, event.y // self.cell_size

        # Ensure the click is within bounds
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            if (x, y) == self.start_cell or (x, y) == self.goal_cell:
                return  # Do not place obstacles on start or goal cells

            # Toggle static obstacle
            if self.grid[x][y] == 1 and (x, y) not in self.dynamic_obstacle_cells:
                self.grid[x][y] = 0
                self.canvas.itemconfig(f"cell_{x}_{y}", fill="white")  # Remove obstacle
                self.static_obstacle_cells.discard((x, y))  # Remove from static list
            elif self.grid[x][y] == 0:
                self.grid[x][y] = 1
                self.canvas.itemconfig(f"cell_{x}_{y}", fill="black")  # Add obstacle
                self.static_obstacle_cells.add((x, y))  # Add to static list
     
     
    def toggle_goal_cell(self, event):
        x, y = event.x // self.cell_size, event.y // self.cell_size
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            if self.goal_cell == (x, y):
                # Remove goal cell
                self.goal_cell = None
                self.canvas.itemconfig(f"cell_{x}_{y}", fill="white")
            elif self.grid[x][y] == 0:
                # Set a new goal cell
                if self.goal_cell:
                    # Clear the previous goal cell
                    self.canvas.itemconfig(f"cell_{self.goal_cell[0]}_{self.goal_cell[1]}", fill="white")
                self.goal_cell = (x, y)
                self.canvas.itemconfig(f"cell_{x}_{y}", fill="green")
 
       
    def start_path(self):
        try:
            self.speed = float(self.speed_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid speed value!")
            return

        if not self.goal_cell:
            messagebox.showwarning("Warning", "Set a goal cell before starting!")
            return

        self.running = True
        # Run the A* algorithm in a thread
        threading.Thread(target=self.run_a_star, daemon=True).start()

    def stop_path(self):
        self.running = False

    def clear_grid(self):
        self.stop_path()
        self.goal_cell = None
        self.start_cell = (0, 0)
        self.path_lines.clear()
        self.draw_grid()

    def clear_path_only(self):
        for line in self.path_lines:
            self.canvas.delete(line)
        self.path_lines.clear()

    def update_grid_size(self):
        try:
            self.cell_size = int(self.cell_size_entry.get())
            new_size = int(self.grid_size_entry.get())
            if new_size < 5 or new_size > 50:
                raise ValueError("Grid size must be between 5 and 50.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid grid size! {e}")
            return

        self.grid_size = new_size
        self.canvas.config(width=self.cell_size * self.grid_size, height=self.cell_size * self.grid_size)
        self.clear_grid()

    def run_a_star(self):
        if not self.goal_cell:
            print("Error: Goal cell is not set.")
            return
        grid = self.grid
        start = self.start_cell
        goal = self.goal_cell
        goal_cell = 0
        algorithm = self.algorithm_var.get() 
        start_time = time.time()
        end_time = time.time()
        col = "red"

        # Update the display values
        self.start_entry.delete(0, tk.END)
        self.start_entry.insert(0, str((3,3)))
        self.goal_entry.delete(0, tk.END)
        self.goal_entry.insert(0, str(goal))
        self.time_entry.delete(0, tk.END)
        try:
            while goal_cell == 0:
                # Call the C++ implementation via the path_planning module
                
                if algorithm == "A*":
                    start_time = time.time()
                    path = path_planning.run_a_star(grid, start, goal)
                    end_time = time.time()
                elif algorithm == "Q-Learning":
                    start_time = time.time()
                    path = path_planning.run_q_learning(grid, start, goal)
                    end_time = time.time()
                    col = "blue"
                # Update the display values
                self.start_entry.delete(0, tk.END)
                self.start_entry.insert(0, str(start))
                self.goal_entry.delete(0, tk.END)
                self.goal_entry.insert(0, str(goal))
                self.time_entry.delete(0, tk.END)
                self.time_entry.insert(0,str(f"{end_time - start_time:.2f} s"))
                print(f"Path found: {path}")
                self.draw_path_line(path, col)  # Draw the calculated path as a line
                print("The start cell is: ", self.start_cell,"     Goal to reach at: ", self.goal_cell)
                if self.start_cell == self.goal_cell:
                    print("path planning is completed ....")
                    self.start_cell = (0,0)
                    self.current_cell = self.start_cell
                    return
                if self.current_cell != (0,0):
                    print("Redrawing starts from: ", start)
                    start = self.current_cell
            		
        except RuntimeError as e:
            print(f"Error during A* execution: {e}")
        finally:
            self.running = False

    def get_neighbors(self, cell):
        x, y = cell
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size and self.grid[nx][ny] == 0:
                neighbors.append((nx, ny))
        return neighbors

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def draw_path(self, path):
        #Draw the calculated path on the canvas.

        for (x, y) in path:
            # Skip the start and goal cells to avoid overwriting their colors
            if (x, y) == self.start_cell or (x, y) == self.goal_cell:
                continue

            # Change the cell's color to indicate the path
            self.canvas.itemconfig(f"cell_{x}_{y}", fill="red")
    
    
    def draw_path_line(self, path, col):
        for i in range(len(path) - 1):
            #if not self.running:
            #    print("Path drawing interrupted.", path[i])
            #    return

            # Get the start and end coordinates of the current segment
            x0, y0 = path[i][0] * self.cell_size + self.cell_size // 2, path[i][1] * self.cell_size + self.cell_size // 2
            x1, y1 = path[i + 1][0] * self.cell_size + self.cell_size // 2, path[i + 1][1] * self.cell_size + self.cell_size // 2
            # if the next cell becomes an obstacle
            if self.grid[path[i+1][0]][path[i+1][1]] == 1 or self.grid[path[i+1][0]][path[i+1][1]] == 1: # or self.grid[path[i+2][0]][path[i+2][1]] == 1:	
                self. current_cell = path[i]
                print(f"Now at:  {path[i]}. ...", "    and current is :", self.current_cell)
                return
            # Check if the current cell becomes an obstacle mid-path
            if self.grid[path[i][0]][path[i][1]] == 1 or self.grid[path[i][0]][path[i][1]] == 2:
                #self.start_cell = path[i]  # Update the start cell to the current point
                #self.recalculate_path()  # Restart pathfinding automatically
                self. current_cell = path[i-1]
                return
            # Draw a red line connecting the cells
            print("Drawing Line from :",path[i-1], "    to: ", path[i], "    toward the goal cell: ", self.goal_cell)
            line = self.canvas.create_line(x0, y0, x1, y1, fill=col, width=2)
            self.path_lines.append(line)
            
            # If it has reach the goal
            print ("The curent cell is : ", path[i], "  and the goal is: ", self.goal_cell)
            if path[i+1] == self.goal_cell:
                self.start_cell = self.goal_cell
                print("Path completed successfully.")
                current_cell = path[i]
                return
            # Add a delay for animation
            time.sleep(self.speed)

        # Update start cell to goal after completing the path
        if self.running:
            self.start_cell = self.goal_cell
            print("Path completed successfully.")
            #current_cell = self.grid[path[i][0]][path[i][1]]
            return
    
    def recalculate_path(self):
        if not self.goal_cell:
            print("Error: Goal cell is not set.")
            return
        grid = self.grid
        start = self.start_cell
        goal = self.goal_cell
        try:
            # Call the C++ implementation via the path_planning module
            path = path_planning.run_a_star(grid, start, goal)
            print(f"New path found: {path}")
            self.draw_path_line(path)  # Redraw the calculated path as a line
        except RuntimeError as e:
            print(f"Error during A* execution: {e}")
        finally:
            self.running = False  
    
    
    
    
   # Adding obstacles
    def add_dynamic_obstacles(self, density=10, speed=1.0, time_range=(5, 15), group_size=1, obstacle_type="block"):
        rows, cols = self.grid_size, self.grid_size
        obstacle_timers = {}  # Dictionary to track dynamic obstacle expiration times
        def create_obstacle_group():
            '''Create a group of dynamic obstacles.'''
            while True:
                x, y = random.randint(0, rows - 1), random.randint(0, cols - 1)
                # Avoid start, goal, static obstacles, and existing dynamic obstacles
                if (x, y) in self.static_obstacle_cells or (x, y) in self.dynamic_obstacle_cells or \
                   (x, y) == self.start_cell or (x, y) == self.goal_cell:
                    continue
                group = [(x, y)]
                for _ in range(group_size - 1):
                    direction = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])  # Right, Down, Left, Up
                    nx, ny = group[-1][0] + direction[0], group[-1][1] + direction[1]
                    if 0 <= nx < rows and 0 <= ny < cols and \
                       (nx, ny) not in self.static_obstacle_cells and \
                       (nx, ny) not in self.dynamic_obstacle_cells and \
                       (nx, ny) != self.start_cell and (nx, ny) != self.goal_cell:
                        group.append((nx, ny))
                return group

        def update_obstacles():
            '''Update dynamic obstacles on the grid.'''
            current_time = time.time()
            # Remove expired obstacles
            to_remove = []
            for (x, y), expire_time in obstacle_timers.items():
                if current_time >= expire_time:
                    self.grid[x][y] = 0
                    #self.dynamic_grid[x][y] = 0
                    self.canvas.itemconfig(f"cell_{x}_{y}", fill="white")
                    to_remove.append((x, y))
            for key in to_remove:
                del obstacle_timers[key]
                self.dynamic_obstacle_cells.discard(key)  # Remove from dynamic list

            # Add new dynamic obstacles based on density
            max_dynamic_obstacles = int((density / 100) * rows * cols)
            if len(self.dynamic_obstacle_cells) < max_dynamic_obstacles:
                group = create_obstacle_group()
                for (x, y) in group:
                    self.grid[x][y] = 2
                    #self.dynamic_grid[x][y] = 1
                    self.canvas.itemconfig(f"cell_{x}_{y}", fill="red")  # Dynamic obstacles are red
                    self.dynamic_obstacle_cells.add((x, y))  # Track dynamic obstacle cells

                    # Set expiration time for each dynamic obstacle
                    if isinstance(time_range, tuple):
                        expire_time = current_time + random.uniform(*time_range)
                    else:
                        expire_time = current_time + time_range
                    obstacle_timers[(x, y)] = expire_time

            # Pause based on speed
            try:
                speed = float(self.speed_entry.get())
                speed = max(1, min(speed, 20))
            except ValueError:
                speed = 1.0
            time.sleep(1 / speed)

            # Repeat updates if dynamic obstacles are enabled
            if self.dynamic_obstacles_enabled:
                self.root.after(50, update_obstacles)  # Schedule the next update

        # Start obstacle updates
        update_obstacles()
    
    

            
if __name__ == "__main__":
    root = tk.Tk()
    app = AStarGUI(root)
    menu = MenuBar(root, app)  # Create and attach the menu bar
    root.mainloop()
