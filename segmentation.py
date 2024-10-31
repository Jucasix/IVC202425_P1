import cv2
import numpy as np

# Global variables
centro_objeto = None
video_running = True  # Flag to control video capture thread
cor_selecionada_hsv = None  # Variable to store clicked HSV color
frame = np.zeros((480, 640, 3), dtype=np.uint8)  # Initialize frame as a blank image

def inicializar_window():
    # Initialize game window and trackbars
    window_name = "Imagem Original"
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, click_selecionar_cor) 
    inicializar_trackbars(window_name)
    return window_name

# Função para inicializar trackbars
def inicializar_trackbars(window_name):
    h_d = 102
    s_d = 81
    v_d = 83

    cv2.createTrackbar('H Min', window_name, max(h_d - 5, 0) , 180, lambda x: None)
    cv2.createTrackbar('H Max', window_name, min(h_d + 5, 180), 180, lambda x: None)
    cv2.createTrackbar('S Min', window_name, max(s_d - 20, 0), 255, lambda x: None)
    cv2.createTrackbar('S Max', window_name, max(s_d + 20, 0), 255, lambda x: None)
    cv2.createTrackbar('V Min', window_name, max(v_d - 20, 0), 255, lambda x: None)
    cv2.createTrackbar('V Max', window_name, max(v_d - 20, 0), 255, lambda x: None)

    set_valores_trackbar(102, 81, 83, "Imagem Original")

# Função para definir os valores da trackbar (usado para o click event)
def set_valores_trackbar(h, s, v, window_name):
    global cor_selecionada_hsv
    h, s, v = int(h), int(s), int(v)

    cv2.setTrackbarPos('H Min', window_name, max(h - 5, 0))
    cv2.setTrackbarPos('H Max', window_name, min(h + 5, 180))
    cv2.setTrackbarPos('S Min', window_name, max(s - 20, 0))
    cv2.setTrackbarPos('S Max', window_name, min(s + 20, 255))
    cv2.setTrackbarPos('V Min', window_name, max(v - 20, 0))
    cv2.setTrackbarPos('V Max', window_name, min(v + 20, 255))

# Função para detetar e segmentar o objeto consoante os valores da trackbar
def detectar_objeto(frame, window_name):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Get dos valores da trackbar
    h_min = cv2.getTrackbarPos('H Min', window_name)
    h_max = cv2.getTrackbarPos('H Max', window_name)
    s_min = cv2.getTrackbarPos('S Min', window_name)
    s_max = cv2.getTrackbarPos('S Max', window_name)
    v_min = cv2.getTrackbarPos('V Min', window_name)
    v_max = cv2.getTrackbarPos('V Max', window_name)

    # Criar mascara com os valores da trackbar
    lower_bound = np.array([h_min, s_min, v_min])
    upper_bound = np.array([h_max, s_max, v_max])
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    # Criar contours
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

    return centro, mask  # Return center of mass and mask

# Função que recebe o click event e aplica a cor nas trackbars
def click_selecionar_cor(event, x, y, flags, param):
    global cor_selecionada_hsv, frame

    if event == cv2.EVENT_LBUTTONDOWN and frame is not None and frame.size != 0:
        # Converter cor BGR para HSV
        clicked_color_bgr = frame[y, x]
        clicked_color_hsv = cv2.cvtColor(np.uint8([[clicked_color_bgr]]), cv2.COLOR_BGR2HSV)
        cor_selecionada_hsv = clicked_color_hsv[0][0]

        # Atualizar trackbars com novos valores HSV
        h, s, v = cor_selecionada_hsv
        set_valores_trackbar(h, s, v, "Imagem Original")
        print("Clicked HSV color:", cor_selecionada_hsv)

# Função para capturar o vídeo em uma thread separada
def capturar_video():
    global centro_objeto, video_running, frame
    cap = cv2.VideoCapture(0)

    window_name = inicializar_window()

    while video_running:
        ret, frame = cap.read()
        if not ret:
            break

        # Receber centro de massa e mascara de segmentação
        centro, mask = detectar_objeto(frame, window_name)

        if centro is not None:
            centro_objeto = centro

        # Inverter camera para igualar movimento da camera
        frame = cv2.flip(frame, 1)
        cv2.imshow(window_name, frame)

        # Inverter mascara para igualar movimento da camera
        mask = cv2.flip(mask, 1)
        cv2.imshow("Mascara", mask)

        # Controla para que a janela feche corretamente
        if cv2.waitKey(1) & 0xFF == ord('q'):
            video_running = False
            break

    cap.release()
    cv2.destroyAllWindows()