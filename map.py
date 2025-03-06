
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import numpy as np
import heapq

class Node:
    def __init__(self, state, parent=None, g=0, h=0):
        self.state = state  # (x, y) coordinates
        self.parent = parent
        self.g = g  # Cost from start to node
        self.h = h  # Heuristic (estimated cost to goal)
        self.f = g + h  # Total cost
    
    def __lt__(self, other):
        return self.f < other.f

class MapRouteFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("Map Route Finder - A* Search")
        
        self.original_image = None
        self.processed_image = None
        self.display_image = None
        self.start_point = None
        self.end_point = None
        self.route = None
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        control_frame = tk.Frame(main_frame)
        control_frame.pack(side=tk.TOP, fill=tk.X, pady=10)
        
        self.load_button = tk.Button(control_frame, text="Load Map Image", command=self.load_image)
        self.load_button.pack(side=tk.LEFT, padx=5)
        
        self.find_route_button = tk.Button(control_frame, text="Find Route", command=self.find_route, state=tk.DISABLED)
        self.find_route_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = tk.Button(control_frame, text="Clear Points", command=self.clear_points)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        self.canvas = tk.Canvas(main_frame, bg="gray")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_click)
    
    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if not file_path:
            return
        try:
            self.original_image = Image.open(file_path)
            self.process_image()
            self.display_image = self.original_image.copy()
            self.update_canvas()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def process_image(self):
        hsv_image = self.original_image.convert('HSV')
        np_image = np.array(hsv_image)
        yellow_mask = (np_image[:,:,0] > 20) & (np_image[:,:,0] < 40) & (np_image[:,:,1] > 100) & (np_image[:,:,2] > 100)
        self.processed_image = np.where(yellow_mask, 255, 0).astype(np.uint8)
    
    def on_canvas_click(self, event):
        x, y = event.x, event.y
        if self.start_point is None:
            self.start_point = (x, y)
        elif self.end_point is None:
            self.end_point = (x, y)
            self.find_route_button.config(state=tk.NORMAL)
        self.display_image = self.original_image.copy()
        self.draw_points()
        self.update_canvas()
    
    def draw_points(self):
        if self.display_image is None:
            return
        draw = ImageDraw.Draw(self.display_image)
        if self.start_point:
            x, y = self.start_point
            draw.ellipse((x-5, y-5, x+5, y+5), fill='red', outline='white')
        if self.end_point:
            x, y = self.end_point
            draw.ellipse((x-5, y-5, x+5, y+5), fill='green', outline='white')
        if self.route:
            for i in range(1, len(self.route)):
                draw.line([self.route[i-1], self.route[i]], fill='blue', width=3)
    
    def update_canvas(self):
        if self.display_image is None:
            return
        self.tk_image = ImageTk.PhotoImage(self.display_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
    
    def find_route(self):
        if not self.start_point or not self.end_point or self.processed_image is None:
            return
        road_map = np.array(self.processed_image)
        self.route = self.a_star_search(road_map, self.start_point, self.end_point)
        if not self.route:
            messagebox.showinfo("No Route Found", "No valid route could be found along the yellow lines.")
        self.display_image = self.original_image.copy()
        self.draw_points()
        self.update_canvas()
    
    def a_star_search(self, road_map, start, goal):
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
        open_set = []
        heapq.heappush(open_set, Node(start, None, 0, heuristic(start, goal)))
        visited = set()
        
        while open_set:
            current = heapq.heappop(open_set)
            if current.state in visited:
                continue
            visited.add(current.state)
            if current.state == goal:
                return self.reconstruct_path(current)
            x, y = current.state
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < road_map.shape[1] and 0 <= ny < road_map.shape[0] and road_map[ny, nx] == 255:
                    heapq.heappush(open_set, Node((nx, ny), current, current.g + 1, heuristic((nx, ny), goal)))
        return None
    
    def reconstruct_path(self, node):
        path = []
        while node:
            path.append(node.state)
            node = node.parent
        return path[::-1]
    
    def clear_points(self):
        self.start_point = None
        self.end_point = None
        self.route = None
        self.find_route_button.config(state=tk.DISABLED)
        self.display_image = self.original_image.copy()
        self.update_canvas()

if __name__ == "__main__":
    root = tk.Tk()
    app = MapRouteFinder(root)
    root.mainloop()