import pygame
import sys
import random

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 600, 400
GRID_SIZE = 40
ROWS, COLS = HEIGHT // GRID_SIZE, WIDTH // GRID_SIZE // 2
INFO_WIDTH = 300  # Ширина окна с информацией
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (169, 169, 169)
BLUE = (0, 0, 255)  # Цвет для поля восстановления

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Пошаговая игра-бродилка")

info_window = pygame.Surface((INFO_WIDTH, HEIGHT))

# Игрок
player_pos = [0, 0]
player_health = 100  # Здоровье игрока
player_defense = 5    # Защита игрока
player_weapon_damage = 20  # Урон от оружия
weapon_durability = 100   # Прочность оружия
armor_durability = 100    # Прочность брони
weapon_broken = False     # Флаг сломанного оружия
armor_broken = False      # Флаг сломанной брони
gold = 0                  # Количество золота
score = 100                 # Количество очков

# Настройка шрифта
font = pygame.font.Font(None, 36)

# Препятствия (объекты) с добавленным здоровьем
num_objects = random.randint(3, 10)

obstacles = {
    (1, 1): 50,
    (2, 2): 50,
    (3, 3): 50,
}

# Поле восстановления
recovery_area = pygame.Rect(4 * GRID_SIZE, 4 * GRID_SIZE, GRID_SIZE, GRID_SIZE)  # Пример области восстановления

recovery_area_point = [GRID_SIZE // 10, GRID_SIZE // 10]


def draw_grid():
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, BLACK, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, BLACK, (0, y), (WIDTH, y))

def draw_player():
    pygame.draw.rect(screen, GREEN, (player_pos[0] * GRID_SIZE, player_pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def draw_obstacles():
    for (x, y), health in obstacles.items():
        if health > 0:  # Отображаем только если здоровье больше 0
            pygame.draw.rect(screen, RED, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
            
# Отрисовка области восстановления
def draw_recovery_area():
    pygame.draw.rect(screen, BLUE, recovery_area)

def draw_fog_of_war():
    for x in range(COLS):
        for y in range(ROWS):
            if abs(x - player_pos[0]) > 1 or abs(y - player_pos[1]) > 1:
                pygame.draw.rect(screen, GRAY, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def can_move(new_pos):
    return obstacles.get(tuple(new_pos), 0) <= 0  # Проверяем, есть ли у препятствия здоровье больше 0

def check_victory():
    return all(health <= 0 for health in obstacles.values())  # Проверяем, остались ли объекты

# Основной игровой цикл
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            score -= 10 
            if score <= 0:
                score = 0
            new_pos = player_pos.copy()
            if event.key in (pygame.K_UP, pygame.K_w) and player_pos[1] > 0:
                new_pos[1] -= 1
            elif event.key in (pygame.K_DOWN, pygame.K_s) and player_pos[1] < ROWS - 1:
                new_pos[1] += 1
            elif event.key in (pygame.K_LEFT, pygame.K_a) and player_pos[0] > 0:
                new_pos[0] -= 1
            elif event.key in (pygame.K_RIGHT, pygame.K_d) and player_pos[0] < COLS - 1:
                new_pos[0] += 1
                
                # Проверка нахождения в области восстановления
            if recovery_area_point == new_pos:
                player_health = 100
                weapon_durability = 100   
                armor_durability = 100

            if can_move(new_pos):
                player_pos = new_pos
                
            else:
                # Уменьшение здоровья игрока с учетом защиты и прочности брони
                damage_taken = 10  # Исходный урон
                effective_damage = max(0, damage_taken + (5 - armor_durability // 10))  # Учитываем защиту и прочность брони
                player_health -= effective_damage  # Уменьшение здоровья игрока

                # Уменьшаем прочность брони (случайно от 0 до 5)
                armor_damage_taken = random.randint(0, 5)
                armor_durability = max(0, armor_durability - armor_damage_taken)  # Условие, чтобы не опустилось ниже 0

                if armor_durability <= 0:
                    armor_broken = True  # Броня сломана
                print(f"Вы столкнулись с препятствием! Урон: {effective_damage}, "
                      f"Здоровье: {player_health}, Прочность брони: {armor_durability}, "
                      f"Броня сломана: {armor_broken}")

                # Наносим урон объекту
                obs_position = tuple(new_pos)
                if obs_position in obstacles:
                    # Уменьшение урона от оружия с учетом прочности
                    if weapon_broken:
                        current_weapon_damage = 0  # Если оружие сломано, урон 0
                    else:
                        current_weapon_damage = max(0, player_weapon_damage - (5 - weapon_durability // 10))  # Учитываем прочность оружия

                    obstacles[obs_position] -= current_weapon_damage  # Уменьшение здоровья объекта на урон от оружия
                    
                    # Уменьшение прочности оружия (случайно от 0 до 5)
                    weapon_damage_taken = random.randint(0, 5)
                    weapon_durability = max(0, weapon_durability - weapon_damage_taken)  # Условие, чтобы не опустилось ниже 0

                    if weapon_durability <= 0:
                        weapon_broken = True  # Оружие сломано

                    print(f"Нанесен урон объекту! Прочность оружия: {weapon_durability}, "
                          f"Урон: {current_weapon_damage}, Оружие сломано: {weapon_broken}")

                    if obstacles[obs_position] <= 0:
                        gold_found = random.randint(5, 20)  # Случайное количество золота
                        gold += gold_found
                        score += 50
                        print(f"Объект на позиции {obs_position} уничтожен! Вы получили {gold_found} золота.")
                        print(f"Текущая сумма золота: {gold}")

                # Проверка, осталась ли жизнь у игрока
                if player_health <= 0:
                    print("Игра окончена! У вас не осталось здоровья.")
                    pygame.quit()
                    sys.exit()

                # Проверка на победу
                if check_victory():
                    print("Поздравляем! Вы победили, уничтожив все объекты.")
                    print("Итоговое количество очков:", score*gold)
                    pygame.quit()
                    sys.exit()

    # Очистка экрана
    screen.fill(WHITE)
    
    draw_grid()
    draw_obstacles()
    draw_player()
    draw_recovery_area()
    draw_fog_of_war()
    
    
    # Отрисовка окна с информацией
    info_window.fill(WHITE)
    health_text = font.render(f'Здоровье: {player_health}', True, BLACK)
    armor_text = font.render(f'Прочность брони: {armor_durability}', True, BLACK)
    weapon_text = font.render(f'Прочность оружия: {weapon_durability}', True, BLACK)
    gold_text = font.render(f'Золото: {gold}', True, BLACK)
    score_text = font.render(f'Очки: {score}', True, BLACK)

    # Рендеринг текста на "информационном окне"
    info_window.blit(health_text, (10, 10))
    info_window.blit(armor_text, (10, 50))
    info_window.blit(weapon_text, (10, 90))
    info_window.blit(gold_text, (10, 130))
    info_window.blit(score_text, (10, 160))

    # Отрисовка окна с информацией на основном экране
    screen.blit(info_window, (WIDTH - INFO_WIDTH, 0))
    
    pygame.display.flip()
    clock.tick(FPS)