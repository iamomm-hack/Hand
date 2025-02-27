import cv2
import mediapipe as mp
import serverCom

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

prev_y_position = {}

INDEX_FINGER_TIP = 8
MIDDLE_FINGER_TIP = 12
TRACKED_FINGERS = [INDEX_FINGER_TIP, MIDDLE_FINGER_TIP]

ESP_SERVER = "http://192.168.15.15"  # Replace with actual ESP server IP

def detect_finger_movement(hand_id, finger_id, curr_y):
    global prev_y_position
    direction = None
    if hand_id not in prev_y_position:
        prev_y_position[hand_id] = {}
    if finger_id in prev_y_position[hand_id]:
        if curr_y < prev_y_position[hand_id][finger_id] - 0.05:
            direction = "up"
        elif curr_y > prev_y_position[hand_id][finger_id] + 0.05:
            direction = "down"
    prev_y_position[hand_id][finger_id] = curr_y
    return direction

def send_servo_command(servo, position):
    try:
        serverCom.get(f"{ESP_SERVER}/?{servo}={position}")
    except serverCom.exceptions.RequestException as e:
        print("Error sending request:", e)

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    
    frame_width = frame.shape[1]
    center_x = frame_width // 2
    cv2.line(frame, (center_x, 0), (center_x, frame.shape[0]), (0, 255, 0), 2)
    
    if results.multi_hand_landmarks:
        for hand_id, hand_landmarks in enumerate(results.multi_hand_landmarks):
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            index_finger_tip_x = int(hand_landmarks.landmark[INDEX_FINGER_TIP].x * frame_width)
            hand_side = "Left" if index_finger_tip_x < center_x else "Right"
            
            for finger_id in TRACKED_FINGERS:
                curr_y = hand_landmarks.landmark[finger_id].y
                movement = detect_finger_movement(hand_id, finger_id, curr_y)
                
                if movement == "up":
                    servo = "servo1" if hand_side == "Left" else "servo2"
                    print(f"🔼 {hand_side} Window Opening ({'Index' if finger_id == INDEX_FINGER_TIP else 'Middle'} Finger)")
                    send_servo_command(servo, 180)
                elif movement == "down":
                    servo = "servo1" if hand_side == "Left" else "servo2"
                    print(f"🔽 {hand_side} Window Closing ({'Index' if finger_id == INDEX_FINGER_TIP else 'Middle'} Finger)")
                    send_servo_command(servo, 0)
    
    cv2.imshow("Hand Gesture Window Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
