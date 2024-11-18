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
import time
import threading
import path_planning
from path_menu_bar2 import MenuBar

class AStarGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dynamic A* Path Planning")
        
        # StringVars for displaying information
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
        self.goal_cell = None
        self.start_cell = (0, 0)
        self.path_lines = []  # To store references to path lines
        self.case = True
        self.setup_ui()
        self.current_cell = (0,0)
    def setup_ui(self):
        # Control panel
        control_frame = tk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Label(control_frame, text="Grid Size:").pack(side=tk.LEFT, padx=5)
        self.grid_size_entry = tk.Entry(control_frame, width=5)
        self.grid_size_entry.insert(0, str(self.grid_size))
        self.grid_size_entry.pack(side=tk.LEFT)

        tk.Label(control_frame, text="Draw Speed (s):").pack(side=tk.LEFT, padx=5)
        self.speed_entry = tk.Entry(control_frame, width=5)
        self.speed_entry.insert(0, str(self.speed))
        self.speed_entry.pack(side=tk.LEFT)

        tk.Button(control_frame, text="Start", command=self.start_path).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Stop", command=self.stop_path).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Clear Path", command=self.clear_path_only).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Clear Grid", command=self.clear_grid).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Update Grid", command=self.update_grid_size).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(control_frame, text="Show Planning", variable=self.show_planning).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Exit", command=self.root.quit).pack(side=tk.LEFT, padx=5)

        # Canvas for grid
        self.canvas = tk.Canvas(self.root, width=self.cell_size * self.grid_size,
                                height=self.cell_size * self.grid_size)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.toggle_obstacle)
        self.canvas.bind("<Button-3>", self.toggle_goal_cell)
        
        # choice of path algorithm
        self.algorithm_var = tk.StringVar(value="A*")  # Default to A*
        algorithm_menu = tk.OptionMenu(self.root, self.algorithm_var, "A*", "Q-Learning")
        algorithm_menu.pack()
        
        
        # Labels and entry widgets for displaying start, goal, and time
        tk.Label(self.root, text="Start:")
        self.start_entry = tk.Entry(self.root, textvariable=self.start_var, width=20)
        self.start_entry.pack()

        tk.Label(self.root, text="Goal:")
        self.goal_entry = tk.Entry(self.root, textvariable=self.goal_var, width=20)
        self.goal_entry.pack()

        tk.Label(self.root, text="Time Taken:")
        self.time_entry = tk.Entry(self.root, textvariable=self.time_var, width=20)
        self.time_entry.pack()
        
        # Footer for copyright
        footer = tk.Label(self.root, text="© 2022-2024, Dynamic A* Path Planner by Dr. Amir Ali Mokhtarzadeh", fg="dark grey", font=("Arial", 8))
        footer.pack(side=tk.BOTTOM, pady=5)

        self.draw_grid()
        
    
    
    # This version works for propery open a saved environment
    def draw_grid(self):
        self.canvas.delete("all")
        if self.case:
            self.grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
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
    '''
    # This version works well with a new environment, but not with opening a saved one
    def draw_grid(self):
        self.canvas.delete("all")
        self.grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x0, y0 = i * self.cell_size, j * self.cell_size
                x1, y1 = x0 + self.cell_size, y0 + self.cell_size
                self.canvas.create_rectangle(x0, y0, x1, y1, fill="white", outline="black", tags=f"cell_{i}_{j}")

        self.start_cell = (0, 0)  # Reset start cell
    '''
    def toggle_obstacle(self, event):
        if self.running:
            self.running = False  # Stop current path drawing
            # here I want later to put the starting point, wherer it has stopped 
            time.sleep(0.1)  # Small delay to ensure drawing stops

        x, y = event.x // self.cell_size, event.y // self.cell_size
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            if (x, y) == self.goal_cell:  # Prevent toggling the goal cell as an obstacle
                return
            self.grid[x][y] = 1 - self.grid[x][y]
            color = "black" if self.grid[x][y] == 1 else "white"
            self.canvas.itemconfig(f"cell_{x}_{y}", fill=color)

            if self.grid[x][y] == 1 and (x, y) == self.start_cell:
                # If obstacle placed on the current path, update start cell
                self.start_cell = (x, y)
                self.start_path()  # Restart pathfinding with the new start

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
 
 
    '''               
    def start_path(self):
        if not self.goal_cell:
            print("Error: Goal cell is not set.")
            return

        self.running = True
        grid = self.grid
        start = self.start_cell
        goal = self.goal_cell

        algorithm = self.algorithm_var.get()

        if algorithm == "A*":
            threading.Thread(target=self.run_a_star, args=(), daemon=True).start()
        elif algorithm == "Q-Learning":
            threading.Thread(target=self.run_q_learning, args=(grid, start, goal), daemon=True).start()              
    '''            
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
    
    
    
    ''' 
    def start_path(self):
        try:
            self.speed = float(self.speed_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid speed!")
            return

        if not self.goal_cell:
            messagebox.showwarning("Warning", "Set a goal cell before starting!")
            return

        self.running = True
        threading.Thread(target=self.run_a_star, daemon=True).start()
    '''
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

        # Update the display values
        self.start_entry.delete(0, tk.END)
        self.start_entry.insert(0, str((3,3)))
        self.goal_entry.delete(0, tk.END)
        self.goal_entry.insert(0, str(goal))
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0,str(f"{end_time - start_time:.2f} s"))

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
                # Update the display values
                self.start_entry.delete(0, tk.END)
                self.start_entry.insert(0, str(start))
                self.goal_entry.delete(0, tk.END)
                self.goal_entry.insert(0, str(goal))
                self.time_entry.delete(0, tk.END)
                self.time_entry.insert(0,str(f"{end_time - start_time:.2f} s"))
                print(f"Path found: {path}")
                self.draw_path_line(path)  # Draw the calculated path as a line
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


    '''
    def run_a_star(self):
        open_set = [(0, self.start_cell)]
        came_from = {}
        g_score = {self.start_cell: 0}
        f_score = {self.start_cell: self.heuristic(self.start_cell, self.goal_cell)}

        while open_set and self.running:
            open_set.sort(key=lambda x: x[0])
            _, current = open_set.pop(0)

            if current == self.goal_cell:
                self.draw_path_line(came_from, current)
                return

            for neighbor in self.get_neighbors(current):
                tentative_g_score = g_score[current] + 1
                if tentative_g_score < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, self.goal_cell)
                    if neighbor not in [x[1] for x in open_set]:
                        open_set.append((f_score[neighbor], neighbor))

            if self.show_planning.get():
                self.canvas.itemconfig(f"cell_{current[0]}_{current[1]}", fill="light grey")

        if self.running:
            messagebox.showinfo("Info", "Path not found!")
    '''
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
        """
        Draw the calculated path on the canvas.

        :param path: List of tuples representing the path [(x1, y1), (x2, y2), ...].
        """
        for (x, y) in path:
            # Skip the start and goal cells to avoid overwriting their colors
            if (x, y) == self.start_cell or (x, y) == self.goal_cell:
                continue

            # Change the cell's color to indicate the path
            self.canvas.itemconfig(f"cell_{x}_{y}", fill="red")
    
    
    def draw_path_line(self, path):
        for i in range(len(path) - 1):
            #if not self.running:
            #    print("Path drawing interrupted.", path[i])
            #    return

            # Get the start and end coordinates of the current segment
            x0, y0 = path[i][0] * self.cell_size + self.cell_size // 2, path[i][1] * self.cell_size + self.cell_size // 2
            x1, y1 = path[i + 1][0] * self.cell_size + self.cell_size // 2, path[i + 1][1] * self.cell_size + self.cell_size // 2
            # if the next cell becomes an obstacle
            if self.grid[path[i+1][0]][path[i+1][1]] == 1: # or self.grid[path[i+2][0]][path[i+2][1]] == 1:	
                self. current_cell = path[i]
                print(f"Now at:  {path[i]}. ...", "    and current is :", self.current_cell)
                return
            # Check if the current cell becomes an obstacle mid-path
            if self.grid[path[i][0]][path[i][1]] == 1:
                self.start_cell = path[i]  # Update the start cell to the current point
                self.recalculate_path()  # Restart pathfinding automatically
                return
            # Draw a red line connecting the cells
            print("Drawing Line from :",path[i-1], "    to: ", path[i], "    toward the goal cell: ", self.goal_cell)
            line = self.canvas.create_line(x0, y0, x1, y1, fill="red", width=2)
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
    
    '''
    # it cannot re-draw new path successfully
    def draw_path_line(self, path):
        """
        Draw the calculated path on the canvas as a continuous line.

        :param path: List of tuples representing the path [(x1, y1), (x2, y2), ...].
        """
        for i in range(len(path) - 1):
            # Get the start and end coordinates of the current segment
            x0, y0 = path[i][0] * self.cell_size + self.cell_size // 2, path[i][1] * self.cell_size + self.cell_size // 2
            x1, y1 = path[i + 1][0] * self.cell_size + self.cell_size // 2, path[i + 1][1] * self.cell_size + self.cell_size // 2

            # Draw a red line connecting the cells
            self.canvas.create_line(x0, y0, x1, y1, fill="red", width=2)

            # Optionally add a delay for animation
            if self.running:
                time.sleep(self.speed)
            
    # the first design
    def draw_path_line(self, came_from, current):
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]

        path.reverse()

        # Get the next color for the path
        path_color = self.path_colors[self.current_color_index]
        self.current_color_index = (self.current_color_index + 1) % len(self.path_colors)

        for i in range(len(path) - 1):
            if not self.running or self.grid[path[i][0]][path[i][1]] == 1:
                # Stop drawing if the path is interrupted or obstacle is set
                self.start_cell = path[i]
                self.start_path()  # Restart pathfinding
                return

            x0, y0 = path[i][0] * self.cell_size + self.cell_size // 2, path[i][1] * self.cell_size + self.cell_size // 2
            x1, y1 = path[i + 1][0] * self.cell_size + self.cell_size // 2, path[i + 1][1] * self.cell_size + self.cell_size // 2
            # Draw the path segment
            line = self.canvas.create_line(x0, y0, x1, y1, fill=path_color, width=2)
            self.path_lines.append(line)  # Store the line reference for clearing later
            time.sleep(self.speed)

        # Set the new start cell to the goal cell after completing the path
        if self.running:
            self.start_cell = self.goal_cell

    '''
            
if __name__ == "__main__":
    root = tk.Tk()
    app = AStarGUI(root)
    menu = MenuBar(root, app)  # Create and attach the menu bar
    root.mainloop()
