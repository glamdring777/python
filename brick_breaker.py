import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 875
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)

# Paddle settings
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 10
PADDLE_SPEED = 8

# Ball settings
BALL_SIZE = 10
BALL_SPEED_X = 5
BALL_SPEED_Y = -5

# Brick settings
BRICK_WIDTH = 75
BRICK_HEIGHT = 30
BRICK_ROWS = 5
BRICK_COLS = 10

# Power-up settings
POWERUP_SIZE = 20
POWERUP_SPEED = 3

class Particle:
    """Individual particle for special effects"""
    def __init__(self, x, y, color, velocity_x=None, velocity_y=None, life=60):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.velocity_x = velocity_x if velocity_x else random.uniform(-3, 3)
        self.velocity_y = velocity_y if velocity_y else random.uniform(-3, 3)
        self.life = life
        self.max_life = life
        self.size = random.uniform(2, 5)
    
    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += 0.1  # Gravity
        self.life -= 1
        return self.life > 0
    
    def draw(self, screen):
        if self.life > 0:
            # Fade out as particle dies
            alpha = int(255 * (self.life / self.max_life))
            current_size = max(1, int(self.size * (self.life / self.max_life)))
            
            # Create fading particle
            particle_surface = pygame.Surface((current_size * 2, current_size * 2))
            particle_surface.set_alpha(alpha)
            particle_surface.fill(self.color)
            screen.blit(particle_surface, (int(self.x - current_size), int(self.y - current_size)))

class ParticleSystem:
    """Manages all particle effects"""
    def __init__(self):
        self.particles = []
    
    def add_explosion(self, x, y, color, count=20):
        """Create explosion effect"""
        for _ in range(count):
            velocity_x = random.uniform(-8, 8)
            velocity_y = random.uniform(-8, 8)
            life = random.randint(30, 90)
            self.particles.append(Particle(x, y, color, velocity_x, velocity_y, life))
    
    def add_sparkle(self, x, y, color, count=5):
        """Create sparkle effect"""
        for _ in range(count):
            velocity_x = random.uniform(-2, 2)
            velocity_y = random.uniform(-2, 2)
            life = random.randint(20, 40)
            self.particles.append(Particle(x, y, color, velocity_x, velocity_y, life))
    
    def add_trail(self, x, y, color):
        """Create trailing particle"""
        velocity_x = random.uniform(-1, 1)
        velocity_y = random.uniform(-1, 1)
        self.particles.append(Particle(x, y, color, velocity_x, velocity_y, 30))
    
    def update(self):
        # Update all particles and remove dead ones
        self.particles = [p for p in self.particles if p.update()]
    
    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)

class SoundManager:
    """Handles all game sounds"""
    def __init__(self):
        self.sound_enabled = True
        try:
            # Try to create sounds - if it fails, disable sound
            self.paddle_hit_sound = self.create_beep(440, 0.1)
            self.brick_hit_sound = self.create_beep(880, 0.1)
            self.powerup_sound = self.create_beep(660, 0.2)
            self.game_over_sound = self.create_beep(220, 0.5)
            self.level_complete_sound = self.create_beep(1320, 0.3)
            self.boss_hit_sound = self.create_beep(330, 0.2)
            self.boss_defeat_sound = self.create_beep(1760, 0.5)
            self.fireball_sound = self.create_beep(800, 0.15)
            print("Sound system initialized successfully!")
        except:
            # If sound creation fails, disable sound system
            self.sound_enabled = False
            print("Sound system disabled (NumPy not available - install with: pip install numpy)")
            # Create dummy sound objects
            self.paddle_hit_sound = None
            self.brick_hit_sound = None
            self.powerup_sound = None
            self.game_over_sound = None
            self.level_complete_sound = None
            self.boss_hit_sound = None
            self.boss_defeat_sound = None
            self.fireball_sound = None
    
    def create_beep(self, frequency, duration):
        try:
            import numpy as np
            sample_rate = 22050
            frames = int(duration * sample_rate)
            
            # Create sine wave using numpy
            t = np.linspace(0, duration, frames, False)
            wave = np.sin(frequency * 2 * np.pi * t) * 4096
            
            # Convert to stereo and ensure C-contiguous array
            stereo_wave = np.array([wave, wave]).T
            stereo_wave = np.ascontiguousarray(stereo_wave.astype(np.int16))
            
            sound = pygame.sndarray.make_sound(stereo_wave)
            return sound
        except ImportError:
            # Fallback: Create silent sound
            return pygame.mixer.Sound(buffer=bytes(1024))
        except Exception as e:
            print(f"Sound creation failed: {e}")
            return pygame.mixer.Sound(buffer=bytes(1024))
    
    def play_paddle_hit(self):
        if self.sound_enabled and self.paddle_hit_sound:
            self.paddle_hit_sound.play()
    
    def play_brick_hit(self):
        if self.sound_enabled and self.brick_hit_sound:
            self.brick_hit_sound.play()
    
    def play_powerup(self):
        if self.sound_enabled and self.powerup_sound:
            self.powerup_sound.play()
    
    def play_game_over(self):
        if self.sound_enabled and self.game_over_sound:
            self.game_over_sound.play()
    
    def play_level_complete(self):
        if self.sound_enabled and self.level_complete_sound:
            self.level_complete_sound.play()
    
    def play_boss_hit(self):
        if self.sound_enabled and self.boss_hit_sound:
            self.boss_hit_sound.play()
    
    def play_boss_defeat(self):
        if self.sound_enabled and self.boss_defeat_sound:
            self.boss_defeat_sound.play()
    
    def play_fireball(self):
        if self.sound_enabled and self.fireball_sound:
            self.fireball_sound.play()

class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.normal_width = PADDLE_WIDTH
        self.wide_width = PADDLE_WIDTH * 1.5
        self.narrow_width = PADDLE_WIDTH * 0.7
        self.powerup_timer = 0
        self.current_powerup = None
        self.shield_timer = 0  # Shield power-up
    
    def move(self, direction):
        if direction == "left" and self.rect.left > 0:
            self.rect.x -= PADDLE_SPEED
        elif direction == "right" and self.rect.right < SCREEN_WIDTH:
            self.rect.x += PADDLE_SPEED
    
    def apply_powerup(self, powerup_type):
        if powerup_type == "shield":
            self.shield_timer = 600  # 10 seconds
        else:
            self.current_powerup = powerup_type
            self.powerup_timer = 300
            
            old_center = self.rect.centerx
            if powerup_type == "wide_paddle":
                self.rect.width = self.wide_width
            elif powerup_type == "narrow_paddle":
                self.rect.width = self.narrow_width
            self.rect.centerx = old_center
    
    def update(self):
        if self.powerup_timer > 0:
            self.powerup_timer -= 1
            if self.powerup_timer == 0:
                old_center = self.rect.centerx
                self.rect.width = self.normal_width
                self.rect.centerx = old_center
                self.current_powerup = None
        
        if self.shield_timer > 0:
            self.shield_timer -= 1
    
    def draw(self, screen):
        color = BLUE
        if self.current_powerup == "wide_paddle":
            color = GREEN
        elif self.current_powerup == "narrow_paddle":
            color = RED
        
        pygame.draw.rect(screen, color, self.rect)
        
        # Draw shield effect
        if self.shield_timer > 0:
            shield_rect = pygame.Rect(self.rect.x - 5, self.rect.y - 5, 
                                    self.rect.width + 10, self.rect.height + 10)
            pygame.draw.rect(screen, CYAN, shield_rect, 3)
            
            # Shield timer indicator
            timer_width = (self.shield_timer / 600) * self.rect.width
            timer_rect = pygame.Rect(self.rect.x, self.rect.y - 8, timer_width, 2)
            pygame.draw.rect(screen, CYAN, timer_rect)
        
        # Power-up timer indicator
        if self.powerup_timer > 0:
            timer_width = (self.powerup_timer / 300) * self.rect.width
            timer_rect = pygame.Rect(self.rect.x, self.rect.y - 5, timer_width, 3)
            pygame.draw.rect(screen, YELLOW, timer_rect)

class Ball:
    def __init__(self, x, y, ball_type="normal"):
        self.rect = pygame.Rect(x, y, BALL_SIZE, BALL_SIZE)
        self.speed_x = BALL_SPEED_X
        self.speed_y = BALL_SPEED_Y
        self.trail = []
        self.max_trail_length = 5
        self.ball_type = ball_type
        self.pierce_count = 0
        self.life_timer = 1800  # 30 seconds for special balls
        
        # Different properties for different ball types
        if ball_type == "fire":
            self.pierce_count = 3  # Can go through 3 bricks
            self.color = RED
            self.max_trail_length = 8
        elif ball_type == "steel":
            self.color = SILVER
            self.damage_multiplier = 2  # Deals double damage
        elif ball_type == "lightning":
            self.color = YELLOW
            self.speed_multiplier = 1.5
            self.speed_x *= self.speed_multiplier
            self.speed_y *= self.speed_multiplier
        else:
            self.color = WHITE
            self.damage_multiplier = 1
    
    def move(self):
        # Special balls have limited lifetime
        if self.ball_type != "normal":
            self.life_timer -= 1
            if self.life_timer <= 0:
                return False  # Ball should be removed
        
        # Add current position to trail
        self.trail.append((self.rect.centerx, self.rect.centery))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
        
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        return True
    
    def bounce_x(self):
        self.speed_x = -self.speed_x
    
    def bounce_y(self):
        self.speed_y = -self.speed_y
    
    def speed_up(self):
        self.speed_x *= 1.1
        self.speed_y *= 1.1
    
    def can_pierce(self):
        """Check if fire ball can pierce through bricks"""
        if self.ball_type == "fire" and self.pierce_count > 0:
            self.pierce_count -= 1
            return True
        return False
    
    def draw(self, screen):
        # Draw trail with ball-specific color
        for i, pos in enumerate(self.trail):
            alpha = int(255 * (i + 1) / len(self.trail) * 0.5)
            trail_surface = pygame.Surface((BALL_SIZE, BALL_SIZE))
            trail_surface.set_alpha(alpha)
            trail_surface.fill(self.color)
            screen.blit(trail_surface, (pos[0] - BALL_SIZE//2, pos[1] - BALL_SIZE//2))
        
        # Draw main ball
        pygame.draw.rect(screen, self.color, self.rect)
        
        # Special effects for different ball types
        if self.ball_type == "fire":
            # Draw fire glow
            glow_rect = pygame.Rect(self.rect.x - 2, self.rect.y - 2, 
                                  BALL_SIZE + 4, BALL_SIZE + 4)
            pygame.draw.rect(screen, ORANGE, glow_rect, 2)
        elif self.ball_type == "lightning":
            # Draw lightning effect
            if random.random() < 0.3:  # 30% chance per frame
                for _ in range(3):
                    x1 = self.rect.centerx + random.randint(-15, 15)
                    y1 = self.rect.centery + random.randint(-15, 15)
                    x2 = self.rect.centerx + random.randint(-15, 15)
                    y2 = self.rect.centery + random.randint(-15, 15)
                    pygame.draw.line(screen, YELLOW, (x1, y1), (x2, y2), 2)

class Brick:
    def __init__(self, x, y, color, hits_required=1):
        self.rect = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
        self.color = color
        self.original_color = color
        self.destroyed = False
        self.hits_required = hits_required
        self.hits_taken = 0
    
    def hit(self, damage=1):
        self.hits_taken += damage
        if self.hits_taken >= self.hits_required:
            self.destroyed = True
            return True
        else:
            # Change color to show damage
            r, g, b = self.original_color
            damage_factor = self.hits_taken / self.hits_required
            self.color = (max(0, int(r * (1 - damage_factor * 0.7))), 
                         max(0, int(g * (1 - damage_factor * 0.7))), 
                         max(0, int(b * (1 - damage_factor * 0.7))))
            return False
    
    def draw(self, screen):
        if not self.destroyed:
            pygame.draw.rect(screen, self.color, self.rect)
            pygame.draw.rect(screen, BLACK, self.rect, 2)
            
            # Draw hit indicators
            if self.hits_required > 1:
                remaining_hits = self.hits_required - self.hits_taken
                for i in range(remaining_hits):
                    dot_x = self.rect.x + 10 + i * 12
                    dot_y = self.rect.y + 5
                    pygame.draw.circle(screen, WHITE, (dot_x, dot_y), 2)

class BossBrick:
    """Special boss brick that moves and has lots of health"""
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, BRICK_WIDTH * 3, BRICK_HEIGHT * 2)
        self.max_health = 50
        self.health = self.max_health
        self.speed = 1
        self.direction = 1
        self.shoot_timer = 0
        self.destroyed = False
        self.color = PURPLE
    
    def update(self):
        # Move side to side
        self.rect.x += self.speed * self.direction
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.direction *= -1
        
        # Shooting timer
        self.shoot_timer += 1
        return self.shoot_timer >= 120  # Shoot every 2 seconds
    
    def reset_shoot_timer(self):
        self.shoot_timer = 0
    
    def hit(self, damage=1):
        self.health -= damage
        if self.health <= 0:
            self.destroyed = True
            return True
        
        # Flash red when hit
        flash_intensity = min(255, damage * 50)
        self.color = (min(255, 128 + flash_intensity), 0, max(0, 128 - flash_intensity))
        return False
    
    def draw(self, screen):
        if not self.destroyed:
            pygame.draw.rect(screen, self.color, self.rect)
            pygame.draw.rect(screen, BLACK, self.rect, 3)
            
            # Draw health bar
            health_ratio = self.health / self.max_health
            health_width = int(self.rect.width * health_ratio)
            health_rect = pygame.Rect(self.rect.x, self.rect.y - 10, health_width, 5)
            health_bg_rect = pygame.Rect(self.rect.x, self.rect.y - 10, self.rect.width, 5)
            
            pygame.draw.rect(screen, RED, health_bg_rect)
            pygame.draw.rect(screen, GREEN, health_rect)
            
            # Draw boss eyes
            eye1 = (self.rect.x + 30, self.rect.y + 20)
            eye2 = (self.rect.x + self.rect.width - 30, self.rect.y + 20)
            pygame.draw.circle(screen, RED, eye1, 8)
            pygame.draw.circle(screen, RED, eye2, 8)
            pygame.draw.circle(screen, WHITE, eye1, 4)
            pygame.draw.circle(screen, WHITE, eye2, 4)

class Projectile:
    """Boss projectiles"""
    def __init__(self, x, y, target_x, target_y):
        self.rect = pygame.Rect(x, y, 8, 8)
        # Calculate direction towards target
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            self.speed_x = (dx / distance) * 4
            self.speed_y = (dy / distance) * 4
        else:
            self.speed_x = 0
            self.speed_y = 4
    
    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        return (0 <= self.rect.x <= SCREEN_WIDTH and 0 <= self.rect.y <= SCREEN_HEIGHT)
    
    def draw(self, screen):
        pygame.draw.rect(screen, ORANGE, self.rect)
        pygame.draw.rect(screen, RED, self.rect, 2)

class PowerUp:
    def __init__(self, x, y, powerup_type):
        self.rect = pygame.Rect(x, y, POWERUP_SIZE, POWERUP_SIZE)
        self.type = powerup_type
        self.speed = POWERUP_SPEED
        self.active = True
        
        self.colors = {
            "wide_paddle": GREEN,
            "narrow_paddle": RED,
            "multi_ball": CYAN,
            "extra_life": PINK,
            "fire_ball": ORANGE,
            "steel_ball": SILVER,
            "lightning_ball": YELLOW,
            "shield": CYAN
        }
        
        self.symbols = {
            "wide_paddle": "W",
            "narrow_paddle": "N",
            "multi_ball": "M",
            "extra_life": "♥",
            "fire_ball": "F",
            "steel_ball": "S",
            "lightning_ball": "L",
            "shield": "◊"
        }
    
    def move(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.active = False
    
    def draw(self, screen, font):
        if self.active:
            color = self.colors.get(self.type, WHITE)
            pygame.draw.rect(screen, color, self.rect)
            pygame.draw.rect(screen, BLACK, self.rect, 2)
            
            symbol = self.symbols.get(self.type, "?")
            text = font.render(symbol, True, BLACK)
            text_rect = text.get_rect(center=self.rect.center)
            screen.blit(text, text_rect)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Ultimate Brick Breaker")
        self.clock = pygame.time.Clock()
        
        self.sound_manager = SoundManager()
        self.particle_system = ParticleSystem()
        
        # Game states
        self.game_state = "start_screen"  # start_screen, playing, paused, game_over
        self.level = 1
        self.max_level = 7
        self.score = 0
        self.lives = 3
        self.balls = []
        self.powerups = []
        self.boss_brick = None
        self.boss_projectiles = []
        
        # Mouse control
        self.use_mouse = True
        self.mouse_sensitivity = 1.0
        
        # Fonts
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 48)
        self.title_font = pygame.font.Font(None, 72)
        
        # Initialize game objects as None (will be created when game starts)
        #self.paddle = None#
        self.paddle = Paddle(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)

        self.bricks = []
        
        print(f"Game initialized with state: {self.game_state}")

    def start_game(self):
        """Initialize game for playing"""
        self.game_state = "playing"
        self.level = 1
        self.score = 0
        self.lives = 3
        self.particle_system = ParticleSystem()
        self.paddle = Paddle(SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.reset_level()
    
    def is_boss_level(self):
        return self.level % 3 == 0 and self.level <= 6  # Boss on levels 3, 6
    
    def reset_level(self):
        self.paddle = Paddle(SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.balls = [Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.powerups = []
        self.bricks = []
        self.boss_brick = None
        self.boss_projectiles = []
        
        if self.is_boss_level():
            self.create_boss_level()
        else:
            self.create_bricks()
    
    def create_boss_level(self):
        """Create boss level with boss brick and support bricks"""
        # Create boss
        self.boss_brick = BossBrick(SCREEN_WIDTH // 2 - (BRICK_WIDTH * 3) // 2, 100)
        
        # Create some support bricks
        colors = [RED, ORANGE, YELLOW, GREEN]
        for row in range(2):
            for col in range(8):
                if col < 2 or col > 5:  # Leave space for boss
                    x = col * (BRICK_WIDTH + 10) + 50
                    y = row * (BRICK_HEIGHT + 10) + 250
                    color = colors[row % len(colors)]
                    hits = 3 if row == 0 else 2
                    self.bricks.append(Brick(x, y, color, hits))
    
    def create_bricks(self):
        colors = [RED, ORANGE, YELLOW, GREEN, PURPLE]
        
        if self.level == 1:
            for row in range(5):
                for col in range(10):
                    x = col * (BRICK_WIDTH + 5) + 35
                    y = row * (BRICK_HEIGHT + 5) + 50
                    color = colors[row % len(colors)]
                    self.bricks.append(Brick(x, y, color, 1))
        
        elif self.level == 2:
            for row in range(5):
                for col in range(10):
                    x = col * (BRICK_WIDTH + 5) + 35
                    y = row * (BRICK_HEIGHT + 5) + 50
                    color = colors[row % len(colors)]
                    hits = 2 if row < 2 else 1
                    self.bricks.append(Brick(x, y, color, hits))
        
        elif self.level == 4:
            # After first boss - harder level
            for row in range(6):
                for col in range(10):
                    if (row + col) % 3 != 0:  # More gaps
                        x = col * (BRICK_WIDTH + 5) + 35
                        y = row * (BRICK_HEIGHT + 5) + 50
                        color = colors[row % len(colors)]
                        hits = min(4, row + 1)
                        self.bricks.append(Brick(x, y, color, hits))
        
        elif self.level == 5:
            # Diamond pattern
            for row in range(7):
                for col in range(10):
                    center_row, center_col = 3, 5
                    if abs(row - center_row) + abs(col - center_col) <= 4:
                        x = col * (BRICK_WIDTH + 5) + 35
                        y = row * (BRICK_HEIGHT + 5) + 50
                        color = colors[row % len(colors)]
                        hits = 5 if abs(row - center_row) + abs(col - center_col) <= 1 else 3
                        self.bricks.append(Brick(x, y, color, hits))
        
        else:  # Level 7+
            for row in range(8):
                for col in range(10):
                    x = col * (BRICK_WIDTH + 5) + 35
                    y = row * (BRICK_HEIGHT + 5) + 50
                    color = colors[row % len(colors)]
                    hits = min(6, row + 2)
                    self.bricks.append(Brick(x, y, color, hits))
    
    def spawn_powerup(self, x, y):
        if random.random() < 0.2:  # 20% chance
            powerup_types = ["wide_paddle", "narrow_paddle", "multi_ball", "extra_life", 
                           "fire_ball", "steel_ball", "lightning_ball", "shield"]
            # Boss levels have better power-ups
            if self.is_boss_level():
                powerup_types = ["fire_ball", "steel_ball", "lightning_ball", "shield", "extra_life"]
            
            powerup_type = random.choice(powerup_types)
            self.powerups.append(PowerUp(x, y, powerup_type))
    
    def handle_input(self):
        # Only handle input if paddle exists
        if not self.paddle:
            return
            
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        
        if self.use_mouse:
            # Mouse control - paddle follows mouse X position
            target_x = mouse_pos[0] - self.paddle.rect.width // 2
            # Smooth movement towards mouse position
            diff = target_x - self.paddle.rect.x
            if abs(diff) > 2:  # Dead zone to prevent jittering
                self.paddle.rect.x += diff * 0.3  # Smooth interpolation
            
            # Keep paddle on screen
            if self.paddle.rect.left < 0:
                self.paddle.rect.left = 0
            elif self.paddle.rect.right > SCREEN_WIDTH:
                self.paddle.rect.right = SCREEN_WIDTH
        else:
            # Keyboard control
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.paddle.move("left")
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.paddle.move("right")
        
        # Toggle control method
        if keys[pygame.K_TAB]:
            self.use_mouse = not self.use_mouse
    
    def update(self):
        # Update particle system
        self.particle_system.update()
        
        # Update paddle
        self.paddle.update()
        
        # Update boss
        if self.boss_brick and not self.boss_brick.destroyed:
            if self.boss_brick.update():
                # Boss shoots at paddle
                self.boss_projectiles.append(Projectile(
                    self.boss_brick.rect.centerx, 
                    self.boss_brick.rect.bottom,
                    self.paddle.rect.centerx,
                    self.paddle.rect.centery
                ))
                self.boss_brick.reset_shoot_timer()
                self.sound_manager.play_fireball()
        
        # Update boss projectiles
        for projectile in self.boss_projectiles[:]:
            if not projectile.update():
                self.boss_projectiles.remove(projectile)
            elif projectile.rect.colliderect(self.paddle.rect):
                if self.paddle.shield_timer <= 0:  # Shield blocks damage
                    self.lives -= 1
                    self.particle_system.add_explosion(projectile.rect.centerx, projectile.rect.centery, RED, 15)
                else:
                    self.particle_system.add_sparkle(projectile.rect.centerx, projectile.rect.centery, CYAN, 10)
                self.boss_projectiles.remove(projectile)
        
        # Update balls
        for ball in self.balls[:]:
            if not ball.move():
                self.balls.remove(ball)  # Remove expired special balls
                continue
            
            # Add trail particles for special balls
            if ball.ball_type != "normal":
                self.particle_system.add_trail(ball.rect.centerx, ball.rect.centery, ball.color)
            
            # Ball collision with walls
            if ball.rect.left <= 0 or ball.rect.right >= SCREEN_WIDTH:
                ball.bounce_x()
            if ball.rect.top <= 0:
                ball.bounce_y()
            
            # Ball collision with paddle
            if ball.rect.colliderect(self.paddle.rect) and ball.speed_y > 0:
                ball.bounce_y()
                hit_pos = (ball.rect.centerx - self.paddle.rect.centerx) / (self.paddle.rect.width / 2)
                ball.speed_x = BALL_SPEED_X * hit_pos * 0.5
                self.sound_manager.play_paddle_hit()
                self.particle_system.add_sparkle(ball.rect.centerx, ball.rect.centery, WHITE, 5)
            
            # Ball collision with boss
            if self.boss_brick and not self.boss_brick.destroyed and ball.rect.colliderect(self.boss_brick.rect):
                damage = getattr(ball, 'damage_multiplier', 1)
                if self.boss_brick.hit(damage):
                    self.score += 500
                    self.particle_system.add_explosion(self.boss_brick.rect.centerx, self.boss_brick.rect.centery, PURPLE, 30)
                    self.sound_manager.play_boss_defeat()
                else:
                    self.sound_manager.play_boss_hit()
                    self.particle_system.add_sparkle(ball.rect.centerx, ball.rect.centery, PURPLE, 8)
                
                if not ball.can_pierce():
                    ball.bounce_y()
            
            # Ball collision with bricks
            for brick in self.bricks:
                if not brick.destroyed and ball.rect.colliderect(brick.rect):
                    damage = getattr(ball, 'damage_multiplier', 1)
                    if brick.hit(damage):
                        self.score += 10 * self.level
                        self.spawn_powerup(brick.rect.centerx, brick.rect.centery)
                        self.particle_system.add_explosion(brick.rect.centerx, brick.rect.centery, brick.color, 15)
                    else:
                        self.particle_system.add_sparkle(ball.rect.centerx, ball.rect.centery, brick.color, 5)
                    
                    if not ball.can_pierce():
                        ball.bounce_y()
                    self.sound_manager.play_brick_hit()
                    break
            
            # Remove ball if it falls off bottom
            if ball.rect.bottom >= SCREEN_HEIGHT:
                self.balls.remove(ball)
        
        # Check if all balls are gone
        if not self.balls:
            self.lives -= 1
            if self.lives > 0:
                self.balls = [Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
            else:
                self.sound_manager.play_game_over()
        
        # Update power-ups
        for powerup in self.powerups[:]:
            powerup.move()
            if not powerup.active:
                self.powerups.remove(powerup)
            elif powerup.rect.colliderect(self.paddle.rect):
                self.apply_powerup(powerup.type)
                self.powerups.remove(powerup)
                self.sound_manager.play_powerup()
                self.particle_system.add_sparkle(powerup.rect.centerx, powerup.rect.centery, powerup.colors[powerup.type], 10)
        
        # Check level completion
        all_bricks_destroyed = all(brick.destroyed for brick in self.bricks)
        boss_defeated = not self.boss_brick or self.boss_brick.destroyed
        
        if all_bricks_destroyed and boss_defeated:
            self.level += 1
            self.sound_manager.play_level_complete()
            if self.level <= self.max_level:
                self.reset_level()
                # Speed up balls slightly each level
                for ball in self.balls:
                    ball.speed_up()
    
    def apply_powerup(self, powerup_type):
        if powerup_type in ["wide_paddle", "narrow_paddle", "shield"]:
            self.paddle.apply_powerup(powerup_type)
        elif powerup_type == "multi_ball" and len(self.balls) < 4:
            # Add extra balls
            for ball in self.balls[:]:
                new_ball = Ball(ball.rect.x, ball.rect.y, ball.ball_type)
                new_ball.speed_x = -ball.speed_x
                new_ball.speed_y = ball.speed_y
                self.balls.append(new_ball)
                break
        elif powerup_type == "extra_life":
            self.lives += 1
        elif powerup_type == "fire_ball":
            # Convert random ball to fire ball
            if self.balls:
                ball = random.choice(self.balls)
                ball.ball_type = "fire"
                ball.pierce_count = 3
                ball.color = RED
                ball.max_trail_length = 8
                ball.life_timer = 1800
        elif powerup_type == "steel_ball":
            # Convert random ball to steel ball
            if self.balls:
                ball = random.choice(self.balls)
                ball.ball_type = "steel"
                ball.color = SILVER
                ball.damage_multiplier = 2
                ball.life_timer = 1200
        elif powerup_type == "lightning_ball":
            # Convert random ball to lightning ball
            if self.balls:
                ball = random.choice(self.balls)
                ball.ball_type = "lightning"
                ball.color = YELLOW
                ball.speed_multiplier = 1.5
                ball.speed_x *= ball.speed_multiplier
                ball.speed_y *= ball.speed_multiplier
                ball.life_timer = 900
    
    def draw_start_screen(self):
        """Draw the start screen with instructions"""
        self.screen.fill(BLACK)
        
        # Animated background particles
        for _ in range(50):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            color = random.choice([BLUE, GREEN, YELLOW, PURPLE, CYAN])
            alpha = random.randint(30, 100)
            size = random.randint(1, 3)
            
            particle_surface = pygame.Surface((size * 2, size * 2))
            particle_surface.set_alpha(alpha)
            particle_surface.fill(color)
            self.screen.blit(particle_surface, (x - size, y - size))
        
        # Title
        title_text = self.title_font.render("ULTIMATE BRICK BREAKER", True, GOLD)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = self.font.render("The Most Advanced Brick Breaker Ever!", True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 130))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Instructions sections
        y_start = 180
        
        # Controls section
        controls_title = self.font.render("CONTROLS:", True, CYAN)
        self.screen.blit(controls_title, (50, y_start))
        y_start += 35
        
        controls = [
            "• Mouse: Move paddle (recommended)",
            "• Arrow Keys / A,D: Move paddle (classic)",
            "• TAB: Switch between mouse/keyboard control",
            "• R: Restart game",
            "• ESC: Pause game"
        ]
        
        for control in controls:
            text = self.small_font.render(control, True, WHITE)
            self.screen.blit(text, (70, y_start))
            y_start += 20
        
        y_start += 15
        
        # Power-ups section
        powerups_title = self.font.render("POWER-UPS:", True, GREEN)
        self.screen.blit(powerups_title, (50, y_start))
        y_start += 35
        
        powerups = [
            "• W = Wide Paddle (easier to hit)",
            "• N = Narrow Paddle (more challenge)", 
            "• M = Multi-Ball (more balls!)",
            "• ♥ = Extra Life",
            "• F = Fire Ball (pierces 3 bricks)",
            "• S = Steel Ball (2x damage)",
            "• L = Lightning Ball (super fast)",
            "• ◊ = Shield (blocks boss attacks)"
        ]
        
        for powerup in powerups:
            text = self.small_font.render(powerup, True, WHITE)
            self.screen.blit(text, (70, y_start))
            y_start += 20
        
        # Game features section
        features_title = self.font.render("SPECIAL FEATURES:", True, PURPLE)
        self.screen.blit(features_title, (SCREEN_WIDTH // 2 + 50, 180))
        
        features = [
            "★ 7 Challenging Levels",
            "★ Epic Boss Battles (Levels 3 & 6)",
            "★ Particle Effects & Visual Magic",
            "★ 3 Special Ball Types",
            "★ Smart Brick Patterns",
            "★ Progressive Difficulty",
            "★ Advanced Physics",
            "★ Professional Sound System*"
        ]
        
        y_pos = 215
        for feature in features:
            text = self.small_font.render(feature, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH // 2 + 70, y_pos))
            y_pos += 20
        
        # Sound note
        sound_status = "Sound: " + ("Enabled" if self.sound_manager.sound_enabled else "Disabled (install numpy for audio)")
        sound_note = self.small_font.render(sound_status, True, GREEN if self.sound_manager.sound_enabled else YELLOW)
        self.screen.blit(sound_note, (SCREEN_WIDTH // 2 + 70, y_pos + 10))
        
        # Start instructions
        start_text = self.large_font.render("Press SPACE to Start!", True, GOLD)
        
        # Pulsing effect for start text
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 0.3 + 0.7
        pulsed_text = self.large_font.render("Press SPACE to Start!", True, (int(255 * pulse), int(215 * pulse), 0))
        pulsed_rect = pulsed_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
        self.screen.blit(pulsed_text, pulsed_rect)
        
        # Version info
        version_text = self.small_font.render("Ultimate Edition v2.0 - By HillTop Digital Media", True, SILVER)
        version_rect = version_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
        self.screen.blit(version_text, version_rect)
        """Draw the main game screen"""
        """Draw the start screen with instructions"""
        self.screen.fill(BLACK)
        
        # Animated background particles
        for _ in range(50):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            color = random.choice([BLUE, GREEN, YELLOW, PURPLE, CYAN])
            alpha = random.randint(30, 100)
            size = random.randint(1, 3)
            
            particle_surface = pygame.Surface((size * 2, size * 2))
            particle_surface.set_alpha(alpha)
            particle_surface.fill(color)
            self.screen.blit(particle_surface, (x - size, y - size))
        
        # Title
        title_text = self.title_font.render("ULTIMATE BRICK BREAKER", True, GOLD)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = self.font.render("The Most Advanced Brick Breaker Ever!", True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 130))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Instructions sections
        y_start = 180
        section_spacing = 25
        
        # Controls section
        controls_title = self.font.render("CONTROLS:", True, CYAN)
        self.screen.blit(controls_title, (50, y_start))
        y_start += 35
        
        controls = [
            "• Mouse: Move paddle (recommended)",
            "• Arrow Keys / A,D: Move paddle (classic)",
            "• TAB: Switch between mouse/keyboard control",
            "• R: Restart game",
            "• ESC: Pause game"
        ]
        
        for control in controls:
            text = self.small_font.render(control, True, WHITE)
            self.screen.blit(text, (70, y_start))
            y_start += 20
        
        y_start += 15
        
        # Power-ups section
        powerups_title = self.font.render("POWER-UPS:", True, GREEN)
        self.screen.blit(powerups_title, (50, y_start))
        y_start += 35
        
        powerups = [
            "• W = Wide Paddle (easier to hit)",
            "• N = Narrow Paddle (more challenge)", 
            "• M = Multi-Ball (more balls!)",
            "• ♥ = Extra Life",
            "• F = Fire Ball (pierces 3 bricks)",
            "• S = Steel Ball (2x damage)",
            "• L = Lightning Ball (super fast)",
            "• ◊ = Shield (blocks boss attacks)"
        ]
        
        for powerup in powerups:
            text = self.small_font.render(powerup, True, WHITE)
            self.screen.blit(text, (70, y_start))
            y_start += 20
        
       # Game features section
        features_title = self.font.render("SPECIAL FEATURES:", True, PURPLE)
        features_rect = features_title.get_rect(center=(SCREEN_WIDTH - 200, 180))
        self.screen.blit(features_title, (SCREEN_WIDTH // 2 + 50, 180))
        
        features = [
            "★ 7 Challenging Levels",
            "★ Epic Boss Battles (Levels 3 & 6)",
            "★ Particle Effects & Visual Magic",
            "★ 3 Special Ball Types",
            "★ Smart Brick Patterns",
            "★ Progressive Difficulty",
            "★ Advanced Physics",
            "★ Professional Sound System*"
        ]
        
        y_pos = 215
        for feature in features:
            text = self.small_font.render(feature, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH // 2 + 70, y_pos))
            y_pos += 20
        
        # Sound note
        sound_note = self.small_font.render("*Install numpy for full audio experience", True, YELLOW)
        self.screen.blit(sound_note, (SCREEN_WIDTH // 2 + 70, y_pos + 10))
        
        # Start instructions
        start_text = self.large_font.render("Press SPACE to Start!", True, GOLD)
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
        
        # Pulsing effect for start text
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 0.3 + 0.7
        start_surface = pygame.Surface(start_text.get_size())
        start_surface.set_alpha(int(255 * pulse))
        start_surface.fill(GOLD)
        
        # Create pulsing text
        pulsed_text = self.large_font.render("Press SPACE to Start!", True, (int(255 * pulse), int(215 * pulse), 0))
        pulsed_rect = pulsed_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
        self.screen.blit(pulsed_text, pulsed_rect)
        
    def draw_game(self):
        """Draw the main game screen"""        
        self.screen.fill(BLACK)
        
        # Draw particle effects first (background)
        self.particle_system.draw(self.screen)
        
        # Draw game objects (check if they exist first)
        if self.paddle is not None:
            self.paddle.draw(self.screen)
        
        for ball in self.balls:
            ball.draw(self.screen)
        
        for brick in self.bricks:
            brick.draw(self.screen)
        
        if self.boss_brick:
            self.boss_brick.draw(self.screen)
        
        for projectile in self.boss_projectiles:
            projectile.draw(self.screen)
        
        for powerup in self.powerups:
            powerup.draw(self.screen, self.small_font)
        
        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (10, 50))
        self.screen.blit(level_text, (10, 90))
        
        # Draw control method indicator
        control_text = f"Control: {'Mouse' if self.use_mouse else 'Keyboard'}"
        control_surface = self.small_font.render(control_text, True, YELLOW)
        self.screen.blit(control_surface, (SCREEN_WIDTH - 150, 10))
        
        # Draw ball type indicators
        y_offset = 130
        for i, ball in enumerate(self.balls):
            if ball.ball_type != "normal":
                ball_info = f"Ball {i+1}: {ball.ball_type.title()}"
                if hasattr(ball, 'life_timer'):
                    time_left = ball.life_timer // 60
                    ball_info += f" ({time_left}s)"
                ball_text = self.small_font.render(ball_info, True, ball.color)
                self.screen.blit(ball_text, (10, y_offset))
                y_offset += 20
        
        # Draw active power-up info (check paddle exists)
        if self.paddle:
            if self.paddle.current_powerup:
                powerup_text = self.small_font.render(f"Paddle: {self.paddle.current_powerup}", True, YELLOW)
                self.screen.blit(powerup_text, (SCREEN_WIDTH - 200, 30))
            
            if self.paddle.shield_timer > 0:
                shield_time = self.paddle.shield_timer // 60
                shield_text = self.small_font.render(f"Shield: {shield_time}s", True, CYAN)
                self.screen.blit(shield_text, (SCREEN_WIDTH - 200, 50))
        
        # Level-specific messages
        if self.is_boss_level():
            if self.boss_brick and not self.boss_brick.destroyed:
                boss_text = self.font.render("BOSS FIGHT!", True, RED)
                text_rect = boss_text.get_rect(center=(SCREEN_WIDTH//2, 30))
                self.screen.blit(boss_text, text_rect)
        
        # Check win condition
        if self.level > self.max_level:
            win_text = self.font.render("YOU ARE THE ULTIMATE CHAMPION!", True, GOLD)
            win_text2 = self.font.render("Press R to restart", True, GREEN)
            text_rect1 = win_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
            text_rect2 = win_text2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            self.screen.blit(win_text, text_rect1)
            self.screen.blit(win_text2, text_rect2)
        elif self.is_boss_level() and self.boss_brick and self.boss_brick.destroyed and all(brick.destroyed for brick in self.bricks):
            boss_defeat_text = self.font.render("BOSS DEFEATED! Next level starting...", True, GOLD)
            text_rect = boss_defeat_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(boss_defeat_text, text_rect)
        elif not self.is_boss_level() and all(brick.destroyed for brick in self.bricks):
            next_text = self.font.render(f"Level {self.level-1} Complete! Next level starting...", True, GREEN)
            text_rect = next_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(next_text, text_rect)
        
        # Check lose condition
        if self.lives <= 0:
            lose_text = self.font.render("GAME OVER! Press R to restart", True, RED)
            text_rect = lose_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(lose_text, text_rect)
        
        # Quick help at bottom
        help_text = self.small_font.render("TAB: Switch controls | ESC: Pause | R: Restart", True, SILVER)
        help_rect = help_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 15))
        self.screen.blit(help_text, help_rect)
    
    def draw_pause_screen(self):
        """Draw pause screen overlay"""
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Draw pause text
        pause_text = self.large_font.render("GAME PAUSED", True, YELLOW)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(pause_text, pause_rect)
        
        resume_text = self.font.render("Press ESC to Resume", True, WHITE)
        resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(resume_text, resume_rect)
        
        restart_text = self.font.render("Press R to Restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
        self.screen.blit(restart_text, restart_rect)
    
    def draw(self):
        """Main draw method that routes to appropriate screen"""        
        if self.game_state == "start_screen":
            self.draw_start_screen()
        elif self.game_state == "playing":
            self.draw_game()
        elif self.game_state == "paused":
            self.draw_game()  # Draw game in background
            self.draw_pause_screen()
        else:
            # Fallback - should never happen
            print(f"Unknown game state: {self.game_state}")
            self.draw_start_screen()
        
        pygame.display.flip()
        self.screen.fill(BLACK)
        
        # Draw particle effects first (background)
        self.particle_system.draw(self.screen)
        
        # Draw game objects
        self.paddle.draw(self.screen)
        
        for ball in self.balls:
            ball.draw(self.screen)
        
        for brick in self.bricks:
            brick.draw(self.screen)
        
        if self.boss_brick:
            self.boss_brick.draw(self.screen)
        
        for projectile in self.boss_projectiles:
            projectile.draw(self.screen)
        
        for powerup in self.powerups:
            powerup.draw(self.screen, self.small_font)
        
        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (10, 50))
        self.screen.blit(level_text, (10, 90))
        
        # Draw ball type indicators
        y_offset = 130
        for i, ball in enumerate(self.balls):
            if ball.ball_type != "normal":
                ball_info = f"Ball {i+1}: {ball.ball_type.title()}"
                if hasattr(ball, 'life_timer'):
                    time_left = ball.life_timer // 60  # Convert to seconds
                    ball_info += f" ({time_left}s)"
                ball_text = self.small_font.render(ball_info, True, ball.color)
                self.screen.blit(ball_text, (10, y_offset))
                y_offset += 20
        
        # Draw active power-up info
        if self.paddle.current_powerup:
            powerup_text = self.small_font.render(f"Paddle: {self.paddle.current_powerup}", True, YELLOW)
            self.screen.blit(powerup_text, (SCREEN_WIDTH - 200, 10))
        
        if self.paddle.shield_timer > 0:
            shield_time = self.paddle.shield_timer // 60
            shield_text = self.small_font.render(f"Shield: {shield_time}s", True, CYAN)
            self.screen.blit(shield_text, (SCREEN_WIDTH - 200, 30))
        
        # Level-specific messages
        if self.is_boss_level():
            if self.boss_brick and not self.boss_brick.destroyed:
                boss_text = self.font.render("BOSS FIGHT!", True, RED)
                text_rect = boss_text.get_rect(center=(SCREEN_WIDTH//2, 30))
                self.screen.blit(boss_text, text_rect)
        
        # Check win condition
        if self.level > self.max_level:
            win_text = self.font.render("YOU ARE THE ULTIMATE CHAMPION!", True, GOLD)
            win_text2 = self.font.render("Press R to restart", True, GREEN)
            text_rect1 = win_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
            text_rect2 = win_text2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            self.screen.blit(win_text, text_rect1)
            self.screen.blit(win_text2, text_rect2)
        elif self.is_boss_level() and self.boss_brick and self.boss_brick.destroyed and all(brick.destroyed for brick in self.bricks):
            boss_defeat_text = self.font.render("BOSS DEFEATED! Next level starting...", True, GOLD)
            text_rect = boss_defeat_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(boss_defeat_text, text_rect)
        elif not self.is_boss_level() and all(brick.destroyed for brick in self.bricks):
            next_text = self.font.render(f"Level {self.level-1} Complete! Next level starting...", True, GREEN)
            text_rect = next_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(next_text, text_rect)
        
        # Check lose condition
        if self.lives <= 0:
            lose_text = self.font.render("GAME OVER! Press R to restart", True, RED)
            text_rect = lose_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(lose_text, text_rect)
        
    def reset_game(self):
        """Reset entire game"""
        self.game_state = "playing"
        self.level = 1
        self.score = 0
        self.lives = 3
        self.particle_system = ParticleSystem()
        self.reset_level()
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.game_state == "start_screen":
                        if event.key == pygame.K_SPACE:
                            self.start_game()
                    
                    elif self.game_state == "playing":
                        if event.key == pygame.K_ESCAPE:
                            self.game_state = "paused"
                        elif event.key == pygame.K_r:
                            if (self.lives <= 0 or self.level > self.max_level or 
                                (all(brick.destroyed for brick in self.bricks) and 
                                 (not self.boss_brick or self.boss_brick.destroyed))):
                                self.reset_game()
                    
                    elif self.game_state == "paused":
                        if event.key == pygame.K_ESCAPE:
                            self.game_state = "playing"
                        elif event.key == pygame.K_r:
                            self.reset_game()
            
            # Update game logic only when playing
            if self.game_state == "playing" and self.lives > 0 and self.level <= self.max_level:
                self.handle_input()
                self.update()
            
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()