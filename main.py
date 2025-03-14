import pgzrun
import random
from pygame import Rect

# Game screen dimensions
WIDTH, HEIGHT = 800, 600

# Game state variables
game_over, win = False, False
game_over_timer, win_timer = 0, 0  # Message durations

# Sounds
fireball_sound = sounds.load("fireball_sound.wav")
player_hit_sound = sounds.load("player_hit_sound.wav")
game_over_sound = sounds.load("game_over_sound.wav")
win_sound = sounds.load("win_sound.wav")

# Player class
class Player(Actor):
    def __init__(self, image, pos):
        super().__init__(image, pos)
        self.vy, self.on_ground, self.hp = 0, False, 200
        self.attacking, self.attack_duration = False, 0
        self.projectiles = []
        self.state = "normal"
        self.images = {"normal": "player1", "attack": "player_attack", "dead": "player_dead"}
        self.image = self.images[self.state]

    def move(self, keys):
        # Player movement controls
        speed = 5
        if keys.left: self.x -= speed
        if keys.right: self.x += speed
        if keys.up and self.on_ground:
            self.vy = -10
            self.on_ground = False

    def attack(self):
        # Player attack method
        if self.state != "dead" and not self.attacking:
            self.state = "attack"
            self.image = self.images[self.state]
            self.attack_duration = 20
            self.attacking = True
            self.projectiles.append(Projectile("fireball1", (self.x, self.y - 20), 5))
            fireball_sound.play()

    def update(self):
        # Update player position, state, and actions
        self.vy += 0.5
        self.y += self.vy
        if self.y > HEIGHT - 50:
            self.y = HEIGHT - 50
            self.vy = 0
            self.on_ground = True

        if self.attacking:
            self.attack_duration -= 1
            if self.attack_duration <= 0:
                self.attacking = False
                self.state = "normal"
                self.image = self.images[self.state]

        if self.hp <= 0:
            self.state = "dead"
            self.image = self.images[self.state]

        for projectile in self.projectiles:
            projectile.update()


# Enemy class
class Enemy(Actor):
    def __init__(self, enemy_type, pos, speed):
        super().__init__(f"{enemy_type}.png", pos)
        self.speed, self.direction, self.hp = speed, 1, 150
        self.projectiles = []
        self.enemy_type = enemy_type
        self.state = "normal"
        self.images = {"normal": f"{enemy_type}.png", "attack": f"{enemy_type}_attack.png", "dead": f"{enemy_type}_dead.png"}
        self.image = self.images[self.state]
        self.attack_duration = 0

    def update(self):
        # Update enemy position and state
        if self.hp > 0:
            self.x += self.speed * self.direction
            if self.x > WIDTH - 100 or self.x < 500:
                self.direction *= -1

            if random.randint(0, 100) < 2:
                self.state = "attack"
                self.image = self.images[self.state]
                self.attack_duration = 15
                self.projectiles.append(Projectile(f"{self.enemy_type}_fireball", (self.x, self.y), -5))
            else:
                self.state = "normal"
                self.image = self.images[self.state]

        if self.attack_duration > 0:
            self.attack_duration -= 1
            if self.attack_duration <= 0:
                self.state = "normal"
                self.image = self.images[self.state]

        if self.hp <= 0:
            self.state = "dead"
            self.image = self.images[self.state]

        for projectile in self.projectiles:
            projectile.update()


# Fireball class
class Projectile(Actor):
    def __init__(self, image, pos, speed):
        super().__init__(image, pos)
        self.speed = speed

    def update(self):
        # Update projectile position
        self.x += self.speed


# Game menu and start screen
def draw_menu():
    screen.fill("black")
    screen.draw.text("Press SPACE to Start", center=(WIDTH // 2, HEIGHT // 2), color="white", fontsize=40)


def draw_hp_bar(entity, x, y):
    # Draw the HP bar for entities
    screen.draw.filled_rect(Rect((x, y), (entity.hp * 1.5, 20)), "red")
    screen.draw.rect(Rect((x, y), (300, 20)), "white")


# Game objects
enemy_types = ["enemy1", "enemy2", "enemy3"]
current_enemy = Enemy(enemy_types[0], (600, 550), 1)
player = Player("player1", (200, 550))


def update():
    global current_enemy, game_over, win, game_over_timer, win_timer

    if game_over or win:
        return

    player.update()
    current_enemy.update()

    for projectile in player.projectiles[:]:
        if projectile.colliderect(current_enemy):
            current_enemy.hp -= 25
            player.projectiles.remove(projectile)
            if current_enemy.hp <= 0:
                current_enemy.state = "dead"
                current_enemy.image = current_enemy.images["dead"]
                enemy_types.pop(0)  # New enemy
                if enemy_types:
                    current_enemy = Enemy(enemy_types[0], (600, 550), 1)
                else:
                    win = True
                    win_sound.play()
                    win_timer = 60
                    return

    for projectile in current_enemy.projectiles[:]:
        if projectile.colliderect(player):
            player.hp -= 10
            current_enemy.projectiles.remove(projectile)
            if player.hp <= 0:
                game_over = True
                game_over_sound.play()
                game_over_timer = 60
                return
            player_hit_sound.play()


def draw():
    global win_timer, game_over_timer

    screen.blit("background", (0, 0))
    player.draw()
    draw_hp_bar(player, 20, 20)
    current_enemy.draw()
    draw_hp_bar(current_enemy, WIDTH - 320, 20)

    for projectile in player.projectiles:
        projectile.draw()
    for projectile in current_enemy.projectiles:
        projectile.draw()

    if game_over:
        screen.draw.text("Game Over", center=(WIDTH // 2, HEIGHT // 2), color="red", fontsize=40)
        game_over_timer -= 1
        if game_over_timer <= 0:
            exit()

    if win:
        screen.draw.text("You Win!", center=(WIDTH // 2, HEIGHT // 2), color="green", fontsize=40)
        win_timer -= 1
        if win_timer <= 0:
            exit()


def on_key_down(key):
    if key == keys.SPACE:
        player.attack()
    else:
        player.move(keyboard)


pgzrun.go()
