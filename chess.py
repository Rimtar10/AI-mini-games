import tkinter as tk
from tkinter import messagebox, simpledialog
import copy
import heapq
import time

class ChessGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess - A* Search Algorithm")
        self.root.geometry("1000x1000")
        self.root.configure(bg="#f0f0f0")
        
        # Piece values for evaluation
        self.piece_values = {
            'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 100,  # White pieces
            'p': -1, 'n': -3, 'b': -3, 'r': -5, 'q': -9, 'k': -100  # Black pieces
        }
        
        # Initialize the chess board
        self.initialize_board()
        
        # Game state variables
        self.selected_piece = None
        self.current_player = 'white'  # White goes first
        self.white_king_pos = (7, 4)   # Initial position of white king
        self.black_king_pos = (0, 4)   # Initial position of black king
        self.ai_thinking = False
        self.white_in_check = False
        self.black_in_check = False
        self.game_over = False
        
        # Setup the UI
        self.setup_ui()
        
    def initialize_board(self):
        # Create the initial chess board state
        # Board is represented as a 2D array where each cell contains a piece or empty space
        # Uppercase letters are white pieces, lowercase are black pieces
        self.board = [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],  # Black back row
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],  # Black pawns
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],  # Empty row
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],  # Empty row
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],  # Empty row
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],  # Empty row
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],  # White pawns
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']   # White back row
        ]
        
    def setup_ui(self):
        # Title and status frame
        top_frame = tk.Frame(self.root, bg="#f0f0f0")
        top_frame.pack(pady=10)
        
        title_label = tk.Label(
            top_frame, 
            text="Chess Game", 
            font=("Arial", 24, "bold"),
            bg="#f0f0f0"
        )
        title_label.pack()
        
        # Status label
        self.status_label = tk.Label(
            top_frame,
            text="White's turn",
            font=("Arial", 14),
            bg="#f0f0f0"
        )
        self.status_label.pack(pady=5)
        
        # Chess board frame
        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack(pady=10)
        
        # Create the chess board squares and pieces
        self.squares = [[None for _ in range(8)] for _ in range(8)]
        self.piece_labels = [[None for _ in range(8)] for _ in range(8)]
        
        # Create board squares
        for row in range(8):
            for col in range(8):
                color = "#f0d9b5" if (row + col) % 2 == 0 else "#b58863"
                square = tk.Frame(
                    self.board_frame,
                    width=60,
                    height=60,
                    bg=color
                )
                square.grid(row=row, column=col)
                square.bind("<Button-1>", lambda event, r=row, c=col: self.square_click(r, c))
                
                # Make sure the frame maintains its size
                square.grid_propagate(False)
                self.squares[row][col] = square
                
                # Add piece labels (initially empty)
                piece_label = tk.Label(
                    square,
                    font=("Arial", 24),
                    bg=color
                )
                piece_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
                self.piece_labels[row][col] = piece_label
        
        # Update the board display with initial pieces
        self.update_board_display()
        
        # Control frame
        control_frame = tk.Frame(self.root, bg="#f0f0f0")
        control_frame.pack(pady=10)
        
        # New game button
        new_game_button = tk.Button(
            control_frame,
            text="New Game",
            font=("Arial", 12),
            command=self.reset_game
        )
        new_game_button.grid(row=0, column=0, padx=10)
        
        # Suggest move button using A* algorithm
        suggest_move_button = tk.Button(
            control_frame,
            text="Suggest Move",
            font=("Arial", 12),
            command=self.suggest_move
        )
        suggest_move_button.grid(row=0, column=1, padx=10)
        
        # AI move button
        ai_move_button = tk.Button(
            control_frame,
            text="AI Move",
            font=("Arial", 12),
            command=self.make_ai_move
        )
        ai_move_button.grid(row=0, column=2, padx=10)
        
        # Display search info
        self.info_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.info_frame.pack(pady=10, fill=tk.X, padx=20)
        
        self.search_info = tk.Text(self.info_frame, height=4, width=80, font=("Arial", 10))
        self.search_info.pack()
        
    def update_board_display(self):
        # Update the board display with current piece positions
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                # Convert piece letter to Unicode chess symbol
                symbol = self.get_piece_symbol(piece)
                
                # Update the label with the piece symbol
                self.piece_labels[row][col].config(text=symbol)
                
                # Color the piece appropriately
                if piece.isupper():  # White piece
                    self.piece_labels[row][col].config(fg="#ffffff")
                elif piece.islower():  # Black piece
                    self.piece_labels[row][col].config(fg="#000000")
                
                # Reset background colors
                color = "#f0d9b5" if (row + col) % 2 == 0 else "#b58863"
                self.squares[row][col].config(bg=color)
                self.piece_labels[row][col].config(bg=color)
        
        # Highlight the selected piece if any
        if self.selected_piece:
            row, col = self.selected_piece
            self.squares[row][col].config(bg="#aaf7aa")
            self.piece_labels[row][col].config(bg="#aaf7aa")
        
        # Highlight kings in check
        if self.white_in_check:
            row, col = self.white_king_pos
            self.squares[row][col].config(bg="#ff6b6b")
            self.piece_labels[row][col].config(bg="#ff6b6b")
        
        if self.black_in_check:
            row, col = self.black_king_pos
            self.squares[row][col].config(bg="#ff6b6b")
            self.piece_labels[row][col].config(bg="#ff6b6b")
            
    def get_piece_symbol(self, piece):
        # Convert piece letter to Unicode chess symbol
        symbols = {
            'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',  # White pieces
            'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟',  # Black pieces
            ' ': ''   # Empty space
        }
        return symbols.get(piece, '')
        
    def square_click(self, row, col):
        if self.game_over or self.ai_thinking:
            return
            
        piece = self.board[row][col]
        
        # If no piece is selected yet
        if self.selected_piece is None:
            # Check if the clicked square has a piece and it belongs to the current player
            if piece != ' ' and ((piece.isupper() and self.current_player == 'white') or 
                                 (piece.islower() and self.current_player == 'black')):
                self.selected_piece = (row, col)
                self.update_board_display()
                
                # Show possible moves
                self.highlight_possible_moves(row, col)
        else:
            # If a piece is already selected
            prev_row, prev_col = self.selected_piece
            
            # If clicking on the same piece, deselect it
            if row == prev_row and col == prev_col:
                self.selected_piece = None
                self.update_board_display()
                return
                
            # If clicking on another piece of the same color, select that piece instead
            if piece != ' ' and ((piece.isupper() and self.current_player == 'white') or 
                               (piece.islower() and self.current_player == 'black')):
                self.selected_piece = (row, col)
                self.update_board_display()
                
                # Show possible moves
                self.highlight_possible_moves(row, col)
                return
                
            # Try to move the selected piece to the clicked square
            if self.is_valid_move(prev_row, prev_col, row, col):
                self.move_piece(prev_row, prev_col, row, col)
                self.selected_piece = None
                
                # Switch players
                self.current_player = 'black' if self.current_player == 'white' else 'white'
                self.status_label.config(text=f"{self.current_player.capitalize()}'s turn")
                
                # Check for check and checkmate
                self.check_for_check()
                if self.is_checkmate():
                    winner = 'White' if self.current_player == 'black' else 'Black'
                    messagebox.showinfo("Checkmate", f"{winner} wins!")
                    self.game_over = True
                    self.status_label.config(text=f"Game Over - {winner} wins!")
                    
                self.update_board_display()
            else:
                # Invalid move, keep the piece selected
                pass
                
    def highlight_possible_moves(self, row, col):
        # Highlight squares for possible valid moves
        piece = self.board[row][col]
        for r in range(8):
            for c in range(8):
                if self.is_valid_move(row, col, r, c):
                    if self.board[r][c] == ' ':
                        # Empty square - light highlight
                        self.squares[r][c].config(bg="#aaf7aa")
                        self.piece_labels[r][c].config(bg="#aaf7aa")
                    else:
                        # Capture - stronger highlight
                        self.squares[r][c].config(bg="#ff9999")
                        self.piece_labels[r][c].config(bg="#ff9999")
                        
    def is_valid_move(self, from_row, from_col, to_row, to_col):
        # Check if a move is valid
        piece = self.board[from_row][from_col]
        target = self.board[to_row][to_col]
        
        # Can't move to a square with your own piece
        if ((piece.isupper() and target.isupper()) or 
            (piece.islower() and target.islower())):
            return False
            
        # Get piece type (lowercase for both colors)
        piece_type = piece.lower()
        
        # Implement chess rules for each piece type
        valid = False
        
        if piece_type == 'p':  # Pawn
            valid = self.is_valid_pawn_move(piece, from_row, from_col, to_row, to_col)
        elif piece_type == 'r':  # Rook
            valid = self.is_valid_rook_move(from_row, from_col, to_row, to_col)
        elif piece_type == 'n':  # Knight
            valid = self.is_valid_knight_move(from_row, from_col, to_row, to_col)
        elif piece_type == 'b':  # Bishop
            valid = self.is_valid_bishop_move(from_row, from_col, to_row, to_col)
        elif piece_type == 'q':  # Queen
            valid = (self.is_valid_rook_move(from_row, from_col, to_row, to_col) or 
                    self.is_valid_bishop_move(from_row, from_col, to_row, to_col))
        elif piece_type == 'k':  # King
            valid = self.is_valid_king_move(from_row, from_col, to_row, to_col)
        
        # Check if the move would put/leave the player's king in check
        if valid:
            # Make a copy of the board to simulate the move
            board_copy = copy.deepcopy(self.board)
            board_copy[to_row][to_col] = board_copy[from_row][from_col]
            board_copy[from_row][from_col] = ' '
            
            # Update king position if the king is being moved
            king_pos = None
            if piece.upper() == 'K':
                if piece.isupper():  # White king
                    king_pos = (to_row, to_col)
                else:  # Black king
                    king_pos = (to_row, to_col)
            else:
                # Use the current king positions
                if piece.isupper():  # White piece
                    king_pos = self.white_king_pos
                else:  # Black piece
                    king_pos = self.black_king_pos
            
            # Check if the king would be in check after the move
            if self.is_square_under_attack(board_copy, king_pos[0], king_pos[1], piece.isupper()):
                return False
        
        return valid
        
    def is_valid_pawn_move(self, piece, from_row, from_col, to_row, to_col):
        # Determine direction of movement (up for white, down for black)
        direction = -1 if piece.isupper() else 1
        
        # Forward movement
        if from_col == to_col:
            # One square forward
            if to_row == from_row + direction and self.board[to_row][to_col] == ' ':
                return True
                
            # Two squares forward from starting position
            if ((from_row == 6 and piece.isupper() and to_row == 4) or 
                (from_row == 1 and piece.islower() and to_row == 3)):
                # Check if spaces are empty
                if (self.board[from_row + direction][from_col] == ' ' and 
                    self.board[to_row][to_col] == ' '):
                    return True
        
        # Diagonal capture
        elif (to_row == from_row + direction and 
              (to_col == from_col - 1 or to_col == from_col + 1)):
            # Check if there is an opponent's piece to capture
            target = self.board[to_row][to_col]
            if ((piece.isupper() and target.islower() and target != ' ') or 
                (piece.islower() and target.isupper() and target != ' ')):
                return True
                
        return False
        
    def is_valid_rook_move(self, from_row, from_col, to_row, to_col):
        # Rook moves in straight lines (horizontally or vertically)
        if from_row != to_row and from_col != to_col:
            return False
            
        # Check if the path is clear
        row_step = 0 if from_row == to_row else (1 if from_row < to_row else -1)
        col_step = 0 if from_col == to_col else (1 if from_col < to_col else -1)
        
        r, c = from_row + row_step, from_col + col_step
        while r != to_row or c != to_col:
            if self.board[r][c] != ' ':
                return False
            r += row_step
            c += col_step
            
        return True
        
    def is_valid_knight_move(self, from_row, from_col, to_row, to_col):
        # Knight moves in an L-shape
        row_diff = abs(from_row - to_row)
        col_diff = abs(from_col - to_col)
        
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)
        
    def is_valid_bishop_move(self, from_row, from_col, to_row, to_col):
        # Bishop moves diagonally
        row_diff = abs(from_row - to_row)
        col_diff = abs(from_col - to_col)
        
        if row_diff != col_diff:
            return False
            
        # Check if the path is clear
        row_step = 1 if from_row < to_row else -1
        col_step = 1 if from_col < to_col else -1
        
        r, c = from_row + row_step, from_col + col_step
        while r != to_row and c != to_col:
            if self.board[r][c] != ' ':
                return False
            r += row_step
            c += col_step
            
        return True
        
    def is_valid_king_move(self, from_row, from_col, to_row, to_col):
        # King moves one square in any direction
        row_diff = abs(from_row - to_row)
        col_diff = abs(from_col - to_col)
        
        return row_diff <= 1 and col_diff <= 1
        
    def move_piece(self, from_row, from_col, to_row, to_col):
        piece = self.board[from_row][from_col]
        
        # Update king positions if king is moved
        if piece == 'K':
            self.white_king_pos = (to_row, to_col)
        elif piece == 'k':
            self.black_king_pos = (to_row, to_col)
            
        # Move the piece
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = ' '
        
        # Handle pawn promotion (simplified - always promotes to queen)
        if piece == 'P' and to_row == 0:
            self.board[to_row][to_col] = 'Q'
        elif piece == 'p' and to_row == 7:
            self.board[to_row][to_col] = 'q'
            
    def is_square_under_attack(self, board, row, col, is_white):
        # Check if a square is under attack by any enemy pieces
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                # Skip empty squares and own pieces
                if piece == ' ' or (is_white and piece.isupper()) or (not is_white and piece.islower()):
                    continue
                    
                # Check if this enemy piece can attack the given square
                piece_type = piece.lower()
                
                if piece_type == 'p':
                    # Pawns attack diagonally
                    direction = -1 if piece.isupper() else 1
                    if ((r + direction == row) and 
                        (c - 1 == col or c + 1 == col)):
                        return True
                        
                elif piece_type == 'r':
                    if self.is_valid_rook_move(r, c, row, col):
                        return True
                        
                elif piece_type == 'n':
                    if self.is_valid_knight_move(r, c, row, col):
                        return True
                        
                elif piece_type == 'b':
                    if self.is_valid_bishop_move(r, c, row, col):
                        return True
                        
                elif piece_type == 'q':
                    if (self.is_valid_rook_move(r, c, row, col) or 
                        self.is_valid_bishop_move(r, c, row, col)):
                        return True
                        
                elif piece_type == 'k':
                    if self.is_valid_king_move(r, c, row, col):
                        return True
                        
        return False
    
    def check_for_check(self):
        # Check if either king is in check
        self.white_in_check = self.is_square_under_attack(
            self.board, self.white_king_pos[0], self.white_king_pos[1], True
        )
        self.black_in_check = self.is_square_under_attack(
            self.board, self.black_king_pos[0], self.black_king_pos[1], False
        )
        
    def is_checkmate(self):
        # Check if the current player is in checkmate
        is_white = self.current_player == 'white'
        
        # If not in check, it's not checkmate
        if (is_white and not self.white_in_check) or (not is_white and not self.black_in_check):
            return False
            
        # Try all possible moves for all pieces of current player
        for r1 in range(8):
            for c1 in range(8):
                piece = self.board[r1][c1]
                
                # Skip empty squares and opponent's pieces
                if piece == ' ' or (is_white and piece.islower()) or (not is_white and piece.isupper()):
                    continue
                    
                # Try moving this piece to every square
                for r2 in range(8):
                    for c2 in range(8):
                        if self.is_valid_move(r1, c1, r2, c2):
                            # There's at least one valid move, so it's not checkmate
                            return False
                            
        # No valid moves and king is in check -> checkmate
        return True
        
    def reset_game(self):
        # Reset the game to initial state
        self.initialize_board()
        self.selected_piece = None
        self.current_player = 'white'
        self.white_king_pos = (7, 4)
        self.black_king_pos = (0, 4)
        self.white_in_check = False
        self.black_in_check = False
        self.game_over = False
        
        self.status_label.config(text="White's turn")
        self.search_info.delete(1.0, tk.END)
        self.update_board_display()
        
    # A* ALGORITHM IMPLEMENTATION
    
    def heuristic(self, board, is_white):
        # Heuristic function for A* search
        # Evaluates board position based on piece values and positional factors
        score = 0
        
        # Material value
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece != ' ':
                    score += self.piece_values.get(piece, 0)
        
        # Positional evaluation (simplified)
        # Center control
        center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        for row, col in center_squares:
            piece = board[row][col]
            if piece != ' ':
                if (piece.isupper() and is_white) or (piece.islower() and not is_white):
                    score += 0.5  # Bonus for controlling center with own pieces
                else:
                    score -= 0.5  # Penalty if opponent controls center
                    
        # King safety - simplified, just checks number of pieces around king
        king_pos = self.white_king_pos if is_white else self.black_king_pos
        kr, kc = king_pos
        
        # King safety bonus/penalty based on surrounding pieces
        for r in range(max(0, kr-1), min(8, kr+2)):
            for c in range(max(0, kc-1), min(8, kc+2)):
                if (r, c) != king_pos:
                    piece = board[r][c]
                    if piece != ' ':
                        if (piece.isupper() and is_white) or (piece.islower() and not is_white):
                            score += 0.2  # Friendly piece near king
                        else:
                            score -= 0.5  # Enemy piece near king
        
        # Return positive score for white, negative for black
        return score if is_white else -score
    
    def get_all_valid_moves(self, board, is_white):
        # Get all valid moves for a player
        moves = []
        
        for r1 in range(8):
            for c1 in range(8):
                piece = board[r1][c1]
                
                # Skip empty squares and opponent's pieces
                if piece == ' ' or (is_white and piece.islower()) or (not is_white and piece.isupper()):
                    continue
                    
                # Try moving this piece to every square
                for r2 in range(8):
                    for c2 in range(8):
                        # Check using the rules we've already defined
                        from_row, from_col = r1, c1
                        to_row, to_col = r2, c2
                        
                        # Skip if it's the same square
                        if from_row == to_row and from_col == to_col:
                            continue
                            
                        piece = board[from_row][from_col]
                        target = board[to_row][to_col]
                        
                        # Can't move to a square with your own piece
                        if ((piece.isupper() and target.isupper()) or 
                            (piece.islower() and target.islower())):
                            continue
                            
                        # Get piece type (lowercase for both colors)
                        piece_type = piece.lower()
                        
                        # Check validity based on piece type
                        valid = False
                        
                        if piece_type == 'p':  # Pawn
                            valid = self.check_pawn_move(board, piece, from_row, from_col, to_row, to_col)
                        elif piece_type == 'r':  # Rook
                            valid = self.check_rook_move(board, from_row, from_col, to_row, to_col)
                        elif piece_type == 'n':  # Knight
                            valid = self.check_knight_move(from_row, from_col, to_row, to_col)
                        elif piece_type == 'b':  # Bishop
                            valid = self.check_bishop_move(board, from_row, from_col, to_row, to_col)
                        elif piece_type == 'q':  # Queen
                            valid = (self.check_rook_move(board, from_row, from_col, to_row, to_col) or 
                                    self.check_bishop_move(board, from_row, from_col, to_row, to_col))
                        elif piece_type == 'k':  # King
                            valid = self.check_king_move(from_row, from_col, to_row, to_col)
                        
                        if valid:
                            # Make a copy of the board to simulate the move
                            board_copy = copy.deepcopy(board)
                            board_copy[to_row][to_col] = board_copy[from_row][from_col]
                            board_copy[from_row][from_col] = ' '
                            
                            # Update king position if the king is being moved
                            king_pos = None
                            white_king = self.white_king_pos
                            black_king = self.black_king_pos
                            
                            if piece.upper() == 'K':
                                if piece.isupper():  # White king
                                    white_king = (to_row, to_col)
                                else:  # Black king
                                    black_king = (to_row, to_col)
                            
                            # Check if the king would be in check after the move
                            king_pos = white_king if is_white else black_king
                            if not self.check_square_under_attack(board_copy, king_pos[0], king_pos[1], is_white):
                                moves.append(((from_row, from_col), (to_row, to_col)))
        
        return moves
    
    # Simplified versions of move checking for A* search
    
    def check_pawn_move(self, board, piece, from_row, from_col, to_row, to_col):
        # Direction of movement (up for white, down for black)
        direction = -1 if piece.isupper() else 1
        
        # Forward movement
        if from_col == to_col:
            # One square forward
            if to_row == from_row + direction and board[to_row][to_col] == ' ':
                return True
                
            # Two squares forward from starting position
            if ((from_row == 6 and piece.isupper() and to_row == 4) or 
                (from_row == 1 and piece.islower() and to_row == 3)):
                # Check if spaces are empty
                if (board[from_row + direction][from_col] == ' ' and 
                    board[to_row][to_col] == ' '):
                    return True
        
        # Diagonal capture
        elif (to_row == from_row + direction and 
              (to_col == from_col - 1 or to_col == from_col + 1)):
            # Check if there is an opponent's piece to capture
            target = board[to_row][to_col]
            if ((piece.isupper() and target.islower() and target != ' ') or 
                (piece.islower() and target.isupper() and target != ' ')):
                return True
                
        return False
    
    def check_rook_move(self, board, from_row, from_col, to_row, to_col):
    # Rook moves in straight lines (horizontally or vertically)
        if from_row != to_row and from_col != to_col:
            return False
        
        # Check if the path is clear
        row_step = 0 if from_row == to_row else (1 if from_row < to_row else -1)
        col_step = 0 if from_col == to_col else (1 if from_col < to_col else -1)
    
        r, c = from_row + row_step, from_col + col_step
        while r != to_row or c != to_col:
            if board[r][c] != ' ':
                return False
            r += row_step
            c += col_step
        
        return True
    
    def check_knight_move(self, from_row, from_col, to_row, to_col):
        # Knight moves in an L-shape
        row_diff = abs(from_row - to_row)
        col_diff = abs(from_col - to_col)
    
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)
    
    def check_bishop_move(self, board, from_row, from_col, to_row, to_col):
    # Bishop moves diagonally
        row_diff = abs(from_row - to_row)
        col_diff = abs(from_col - to_col)
    
        if row_diff != col_diff:
            return False
        
    # Check if the path is clear
        row_step = 1 if from_row < to_row else -1
        col_step = 1 if from_col < to_col else -1
    
        r, c = from_row + row_step, from_col + col_step
        while r != to_row and c != to_col:
            if board[r][c] != ' ':
                return False
            r += row_step
            c += col_step
        
        return True
    
    def check_king_move(self, from_row, from_col, to_row, to_col):
    # King moves one square in any direction
        row_diff = abs(from_row - to_row)
        col_diff = abs(from_col - to_col)
    
        return row_diff <= 1 and col_diff <= 1
    
    def check_square_under_attack(self, board, row, col, is_white):
    # Check if a square is under attack by any enemy pieces
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
            # Skip empty squares and own pieces
                if piece == ' ' or (is_white and piece.isupper()) or (not is_white and piece.islower()):
                    continue
                
            # Check if this enemy piece can attack the given square
                piece_type = piece.lower()
            
                if piece_type == 'p':
                # Pawns attack diagonally
                    direction = -1 if piece.isupper() else 1
                    if ((r + direction == row) and 
                        (c - 1 == col or c + 1 == col)):
                        return True
                    
                elif piece_type == 'r':
                    if self.check_rook_move(board, r, c, row, col):
                        return True
                    
                elif piece_type == 'n':
                    if self.check_knight_move(r, c, row, col):
                        return True
                    
                elif piece_type == 'b':
                    if self.check_bishop_move(board, r, c, row, col):
                        return True
                    
                elif piece_type == 'q':
                    if (self.check_rook_move(board, r, c, row, col) or 
                        self.check_bishop_move(board, r, c, row, col)):
                        return True
                    
                elif piece_type == 'k':
                    if self.check_king_move(r, c, row, col):
                        return True
                    
        return False

    def a_star_search(self, max_depth=3):
    # A* search for the best move
        start_time = time.time()
        start_board = copy.deepcopy(self.board)
        is_white = self.current_player == 'white'
    
        # Track search statistics
        nodes_explored = 0
        max_queue_size = 0
    
    # Define goal state (evaluation function)
        def goal_test(board, depth):
            return depth >= max_depth
    
        # priority queue for A* search
        # Each item: (priority, (board, depth, move_sequence))
        # Lower priority values are explored first
        queue = []
        initial_state = (start_board, 0, [])  # (board, depth, move_sequence)
        initial_priority = -self.heuristic(start_board, is_white)  # Negate for min-heap priority
        heapq.heappush(queue, (initial_priority, initial_state))
    
        best_move = None
        best_score = float('-inf') if is_white else float('inf')
    
    # Keep track of visited states to avoid cycles
        visited = set()
    
        while queue and time.time() - start_time < 5:  # 5-second time limit
            nodes_explored += 1
            max_queue_size = max(max_queue_size, len(queue))
        
        # Get the board state with the best priority
            priority, (board, depth, move_sequence) = heapq.heappop(queue)
        
        # Convert board to a hashable representation for visited set
            board_hash = tuple(tuple(row) for row in board)
            if board_hash in visited:
                continue
            visited.add(board_hash)
        
        # If we've reached max depth, evaluate the position
            if goal_test(board, depth):
                score = self.heuristic(board, is_white)
                if (is_white and score > best_score) or (not is_white and score < best_score):
                    best_score = score
                    if move_sequence:
                        best_move = move_sequence[0]  # The first move in the sequence
                continue
        
        # Generate all possible moves for the current player
            current_is_white = is_white if depth % 2 == 0 else not is_white
            moves = self.get_all_valid_moves(board, current_is_white)
        
            for move in moves:
            # Apply the move to get a new board state
                new_board = copy.deepcopy(board)
                from_pos, to_pos = move
                from_row, from_col = from_pos
                to_row, to_col = to_pos
            
            # Move the piece
                new_board[to_row][to_col] = new_board[from_row][from_col]
                new_board[from_row][from_col] = ' '
            
            # Handle pawn promotion (simplified - always promotes to queen)
                if new_board[to_row][to_col] == 'P' and to_row == 0:
                    new_board[to_row][to_col] = 'Q'
                elif new_board[to_row][to_col] == 'p' and to_row == 7:
                    new_board[to_row][to_col] = 'q'
            
            # Create new move sequence
                new_move_sequence = move_sequence.copy()
                if not new_move_sequence:
                    new_move_sequence.append(move)
            
            # Calculate the priority (lower is better)
            # The priority is based on depth and the board evaluation
                h_value = self.heuristic(new_board, is_white)
            # For opponent's turn, we want to minimize their advantage
                if depth % 2 == 1:
                    h_value = -h_value
            
            # f(n) = g(n) + h(n), where g(n) is depth cost
                priority = depth + 1 - h_value
            
            # Add to queue
                next_state = (new_board, depth + 1, new_move_sequence)
                heapq.heappush(queue, (priority, next_state))
    
    # Report search statistics
        end_time = time.time()
        search_time = end_time - start_time
    
        self.search_info.delete(1.0, tk.END)
        self.search_info.insert(tk.END, f"A* Search Stats:\n")
        self.search_info.insert(tk.END, f"Nodes explored: {nodes_explored}\n")
        self.search_info.insert(tk.END, f"Max queue size: {max_queue_size}\n")
        self.search_info.insert(tk.END, f"Search time: {search_time:.3f} seconds\n")
    
        return best_move

    def suggest_move(self):
        if self.game_over:
            messagebox.showinfo("Game Over", "The game has ended. Start a new game to continue.")
            return
        
    # Use A* search to find a good move
        best_move = self.a_star_search()
    
        if best_move:
            from_pos, to_pos = best_move
            from_row, from_col = from_pos
            to_row, to_col = to_pos
        
        # Highlight the suggested move
            self.squares[from_row][from_col].config(bg="#aaf7aa")
            self.piece_labels[from_row][from_col].config(bg="#aaf7aa")
            self.squares[to_row][to_col].config(bg="#ffcc00")
            self.piece_labels[to_row][to_col].config(bg="#ffcc00")
        
            messagebox.showinfo("Suggested Move", 
                            f"Suggested move: {from_row},{from_col} to {to_row},{to_col}")
        else:
            messagebox.showinfo("No Move", "Could not find a good move.")

    def make_ai_move(self):
        if self.game_over or self.ai_thinking:
            return
        
        if self.current_player == 'black':  # AI plays as black
            self.ai_thinking = True
            self.status_label.config(text="AI thinking...")
            self.root.update()
        
        # Use A* search to find a good move
            best_move = self.a_star_search()
        
            if best_move:
                from_pos, to_pos = best_move
                from_row, from_col = from_pos
                to_row, to_col = to_pos
            
            # Make the move
                self.move_piece(from_row, from_col, to_row, to_col)
            
            # Switch to player's turn
                self.current_player = 'white'
                self.status_label.config(text="White's turn")
            
            # Check for check and checkmate
                self.check_for_check()
                if self.is_checkmate():
                    messagebox.showinfo("Checkmate", "Black wins!")
                    self.game_over = True
                    self.status_label.config(text="Game Over - Black wins!")
            else:
                messagebox.showinfo("AI Move", "AI could not find a valid move.")
            
            self.update_board_display()
            self.ai_thinking = False
        else:
            messagebox.showinfo("Player's Turn", "It's your turn (White). AI plays as Black.")

def main():
    root = tk.Tk()
    game = ChessGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()