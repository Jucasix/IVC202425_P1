import pygame
import cv2
import segmentation  # Importar funções de segmentação
import threading
import numpy as np

pygame.init()

screen_width = 600
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Breakout')

#define font
font = pygame.font.SysFont('Constantia', 30)

#define colours
bg = (234, 218, 184)
block_red = (242, 85, 96)
block_green = (86, 174, 87)
block_blue = (69, 177, 232)
paddle_col = (142, 135, 123)
paddle_outline = (100, 100, 100)
text_col = (78, 81, 139)

#define game variables
cols = 6
rows = 6
clock = pygame.time.Clock()
fps = 60
live_ball = False
game_over = 0

#function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def readme_window(window_name="README", width=600, height=300, font_scale=0.6, color=(255, 255, 255), thickness=1):
    image = np.zeros((height,width, 3), dtype=np.uint8)

    font = cv2.FONT_HERSHEY_SIMPLEX

    text1 = "Cor por defeito esta definida como um tom de verde."
    text2 = "Alterar cor clicando num objeto no frame da camera"
    text3 = "ou utilizando as trackbars."

    text_x = 25
    text_y1 = 100
    text_y2 = 150
    text_y3 = 200

    cv2.putText(image, text1, (text_x, text_y1), font, font_scale, color, thickness, lineType=cv2.LINE_AA)
    cv2.putText(image, text2, (text_x, text_y2), font, font_scale, color, thickness, lineType=cv2.LINE_AA)
    cv2.putText(image, text3, (text_x, text_y3), font, font_scale, color, thickness, lineType=cv2.LINE_AA)

    cv2.imshow(window_name, image)

# Classe wall para os blocos
class wall():
    def __init__(self):
        self.width = screen_width // cols
        self.height = 50

    def create_wall(self):
        self.blocks = []
        for row in range(rows):
            block_row = []
            for col in range(cols):
                block_x = col * self.width
                block_y = row * self.height
                rect = pygame.Rect(block_x, block_y, self.width, self.height)
                if row < 2:
                    strength = 3
                elif row < 4:
                    strength = 2
                elif row < 6:
                    strength = 1
                block_row.append([rect, strength])
            self.blocks.append(block_row)

    def draw_wall(self):
        for row in self.blocks:
            for block in row:
                if block[1] == 3:
                    block_col = block_blue
                elif block[1] == 2:
                    block_col = block_green
                elif block[1] == 1:
                    block_col = block_red
                pygame.draw.rect(screen, block_col, block[0])
                pygame.draw.rect(screen, bg, (block[0]), 2)

# Paddle com correção da direção
class paddle():
    def __init__(self):
        self.reset()

    # Função para mover a barra com base na posição x do objeto verde
    def move_to_position(self, x):
        # Inverter a direção do movimento usando screen_width
        inverted_x = screen_width - x
        self.rect.x = inverted_x - self.width // 2  # Centraliza a barra na posição do objeto

        # Limitar o paddle para não sair da tela
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width

    def draw(self):
        pygame.draw.rect(screen, paddle_col, self.rect)
        pygame.draw.rect(screen, paddle_outline, self.rect, 3)

    def reset(self):
        self.height = 20
        self.width = int(screen_width / cols)
        self.x = int((screen_width / 2) - (self.width / 2))
        self.y = screen_height - (self.height * 2)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

# Classe ball para a bola
class game_ball():
    def __init__(self, x, y):
        self.reset(x, y)

    def move(self):
        # Atualiza a posição da bola
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Colisões com as paredes
        if self.rect.left < 0 or self.rect.right > screen_width:
            self.speed_x *= -1
        if self.rect.top < 0:
            self.speed_y *= -1
        if self.rect.bottom > screen_height:
            self.game_over = -1  # Jogo perdido

        # Verifica colisão com o paddle
        if self.rect.colliderect(player_paddle.rect):
            # Colide de baixo para cima, inverte a velocidade y
            if abs(self.rect.bottom - player_paddle.rect.top) < 10 and self.speed_y > 0:
                self.speed_y *= -1

        # Verifica colisão com os blocos
        for row in wall.blocks:
            for block in row:
                # Se o bloco ainda existe (tem uma área definida)
                if block[1] > 0:
                    if self.rect.colliderect(block[0]):
                        # Verifica a direção da colisão e ajusta o movimento da bola
                        if abs(self.rect.right - block[0].left) < 10 or abs(self.rect.left - block[0].right) < 10:
                            self.speed_x *= -1
                        if abs(self.rect.bottom - block[0].top) < 10 or abs(self.rect.top - block[0].bottom) < 10:
                            self.speed_y *= -1

                        # Diminui a força do bloco
                        block[1] -= 1
                        if block[1] == 0:
                            block[0] = pygame.Rect(0, 0, 0, 0)  # "Destrói" o bloco ao zerar seu retângulo

        return self.game_over

    def draw(self):
        pygame.draw.circle(screen, paddle_col, (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad), self.ball_rad)
        pygame.draw.circle(screen, paddle_outline, (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad), self.ball_rad, 3)

    def reset(self, x, y):
        self.ball_rad = 10
        self.x = x - self.ball_rad
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, self.ball_rad * 2, self.ball_rad * 2)
        self.speed_x = 4
        self.speed_y = -4
        self.speed_max = 5
        self.game_over = 0

# Inicializar o jogo
wall = wall()
wall.create_wall()
player_paddle = paddle()
ball = game_ball(player_paddle.x + (player_paddle.width // 2), player_paddle.y - player_paddle.height)

# Iniciar a captura de vídeo em uma thread separada
thread_video = threading.Thread(target=segmentation.capturar_video)
thread_video.start()
readme_window()

# Loop principal do jogo
run = True
while run:
    clock.tick(fps)
    screen.fill(bg)

    # Usar a posição detectada do objeto verde para mover a barra
    if segmentation.centro_objeto is not None:
        player_paddle.move_to_position(segmentation.centro_objeto[0])

    # Desenhar todos os elementos do jogo
    wall.draw_wall()
    player_paddle.draw()
    ball.draw()

    # Movimento da bola
    if live_ball:
        game_over = ball.move()
        if game_over != 0:
            live_ball = False

    # Texto de início e reinício do jogo
    if not live_ball:
        if game_over == 0:
            draw_text('CLICK ANYWHERE TO START', font, text_col, 100, screen_height // 2 + 100)
        elif game_over == 1:
            draw_text('YOU WON!', font, text_col, 240, screen_height // 2 + 50)
            draw_text('CLICK ANYWHERE TO START', font, text_col, 100, screen_height // 2 + 100)
        elif game_over == -1:
            draw_text('YOU LOST!', font, text_col, 240, screen_height // 2 + 50)
            draw_text('CLICK ANYWHERE TO START', font, text_col, 100, screen_height // 2 + 100)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and live_ball == False:
            live_ball = True
            ball.reset(player_paddle.x + (player_paddle.width // 2), player_paddle.y - player_paddle.height)
            player_paddle.reset()
            wall.create_wall()

    pygame.display.update()

# Finalizar a thread de captura de vídeo e fechar as janelas
video_running = False
thread_video.join()
pygame.quit()
