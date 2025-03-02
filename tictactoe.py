import tkinter as tk
from tkinter import messagebox
import random

class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe - Minimax AI")
        self.root.geometry("1000x1000")
        self.root.configure(bg="#f0f0f0")
        
        self.player = "X"  # Human player
        self.ai = "O"      # AI player
        self.current_player = self.player  # Player goes first by default
        self.board = [""] * 9  # Empty 3x3 board
        self.game_over = False
        
        self.setup_ui()
        
        # If AI goes first, make a move
        if self.current_player == self.ai:
            self.root.after(500, self.ai_move)
    
    def setup_ui(self):
        # Title
        title_label = tk.Label(
            self.root, 
            text="Tic Tac Toe", 
            font=("Arial", 24, "bold"),
            bg="#f0f0f0"
        )
        title_label.pack(pady=20)
        
        # Game status
        self.status_label = tk.Label(
            self.root,
            text=f"Your turn (X)",
            font=("Arial", 14),
            bg="#f0f0f0"
        )
        self.status_label.pack(pady=10)
        
        # Game board frame
        board_frame = tk.Frame(
            self.root,
            bg="#f0f0f0"
        )
        board_frame.pack(pady=20)
        
        # Create the game board buttons
        self.buttons = []
        for i in range(3):
            for j in range(3):
                button = tk.Button(
                    board_frame,
                    text="",
                    font=("Arial", 24, "bold"),
                    width=4,
                    height=2,
                    command=lambda idx=i*3+j: self.make_move(idx)
                )
                button.grid(row=i, column=j, padx=5, pady=5)
                self.buttons.append(button)
        
        # Control buttons
        control_frame = tk.Frame(
            self.root,
            bg="#f0f0f0"
        )
        control_frame.pack(pady=20)
        
        reset_button = tk.Button(
            control_frame,
            text="New Game",
            font=("Arial", 12),
            command=self.reset_game
        )
        reset_button.grid(row=0, column=0, padx=10)
        
        # Toggle first player button
        self.first_player_var = tk.StringVar(value="Player")
        first_player_button = tk.Button(
            control_frame,
            textvariable=self.first_player_var,
            font=("Arial", 12),
            command=self.toggle_first_player
        )
        first_player_button.grid(row=0, column=1, padx=10)
        
        # Difficulty level (primarily adjusts the randomness of AI in non-winning/blocking moves)
        self.difficulty_var = tk.StringVar(value="Hard")
        difficulties = ["Easy", "Medium", "Hard"]
        difficulty_menu = tk.OptionMenu(
            control_frame,
            self.difficulty_var,
            *difficulties
        )
        difficulty_menu.grid(row=0, column=2, padx=10)
        
    def make_move(self, index):
        # Check if the move is valid and the game is not over
        if self.board[index] == "" and not self.game_over:
            # Update the board with the player's move
            self.board[index] = self.current_player
            self.buttons[index].config(
                text=self.current_player,
                fg="#3498db" if self.current_player == self.player else "#e74c3c"
            )
            
            # Check if the game is over
            if self.check_winner():
                self.game_over = True
                self.status_label.config(text=f"Player {self.current_player} wins!")
                self.highlight_winning_combination()
            elif "" not in self.board:
                self.game_over = True
                self.status_label.config(text="It's a tie!")
            else:
                # Switch players
                self.current_player = self.ai if self.current_player == self.player else self.player
                self.status_label.config(text=f"AI's turn (O)" if self.current_player == self.ai else f"Your turn (X)")
                
                # If it's AI's turn, make a move
                if self.current_player == self.ai:
                    self.root.after(500, self.ai_move)
    
    def ai_move(self):
        difficulty = self.difficulty_var.get()
        
        if difficulty == "Easy":
            # Mostly random moves, but occasionally makes smart moves
            if random.random() < 0.3:
                best_score = float("-inf")
                best_move = None
                
                for i in range(9):
                    if self.board[i] == "":
                        self.board[i] = self.ai
                        score = self.minimax(self.board, 0, False)
                        self.board[i] = ""
                        
                        if score > best_score:
                            best_score = score
                            best_move = i
                
                self.make_move(best_move)
            else:
                # Random move
                empty_cells = [i for i in range(9) if self.board[i] == ""]
                if empty_cells:
                    self.make_move(random.choice(empty_cells))
                    
        elif difficulty == "Medium":
            # Blend of random and minimax
            if random.random() < 0.7:
                # Use minimax but with limited depth
                best_score = float("-inf")
                best_move = None
                
                for i in range(9):
                    if self.board[i] == "":
                        self.board[i] = self.ai
                        score = self.minimax(self.board, 0, False, max_depth=2)
                        self.board[i] = ""
                        
                        if score > best_score:
                            best_score = score
                            best_move = i
                
                self.make_move(best_move)
            else:
                # Random move
                empty_cells = [i for i in range(9) if self.board[i] == ""]
                if empty_cells:
                    self.make_move(random.choice(empty_cells))
        else:
            # Hard - Full minimax
            best_score = float("-inf")
            best_move = None
            
            for i in range(9):
                if self.board[i] == "":
                    self.board[i] = self.ai
                    score = self.minimax(self.board, 0, False)
                    self.board[i] = ""
                    
                    if score > best_score:
                        best_score = score
                        best_move = i
            
            self.make_move(best_move)
    
    def minimax(self, board, depth, is_maximizing, max_depth=None):
        # Check if max depth is reached (for easier difficulties)
        if max_depth is not None and depth >= max_depth:
            return 0
            
        # Check terminal states
        if self.check_winner_board(board, self.ai):
            return 10 - depth
        elif self.check_winner_board(board, self.player):
            return depth - 10
        elif "" not in board:
            return 0
        
        if is_maximizing:
            best_score = float("-inf")
            for i in range(9):
                if board[i] == "":
                    board[i] = self.ai
                    score = self.minimax(board, depth + 1, False, max_depth)
                    board[i] = ""
                    best_score = max(score, best_score)
            return best_score
        else:
            best_score = float("inf")
            for i in range(9):
                if board[i] == "":
                    board[i] = self.player
                    score = self.minimax(board, depth + 1, True, max_depth)
                    board[i] = ""
                    best_score = min(score, best_score)
            return best_score
    
    def check_winner(self):
        return self.check_winner_board(self.board, self.current_player)
    
    def check_winner_board(self, board, player):
        # Define winning combinations
        win_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]              # Diagonals
        ]
        
        # Check if any winning combination is satisfied
        for combo in win_combinations:
            if board[combo[0]] == board[combo[1]] == board[combo[2]] == player:
                self.winning_combo = combo  # Store the winning combination
                return True
        
        return False
    
    def highlight_winning_combination(self):
        # Highlight the winning cells
        for idx in self.winning_combo:
            self.buttons[idx].config(bg="#27ae60")
    
    def reset_game(self):
        # Reset game state
        self.board = [""] * 9
        self.game_over = False
        
        # Determine who goes first based on the toggle button
        if self.first_player_var.get() == "Player":
            self.current_player = self.player
        else:
            self.current_player = self.ai
        
        # Reset UI
        for button in self.buttons:
            button.config(text="", bg="SystemButtonFace")
        
        self.status_label.config(text=f"Your turn (X)" if self.current_player == self.player else f"AI's turn (O)")
        
        # If AI goes first, make a move
        if self.current_player == self.ai:
            self.root.after(500, self.ai_move)
    
    def toggle_first_player(self):
        # Toggle between player and AI going first
        if self.first_player_var.get() == "Player":
            self.first_player_var.set("AI")
        else:
            self.first_player_var.set("Player")
        
        # Reset the game with the new first player
        self.reset_game()


if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()