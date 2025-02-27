import requests
import cv2
import mediapipe as mp

ESP_SERVER = "http://192.168.15.15"

def set_servo1_position(position):
    url = f"{ESP_SERVER}/?servo1={position}&"
    requests.get(url)

def set_servo2_position(position):
    url = f"{ESP_SERVER}/?servo2={position}&"
    requests.get(url)

def set_both_servos(position):
    url = f"{ESP_SERVER}/?bothServo={position}&"
    requests.get(url)

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

prev_y_position = {}
INDEX_FINGER_TIP = 8
MIDDLE_FINGER_TIP = 12
TRACKED_FINGERS = [INDEX_FINGER_TIP, MIDDLE_FINGER_TIP]

cap = cv2.VideoCapture(0)
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame_width = frame.shape[1]
    center_x = frame_width // 2
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    cv2.line(frame, (center_x, 0), (center_x, frame.shape[0]), (0, 255, 0), 2)

    if results.multi_hand_landmarks:
        for hand_id, hand_landmarks in enumerate(results.multi_hand_landmarks):
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            index_finger_tip_x = int(hand_landmarks.landmark[INDEX_FINGER_TIP].x * frame_width)
            hand_side = "Left" if index_finger_tip_x < center_x else "Right"

            for finger_id in TRACKED_FINGERS:
                curr_y = hand_landmarks.landmark[finger_id].y
                if curr_y < 0.4:  # Threshold for UP gesture
                    set_both_servos(180)
                    print(f"🔼 {hand_side} Window Fully Opened")
                elif curr_y > 0.6:  # Threshold for DOWN gesture
                    set_both_servos(0)
                    print(f"🔽 {hand_side} Window Fully Closed")

    cv2.imshow("Hand Gesture Window Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
