import pgzrun
import random
from pygame import Rect

# Game screen dimensions
WIDTH, HEIGHT = 800, 600

# Game state variables
game_over, win = False, False
game_over_timer, win_timer = 0, 0  # Message durations
game_started = False  # Game starts when SPACE is pressed

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
        self.images = {
            "normal": "player_female_idle",
            "attack": "player_female_attack",
            "dead": "player_female_dead",
            "jump": "player_female_jump",
            "run1": "player_female_run1",
            "run2": "player_female_run2"
        }
        self.image = self.images[self.state]
        self.run_frame = 0  # Koşma animasyonu için sayaç

    def move(self, keys):
        speed = 5  # Hız değeri
        if keys.left:
            self.x -= speed
            # Koşma animasyonu için geçiş
            self.run_frame += 0.1
            if self.run_frame >= 2:
                self.run_frame = 0
            if self.run_frame < 1:
                self.image = self.images["run1"]
            else:
                self.image = self.images["run2"]
            self.state = "run1"  # Sola doğru koşarken animasyonu
        elif keys.right:
            self.x += speed
            # Koşma animasyonu için geçiş
            self.run_frame += 0.1
            if self.run_frame >= 2:
                self.run_frame = 0
            if self.run_frame < 1:
                self.image = self.images["run1"]
            else:
                self.image = self.images["run2"]
            self.state = "run1"  # Sağa doğru koşarken animasyonu
        else:
            self.state = "normal"  # Duruş animasyonu

        if keys.up and self.on_ground:
            self.vy = -10
            self.on_ground = False
            self.state = "jump"  # Zıplama animasyonu

    def attack(self):
        if self.state != "dead" and not self.attacking:
            self.state = "attack"
            self.image = self.images[self.state]
            self.attack_duration = 20
            self.attacking = True
            self.projectiles.append(Projectile("player_female_fireball", (self.x, self.y - 20), 5))
            fireball_sound.play()

    def update(self, keys):
        # Hareket, zıplama ve saldırı animasyonları
        self.move(keys)
        self.vy += 0.5
        self.y += self.vy
        if self.y > HEIGHT - 50:
            self.y = HEIGHT - 50
            self.vy = 0
            self.on_ground = True

        # Zıplama ve saldırı animasyonları
        if self.state == "jump":
            self.image = self.images["jump"]
        elif self.attacking:
            self.attack_duration -= 1
            if self.attack_duration <= 0:
                self.attacking = False
                self.state = "normal"
                self.image = self.images[self.state]
        elif self.state != "attack" and self.state != "jump":
            self.image = self.images[self.state]

        # Ölüm durumu
        if self.hp <= 0:
            self.state = "dead"
            self.image = self.images[self.state]

        for projectile in self.projectiles:
            projectile.update()


# Enemy class
class Enemy(Actor):
    def __init__(self, enemy_type, pos, speed):
        super().__init__(f"{enemy_type}_idle.png", pos)
        self.speed, self.direction, self.hp = speed, 1, 150
        self.projectiles = []
        self.enemy_type = enemy_type
        self.state = "normal"
        self.images = {
            "normal": f"{enemy_type}_idle.png",
            "attack": f"{enemy_type}_attack.png",
            "dead": f"{enemy_type}_dead.png",
            "run": [f"{enemy_type}_walk1.png", f"{enemy_type}_walk2.png"]
        }
        self.image = self.images[self.state]
        self.attack_duration = 0
        self.run_frame = 0
        self.run_animation_speed = 0.1  # Slower animation speed for walking

    def update(self):
        # Update enemy position and state
        if self.hp > 0:
            self.x += self.speed * self.direction
            if self.x > WIDTH - 100 or self.x < 500:
                self.direction *= -1

            # Rakiplerin ateş etmesi için koşullu kısım
            if random.randint(0, 100) < 2:
                self.state = "attack"
                self.image = self.images[self.state]
                self.attack_duration = 15
                self.projectiles.append(Projectile(f"{self.enemy_type}_fireball", (self.x, self.y), -5))
            else:
                self.state = "normal"
                self.image = self.images[self.state]

        if self.state == "normal":
            self.run_frame += self.run_animation_speed
            if self.run_frame >= len(self.images["run"]):
                self.run_frame = 0
            self.image = self.images["run"][int(self.run_frame)]

        if self.attack_duration > 0:
            self.attack_duration -= 1
            if self.attack_duration <= 0:
                self.state = "normal"
                self.image = self.images[self.state]

        if self.hp <= 0:
            self.state = "dead"
            self.image = self.images["dead"]

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
    screen.draw.text("Press X to Start", center=(WIDTH // 2, HEIGHT // 2), color="white", fontsize=40)


def draw_hp_bar(entity, x, y):
    # Draw the HP bar for entities
    screen.draw.filled_rect(Rect((x, y), (entity.hp * 1.5, 20)), "red")
    screen.draw.rect(Rect((x, y), (300, 20)), "white")


# Game objects
enemy_types = ["enemy1", "enemy2"]
current_enemy = Enemy(enemy_types[0], (600, 550), 1)
player = Player("player_female_idle", (200, 550))


def update():
    global current_enemy, game_over, win, game_over_timer, win_timer, game_started

    if game_over or win:
        return

    if not game_started:
        return  # Menüdeyken oyunun güncellenmesi yapılmaz

    player.update(keyboard)  # Burada keyboard parametresini geçiyoruz.

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
    global win_timer, game_over_timer, game_started

    if not game_started:  # Menüdeyken sadece menü çizilecek
        draw_menu()
        return

    screen.blit("background1", (0, 0))  # Background change can be here
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
    global game_started
    if key == keys.X and not game_started:
        game_started = True
        return
    if key == keys.SPACE:
        player.attack()



pgzrun.go()
