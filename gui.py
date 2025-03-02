import tkinter as tk
import subprocess

class GameSelectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Selection")
        self.root.geometry("1000x1000")
        self.root.configure(bg="#f0f0f0")
        
        self.setup_main_menu()
    
    def setup_main_menu(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Title
        title_label = tk.Label(
            self.root, 
            text="Game Selection", 
            font=("Arial", 24, "bold"),
            bg="#f0f0f0"
        )
        title_label.pack(pady=50) # pady is padding on the y-axis
        
        # Game selection buttons
        button_frame = tk.Frame(self.root, bg="#f0f0f0") # Frame to hold buttons
        button_frame.pack(pady=20)
        
        games = [
            ("Tic Tac Toe", "tictactoe.py", "#3498db"),
            ("Chess", "chess.py", "#2ecc71"),
            ("Maze", "maze.py", "#e74c3c")
        ]
        
        self.buttons = []
        
        for game_name, script, color in games:
            button = tk.Button(
                button_frame,
                text=game_name,
                font=("Arial", 16),
                width=15,
                height=2,
                bg=color,
                fg="white",
                
                command=lambda s=script: self.open_game(s)
            )
            button.pack(pady=10)
            self.buttons.append(button)
        
        # Exit button
        exit_button = tk.Button(
            self.root,
            text="Exit",
            font=("Arial", 12),
            width=10,
            command=self.root.quit
        )
        exit_button.pack(pady=30)
    
    def open_game(self, script_name):
        try:
            subprocess.Popen(["python", script_name])
        except Exception as e:
            print(f"Error opening {script_name}: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GameSelectionApp(root)
    root.mainloop()
