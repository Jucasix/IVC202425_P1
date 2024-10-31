import cv2
import numpy as np

# Global variables
centro_objeto = None
video_running = True  # Flag to control video capture thread
selected_hsv_color = None  # Variable to store clicked HSV color
frame = np.zeros((480, 640, 3), dtype=np.uint8)  # Initialize frame as a blank image

def inicializar_window():
    # Initialize game window and trackbars
    window_name = "Imagem Original"
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, click_event)  # Set mouse callback for color selection
    create_trackbar(window_name)
    return window_name

# Function to create trackbars
def create_trackbar(window_name):
    global selected_hsv_color

    h_min_d = 15
    h_max_d = 40
    s_min_d = 110
    s_max_d = 255
    v_min_d = 155
    v_max_d = 255
    cv2.createTrackbar('H Min', window_name, 15, 180, lambda x: None)
    cv2.createTrackbar('H Max', window_name, 40, 180, lambda x: None)
    cv2.createTrackbar('S Min', window_name, 110, 255, lambda x: None)
    cv2.createTrackbar('S Max', window_name, 255, 255, lambda x: None)
    cv2.createTrackbar('V Min', window_name, 155, 255, lambda x: None)
    cv2.createTrackbar('V Max', window_name, 255, 255, lambda x: None)

    selected_hsv_color = [(int)(h_min_d+h_max_d)/2,(int)(s_min_d+s_max_d)/2,(int)(v_min_d+v_max_d)/2]

# Function to set trackbar positions based on HSV color
def set_trackbar_values(h, s, v, window_name):
    global selected_hsv_color
    # Cast to int to prevent overflow in np.uint8 values
    h, s, v = int(h), int(s), int(v)

    cv2.setTrackbarPos('H Min', window_name, max(h - 5, 0))
    cv2.setTrackbarPos('H Max', window_name, min(h + 5, 180))
    cv2.setTrackbarPos('S Min', window_name, max(s - 20, 0))
    cv2.setTrackbarPos('S Max', window_name, min(s + 20, 255))
    cv2.setTrackbarPos('V Min', window_name, max(v - 20, 0))
    cv2.setTrackbarPos('V Max', window_name, min(v + 20, 255))

    display_selected_color = [h,s,v]

# Function to display selected color
def display_selected_color(h, s, v):
    global frame
    color_bgr = cv2.cvtColor(np.uint8([[[h, s, v]]]), cv2.COLOR_HSV2BGR)[0][0]
    cv2.rectangle(frame, (10, 10), (60, 60), color_bgr.tolist(), -1)  # Draw color square at top-left

# Function to detect object using HSV trackbar values
def detectar_objeto(frame, window_name):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Get trackbar values
    h_min = cv2.getTrackbarPos('H Min', window_name)
    h_max = cv2.getTrackbarPos('H Max', window_name)
    s_min = cv2.getTrackbarPos('S Min', window_name)
    s_max = cv2.getTrackbarPos('S Max', window_name)
    v_min = cv2.getTrackbarPos('V Min', window_name)
    v_max = cv2.getTrackbarPos('V Max', window_name)

    # Create mask using trackbar values
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

    return centro, mask  # Return center of mass and mask

# Function to handle mouse clicks
def click_event(event, x, y, flags, param):
    global selected_hsv_color, frame

    # Only process left mouse button click
    if event == cv2.EVENT_LBUTTONDOWN and frame is not None and frame.size != 0:
        # Convert the clicked BGR color to HSV
        clicked_color_bgr = frame[y, x]
        clicked_color_hsv = cv2.cvtColor(np.uint8([[clicked_color_bgr]]), cv2.COLOR_BGR2HSV)
        selected_hsv_color = clicked_color_hsv[0][0]

        # Update trackbars based on clicked HSV values
        h, s, v = selected_hsv_color
        set_trackbar_values(h, s, v, "Imagem Original")
        print("Clicked HSV color:", selected_hsv_color)

# Função para capturar o vídeo em uma thread separada
def capturar_video():
    global centro_objeto, video_running, frame
    cap = cv2.VideoCapture(0)

    window_name = inicializar_window()

    while video_running:
        ret, frame = cap.read()
        if not ret:
            break

        # Detect center and mask
        centro, mask = detectar_objeto(frame, window_name)

        if centro is not None:
            centro_objeto = centro

        # Flip camera feed to match player movement
        frame = cv2.flip(frame, 1)

        # Display the frame and the selected color square
        display_selected_color(*selected_hsv_color) if selected_hsv_color is not None else None
        cv2.imshow(window_name, frame)

        # Flip mask feed to match player movement
        mask = cv2.flip(mask, 1)
        cv2.imshow("Mascara", mask)  # Segmented mask

        # Controla para que a janela feche corretamente
        if cv2.waitKey(1) & 0xFF == ord('q'):
            video_running = False
            break

    cap.release()
    cv2.destroyAllWindows()