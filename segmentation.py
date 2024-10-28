import cv2
import numpy as np

# Função pra criar as trackbars
def create_trackbar(window_name):
    cv2.createTrackbar('H Min', window_name, 44, 180, lambda x: None)
    cv2.createTrackbar('H Max', window_name, 73, 180, lambda x: None)
    cv2.createTrackbar('S Min', window_name, 0, 255, lambda x: None)
    cv2.createTrackbar('S Max', window_name, 255, 255, lambda x: None)
    cv2.createTrackbar('V Min', window_name, 158, 255, lambda x: None)
    cv2.createTrackbar('V Max', window_name, 255, 255, lambda x: None)

# Função pra detetar o objeto utilizando os valores HSV das trackbars
def detectar_objeto(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Get dos valores das trackbars
    h_min = cv2.getTrackbarPos('H Min', 'Imagem Original')
    h_max = cv2.getTrackbarPos('H Max', 'Imagem Original')
    s_min = cv2.getTrackbarPos('S Min', 'Imagem Original')
    s_max = cv2.getTrackbarPos('S Max', 'Imagem Original')
    v_min = cv2.getTrackbarPos('V Min', 'Imagem Original')
    v_max = cv2.getTrackbarPos('V Max', 'Imagem Original')

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
