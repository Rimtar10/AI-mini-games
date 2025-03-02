import tkinter as tk
import random
import heapq
from tkinter import messagebox, ttk


class MazeGame:
    DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Down, Right, Up, Left
    
    def __init__(self, root):
        self.root = root
        self.root.title("Maze Escape Game")
        
        # Get screen dimensions
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        
        # Game settings
        self.cell_size = 30
        self.difficulty_settings = {
            "Easy": {"size": 15, "ai_speed": 1, "opening_factor": 0.1, "optimal_move_chance": 0.7},
            "Medium": {"size": 21, "ai_speed": 2, "opening_factor": 0.05, "optimal_move_chance": 0.9},
            "Hard": {"size": None, "ai_speed": 3, "opening_factor": 0.01, "optimal_move_chance": 1.0}
        }
        
        # Colors
        self.colors = {
            "wall": "#333333",
            "path": "#EEEEEE",
            "player": "#00FF00",
            "ai": "#FF0000",
            "exit": "#0000FF"
        }
        
        # Game state
        self.maze = None
        self.player_pos = None
        self.ai_pos = None
        self.exit_pos = None
        self.game_active = False
        self.move_count = 0
        self.current_settings = None
        self.difficulty_var = tk.StringVar(value="Easy")
        
        # Set up the UI
        self.setup_ui()
    
    def setup_ui(self):
        # Control panel
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        
        # Level selector (buttons instead of dropdown)
        level_frame = tk.Frame(control_frame)
        level_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(level_frame, text="Level:").pack(side=tk.LEFT)
        
        # Create button frame
        button_frame = tk.Frame(level_frame)
        button_frame.pack(side=tk.LEFT, padx=5)
        
        # Create level buttons
        for level in self.difficulty_settings.keys():
            level_button = tk.Button(
                button_frame, 
                text=level,
                command=lambda l=level: self.select_level(l),
                width=8
            )
            level_button.pack(side=tk.LEFT, padx=2)
        
        # Restart button
        restart_button = tk.Button(control_frame, text="Restart", command=self.start_game)
        restart_button.pack(side=tk.LEFT, padx=20)
        
        # Game stats
        self.stats_label = tk.Label(self.root, text="Moves: 0 | Level: Easy")
        self.stats_label.pack(pady=5)
        
        # Instructions
        instructions = "Use arrow keys to move. Reach the blue exit before the red AI catches you!"
        tk.Label(self.root, text=instructions).pack(pady=5)
        
        # Canvas container
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Start the game
        self.start_game()
    
    def select_level(self, level):
        self.difficulty_var.set(level)
        self.start_game()
    
    def create_canvas(self, width, height):
        if hasattr(self, 'canvas'):
            self.canvas.destroy()
            
        canvas_width = width * self.cell_size
        canvas_height = height * self.cell_size
        
        self.canvas = tk.Canvas(
            self.canvas_frame, 
            width=canvas_width, 
            height=canvas_height, 
            bg=self.colors["wall"]
        )
        self.canvas.pack(expand=True)
        
        # Bind keyboard events
        self.root.bind("<KeyPress>", self.handle_keypress)
    
    def start_game(self):
        # Get current difficulty settings
        difficulty = self.difficulty_var.get()
        self.current_settings = self.difficulty_settings[difficulty]
        
        # Set size based on difficulty
        if difficulty == "Hard":
            # Calculate maze size based on screen dimensions
            # Adjust cell size for Hard mode to fit screen
            self.cell_size = min(20, self.cell_size)  # Smaller cells for Hard mode
            max_width = self.screen_width // self.cell_size
            max_height = (self.screen_height - 100) // self.cell_size  # Leave room for controls
            size = min(max_width, max_height)
            
            # Make sure size is odd for maze generation
            if size % 2 == 0:
                size -= 1
                
            # Set window to maximize (Hard mode only)
            self.root.state('zoomed')
        else:
            # Normal window for Easy/Medium
            self.cell_size = 30  # Reset cell size for other modes
            size = self.current_settings["size"]
            self.root.state('normal')
            self.root.resizable(False, False)
        
        # Create UI elements
        self.create_canvas(size, size)
        
        # Generate maze and entities
        self.maze = self.generate_maze(size, size)
        self.place_entities(size)
        
        # Reset game state
        self.game_active = True
        self.move_count = 0
        
        # Draw the maze
        self.draw_maze()
        self.update_stats()
    
    def generate_maze(self, width, height):
        # Initialize maze with walls
        maze = [['#' for _ in range(width)] for _ in range(height)]
        
        def carve_passages(x, y, visited=None):
            if visited is None:
                visited = set()
                
            maze[y][x] = ' '
            visited.add((x, y))
            
            # Randomize directions
            directions = list(self.DIRECTIONS)
            random.shuffle(directions)
            
            for dx, dy in directions:
                nx, ny = x + 2*dx, y + 2*dy
                
                if (0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited):
                    # Carve passage
                    maze[y + dy][x + dx] = ' '
                    carve_passages(nx, ny, visited)
        
        # Start from a random position
        start_x = random.randrange(1, width, 2)
        start_y = random.randrange(1, height, 2)
        
        # Adjust if out of bounds
        if start_x >= width: start_x = width - 2
        if start_y >= height: start_y = height - 2
        
        # Generate the maze
        carve_passages(start_x, start_y)
        
        # Add random openings based on difficulty
        opening_factor = self.current_settings["opening_factor"]
        
        for y in range(1, height-1):
            for x in range(1, width-1):
                if maze[y][x] == '#' and random.random() < opening_factor:
                    # Prevent 2x2 open areas
                    if not all(maze[y+dy][x+dx] == ' ' for dx, dy in [(0,0), (1,0), (0,1), (1,1)]):
                        maze[y][x] = ' '
        
        return maze
    
    def place_entities(self, size):
        # Find all empty cells
        empty_cells = []
        for y in range(size):
            for x in range(size):
                if self.maze[y][x] == ' ':
                    empty_cells.append((x, y))
        
        if not empty_cells:
            return  # No empty cells (shouldn't happen)
        
        # Place player in top-left area
        top_left = [(x, y) for x, y in empty_cells if x < size//2 and y < size//2]
        self.player_pos = random.choice(top_left if top_left else empty_cells)
        
        # Place exit in bottom-right area
        bottom_right = [(x, y) for x, y in empty_cells 
                       if x >= size//2 and y >= size//2 and (x, y) != self.player_pos]
        self.exit_pos = random.choice(bottom_right if bottom_right else 
                                     [pos for pos in empty_cells if pos != self.player_pos])
        
        # Place AI far from player
        available = [(x, y) for x, y in empty_cells 
                    if (x, y) != self.player_pos and (x, y) != self.exit_pos]
        
        # Sort by distance (descending)
        available.sort(key=lambda pos: -self.manhattan_distance(pos, self.player_pos))
        
        # Choose one of the farthest positions
        far_positions = available[:max(1, len(available) // 10)]
        self.ai_pos = random.choice(far_positions)
    
    def draw_maze(self):
        self.canvas.delete("all")
        
        size = len(self.maze)
        
        # Draw maze cells
        for y in range(size):
            for x in range(size):
                x1, y1 = x * self.cell_size, y * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                
                if self.maze[y][x] == '#':
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=self.colors["wall"], outline="")
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=self.colors["path"], outline="")
        
        # Draw exit
        ex, ey = self.exit_pos
        self.draw_entity(ex, ey, self.colors["exit"], "rectangle")
        
        # Draw AI
        ax, ay = self.ai_pos
        self.draw_entity(ax, ay, self.colors["ai"], "oval")
        
        # Draw player
        px, py = self.player_pos
        self.draw_entity(px, py, self.colors["player"], "oval")
    
    def draw_entity(self, x, y, color, shape):
        x1, y1 = x * self.cell_size, y * self.cell_size
        x2, y2 = x1 + self.cell_size, y1 + self.cell_size
        
        if shape == "rectangle":
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
        else:  # "oval"
            self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline="")
    
    def update_stats(self):
        self.stats_label.config(text=f"Moves: {self.move_count} | Level: {self.difficulty_var.get()}")
    
    def handle_keypress(self, event):
        if not self.game_active:
            return
        
        px, py = self.player_pos
        new_px, new_py = px, py
        
        # Process arrow key input
        if event.keysym == 'Up':
            new_py -= 1
        elif event.keysym == 'Down':
            new_py += 1
        elif event.keysym == 'Left':
            new_px -= 1
        elif event.keysym == 'Right':
            new_px += 1
        else:
            return  # Not a movement key
        
        # Validate move
        if self.is_valid_move(new_px, new_py):
            # If the AI is already at the new position, the player loses immediately
            if (new_px, new_py) == self.ai_pos:
                self.player_pos = (new_px, new_py)  # Move player to AI position (for visual feedback)
                self.move_count += 1
                self.game_active = False
                self.draw_maze()
                self.update_stats()
                self.show_game_result(False)
                return
                
            self.player_pos = (new_px, new_py)
            self.move_count += 1
            
            # Check win condition
            if self.player_pos == self.exit_pos:
                self.game_active = False
                self.draw_maze()
                self.update_stats()
                self.show_game_result(True)
                return
            
            # Move AI
            for _ in range(self.current_settings["ai_speed"]):
                if self.game_active:
                    self.move_ai()
                    
                    # Check if AI caught player
                    if self.ai_pos == self.player_pos:
                        self.game_active = False
                        self.draw_maze()
                        self.update_stats()
                        self.show_game_result(False)
                        return
            
            # Update display
            self.draw_maze()
            self.update_stats()
    
    def is_valid_move(self, x, y):
        size = len(self.maze)
        return (0 <= x < size and 0 <= y < size and self.maze[y][x] != '#')
    
    def move_ai(self):
        difficulty = self.difficulty_var.get()
        
        if difficulty == "Hard":
            # Use A* pathfinding
            path = self.a_star_search(self.ai_pos, self.player_pos)
            if path and len(path) > 1:
                self.ai_pos = path[1]  # Next step in path
        else:
            # Simpler pathfinding for Easy/Medium
            ax, ay = self.ai_pos
            possible_moves = []
            
            # Get all valid moves
            for dx, dy in self.DIRECTIONS:
                nx, ny = ax + dx, ay + dy
                if self.is_valid_move(nx, ny):
                    possible_moves.append((nx, ny))
            
            if possible_moves:
                # Choose move based on difficulty
                optimal_chance = self.current_settings["optimal_move_chance"]
                
                if random.random() < optimal_chance:
                    # Sort by distance to player (ascending)
                    possible_moves.sort(key=lambda pos: self.manhattan_distance(pos, self.player_pos))
                    self.ai_pos = possible_moves[0]  # Best move
                else:
                    # Random move
                    self.ai_pos = random.choice(possible_moves)
    
    def a_star_search(self, start, goal):
        # A* search algorithm with priority queue
        frontier = [(0, start)]  # (priority, position)
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        while frontier:
            _, current = heapq.heappop(frontier)
            
            if current == goal:
                break
                
            cx, cy = current
            for dx, dy in self.DIRECTIONS:
                next_pos = (cx + dx, cy + dy)
                nx, ny = next_pos
                
                if self.is_valid_move(nx, ny):
                    new_cost = cost_so_far[current] + 1
                    
                    if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                        cost_so_far[next_pos] = new_cost
                        priority = new_cost + self.manhattan_distance(next_pos, goal)
                        heapq.heappush(frontier, (priority, next_pos))
                        came_from[next_pos] = current
        
        # Reconstruct path
        if goal not in came_from:
            return None
            
        path = [goal]
        current = goal
        while current != start:
            current = came_from[current]
            path.append(current)
        path.reverse()
        
        return path
    
    def manhattan_distance(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def show_game_result(self, won):
        if won:
            title = "Victory!"
            message = f"Congratulations! You escaped the maze in {self.move_count} moves."
        else:
            title = "Game Over"
            message = f"The AI caught you after {self.move_count} moves. Better luck next time!"
        
        result = messagebox.askquestion(title, message + "\nDo you want to play again?")
        if result == 'yes':
            self.start_game()


if __name__ == "__main__":
    root = tk.Tk()
    game = MazeGame(root)
    root.mainloop()