import requests
import cv2
import mediapipe as mp
import time
import threading

ESP_SERVER = "http://192.168.249.15"

def set_servo_position(side, position):
    servo_param = "servo1" if side == "Left" else "servo2"
    url = f"{ESP_SERVER}/?{servo_param}={position}&"
    threading.Thread(target=requests.get, args=(url,), daemon=True).start()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)
cap = cv2.VideoCapture(0)

prev_angle = {"Left": 90, "Right": 90}  # Start at 90 degrees
last_update_time = {"Left": time.time(), "Right": time.time()}
debounce_interval = 0.1  # 100ms debounce interval

def smooth_angle_change(current_angle, target_angle, step=3):
    if current_angle < target_angle:
        return min(target_angle, current_angle + step)
    elif current_angle > target_angle:
        return max(target_angle, current_angle - step)
    return current_angle

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    frame_width = frame.shape[1]
    center_x = frame_width // 2
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    current_time = time.time()
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            index_finger_x = int(hand_landmarks.landmark[8].x * frame_width)
            hand_side = "Left" if index_finger_x < center_x else "Right"
            
            if current_time - last_update_time[hand_side] < debounce_interval:
                continue  # Skip update if debounce interval not met
            
            last_update_time[hand_side] = current_time  # Update last change timestamp
            
            thumb_tip = hand_landmarks.landmark[4].y
            index_tip = hand_landmarks.landmark[8].y
            middle_tip = hand_landmarks.landmark[12].y
            ring_tip = hand_landmarks.landmark[16].y
            pinky_tip = hand_landmarks.landmark[20].y
            palm_base = hand_landmarks.landmark[0].y
            
            extended_fingers = sum(tip < palm_base for tip in [thumb_tip, index_tip, middle_tip, ring_tip, pinky_tip])
            
            is_open_hand = extended_fingers >= 4
            is_fist = extended_fingers == 0
            
            target_angle = prev_angle[hand_side]
            if is_open_hand:
                target_angle = min(180, prev_angle[hand_side] + 5)
                print(f"{hand_side} Hand Open - Increasing Angle: {target_angle}")
            elif is_fist:
                target_angle = max(0, prev_angle[hand_side] - 5)
                print(f"{hand_side} Hand Fist - Decreasing Angle: {target_angle}")
            else:
                print(f"{hand_side} Hand in Neutral Position")
                continue  # Skip if neither open hand nor fist detected
            
            smoothed_angle = smooth_angle_change(prev_angle[hand_side], target_angle)
            if smoothed_angle != prev_angle[hand_side]:  # Only send request if angle changed
                prev_angle[hand_side] = smoothed_angle
                set_servo_position(hand_side, smoothed_angle)
    
    cv2.imshow("Hand Gesture Window Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
