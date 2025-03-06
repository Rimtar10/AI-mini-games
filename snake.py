import pygame
import sys
import random
import time
from collections import deque

# Initialize pygame
pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

# Game settings
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 10

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Search Game")
clock = pygame.time.Clock()

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = (min(color[0] + 50, 255), min(color[1] + 50, 255), min(color[2] + 50, 255))
        self.is_hovered = False
        
    def draw(self):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        font = pygame.font.SysFont(None, 25)
        text = font.render(self.text, True, BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click

class Snake:
    def __init__(self):
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)  # Start moving right
        self.grow = False
        
    def move(self):
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = ((head_x + dx) % GRID_WIDTH, (head_y + dy) % GRID_HEIGHT)
        
        if self.grow:
            self.body = [new_head] + self.body
            self.grow = False
        else:
            self.body = [new_head] + self.body[:-1]
    
    def set_direction(self, direction):
        self.direction = direction
        
    def grow_snake(self):
        self.grow = True
        
    def get_head_position(self):
        return self.body[0]
    
    def draw(self):
        for i, segment in enumerate(self.body):
            x, y = segment
            segment_rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            
            # Head is darker green
            if i == 0:
                pygame.draw.rect(screen, (0, 200, 0), segment_rect)
            else:
                pygame.draw.rect(screen, GREEN, segment_rect)
            pygame.draw.rect(screen, BLACK, segment_rect, 1)

class Food:
    def __init__(self):
        self.position = self.randomize_position()
        
    def randomize_position(self):
        return (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        
    def draw(self):
        x, y = self.position
        food_rect = pygame.Rect(x * GRID_SIZE + GRID_SIZE // 4, y * GRID_SIZE + GRID_SIZE // 4, 
                               GRID_SIZE // 2, GRID_SIZE // 2)
        pygame.draw.ellipse(screen, RED, food_rect)

def find_path(snake, food):
    """Find the shortest path from snake head to food using BFS"""
    start = snake.get_head_position()
    end = food.position
    
    # BFS queue
    queue = deque([(start, [])])
    visited = set([start])
    
    while queue:
        current, path = queue.popleft()
        
        if current == end:
            return path
        
        x, y = current
        
        # Try all four directions
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            next_pos = ((x + dx) % GRID_WIDTH, (y + dy) % GRID_HEIGHT)
            
            if next_pos not in visited:
                visited.add(next_pos)
                new_path = path + [(dx, dy)]
                queue.append((next_pos, new_path))
    
    # If no path is found (shouldn't happen with wrap-around)
    return []

def draw_grid():
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

def main():
    snake = Snake()
    food = Food()
    current_path = []
    
    # Create stop button
    stop_button = Button(WIDTH - 100, 10, 90, 30, "Stop Game", (255, 100, 100))
    
    game_active = True
    auto_mode = False
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            mouse_pos = pygame.mouse.get_pos()
            mouse_clicked = pygame.mouse.get_pressed()[0]
            
            stop_button.check_hover(mouse_pos)
            if stop_button.is_clicked(mouse_pos, mouse_clicked):
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_active:
                    # Generate new food and calculate path
                    food = Food()
                    current_path = find_path(snake, food)
                    auto_mode = True
        
        if game_active and auto_mode:
            # If we have a path, follow it
            if current_path:
                snake.set_direction(current_path[0])
                current_path = current_path[1:]
            
            # Move snake
            snake.move()
            
            # Check if snake reached food
            if snake.get_head_position() == food.position:
                snake.grow_snake()
                food = Food()
                current_path = find_path(snake, food)
            
            # If path is empty, recalculate
            if not current_path:
                current_path = find_path(snake, food)
        
        # Drawing
        screen.fill(WHITE)
        draw_grid()
        
        food.draw()
        snake.draw()
        stop_button.draw()
        
        # Display instructions
        font = pygame.font.SysFont(None, 24)
        instructions = font.render("Press SPACE to start the game", True, BLACK)
        screen.blit(instructions, (10, 10))
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()