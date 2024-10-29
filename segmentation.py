import cv2
import numpy as np

# Função para detectar o centro de massa do objeto verde e retornar a máscara
def detectar_objeto(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_green = np.array([40, 50, 50])
    upper_green = np.array([80, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)
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

    return centro, mask

# Função para criar trackbars (ajuste conforme necessário para sliders específicos)
def create_trackbar(window_name):
    cv2.createTrackbar("LowH", window_name, 40, 179, lambda x: None)
    cv2.createTrackbar("HighH", window_name, 80, 179, lambda x: None)
    cv2.createTrackbar("LowS", window_name, 50, 255, lambda x: None)
    cv2.createTrackbar("HighS", window_name, 255, 255, lambda x: None)
    cv2.createTrackbar("LowV", window_name, 50, 255, lambda x: None)
    cv2.createTrackbar("HighV", window_name, 255, 255, lambda x: None)

# Função para capturar o vídeo e processar o objeto em uma thread separada
def capturar_video(centro_callback, video_running):
    cap = cv2.VideoCapture(0)

    # Inicializar janela de jogo e trackbars
    window_name = "Imagem Original"
    cv2.namedWindow(window_name)
    create_trackbar(window_name)

    while video_running.is_set():
        ret, frame = cap.read()
        if not ret:
            break

        # Detectar o centro e a máscara
        centro, mask = detectar_objeto(frame)

        if centro is not None:
            centro_callback(centro)

        # Dar flip ao camera feed para dar match do movimento do jogador
        frame = cv2.flip(frame, 1)
        cv2.imshow(window_name, frame)

        # Dar flip ao mask feed para dar match do movimento do jogador
        mask = cv2.flip(mask, 1)
        cv2.imshow("Mascara", mask)

        # Controla para que a janela feche corretamente
        if cv2.waitKey(1) & 0xFF == ord('q'):
            video_running.clear()
            break

    cap.release()
    cv2.destroyAllWindows()
