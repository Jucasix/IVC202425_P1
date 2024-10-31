import cv2
import numpy as np

# Variável para armazenar a posição do objeto detectado
centro_objeto = None
video_running = True  # Flag para controlar a thread de captura de vídeo

def inicializar_window():
    # Inicializar janela de jogo e trackbars
    window_name = "Imagem Original"
    cv2.namedWindow(window_name)
    create_trackbar(window_name)
    return window_name

# Função pra criar as trackbars
def create_trackbar(window_name):
    cv2.createTrackbar('H Min', window_name, 44, 180, lambda x: None)
    cv2.createTrackbar('H Max', window_name, 73, 180, lambda x: None)
    cv2.createTrackbar('S Min', window_name, 0, 255, lambda x: None)
    cv2.createTrackbar('S Max', window_name, 255, 255, lambda x: None)
    cv2.createTrackbar('V Min', window_name, 158, 255, lambda x: None)
    cv2.createTrackbar('V Max', window_name, 255, 255, lambda x: None)

# Função pra detetar o objeto utilizando os valores HSV das trackbars
def detectar_objeto(frame, window_name):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Get dos valores das trackbars
    h_min = cv2.getTrackbarPos('H Min', window_name)
    h_max = cv2.getTrackbarPos('H Max', window_name)
    s_min = cv2.getTrackbarPos('S Min', window_name)
    s_max = cv2.getTrackbarPos('S Max', window_name)
    v_min = cv2.getTrackbarPos('V Min', window_name)
    v_max = cv2.getTrackbarPos('V Max', window_name)

    # Criar mascara usando os valores da trackbar
    lower_bound = np.array([h_min, s_min, v_min])
    upper_bound = np.array([h_max, s_max, v_max])
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    centro = None
    if len(contours) > 0:
        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            centro = (cX, cY)
            cv2.circle(frame, centro, 5, (0, 0, 255), -1)

    return centro, mask  # Retorna o centro de massa e a mask

# Função para capturar o vídeo em uma thread separada
def capturar_video():
    global centro_objeto, video_running
    cap = cv2.VideoCapture(0)

    window_name = inicializar_window()

    while video_running:
        ret, frame = cap.read()
        if not ret:
            break

        # Detectar o centro e a máscara
        centro, mask = detectar_objeto(frame, window_name)

        if centro is not None:
            centro_objeto = centro

        # Dar flip ao camera feed para dar match do movimento do jogador
        frame = cv2.flip(frame, 1)

        cv2.imshow(window_name, frame)

        # Dar flip ao mask feed para dar match do movimento do jogador
        mask = cv2.flip(mask, 1)

        cv2.imshow("Mascara", mask)  # Mascara segmentada

        # Controla para que a janela feche corretamente
        if cv2.waitKey(1) & 0xFF == ord('q'):
            video_running = False
            break

    cap.release()
    cv2.destroyAllWindows()