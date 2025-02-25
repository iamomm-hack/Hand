import cv2
import mediapipe as mp

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Store previous positions for movement detection
prev_y_position = {}

# Define finger landmarks for Index and Middle Finger
INDEX_FINGER_TIP = 8   # Index Finger Tip
MIDDLE_FINGER_TIP = 12  # Middle Finger Tip
TRACKED_FINGERS = [INDEX_FINGER_TIP, MIDDLE_FINGER_TIP]  # Only track these two

# Function to detect movement direction for index and middle finger
def detect_finger_movement(hand_id, finger_id, curr_y):
    global prev_y_position
    direction = None

    if hand_id not in prev_y_position:
        prev_y_position[hand_id] = {}

    if finger_id in prev_y_position[hand_id]:
        if curr_y < prev_y_position[hand_id][finger_id] - 0.05:  # Moving Up
            direction = "up"
        elif curr_y > prev_y_position[hand_id][finger_id] + 0.05:  # Moving Down
            direction = "down"

    prev_y_position[hand_id][finger_id] = curr_y  # Update position
    return direction

# Open webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally for a mirror effect
    frame = cv2.flip(frame, 1)

    # Get frame width
    frame_width = frame.shape[1]
    center_x = frame_width // 2  # Midpoint of the screen

    # Convert BGR to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    # Draw the center dividing line
    cv2.line(frame, (center_x, 0), (center_x, frame.shape[0]), (0, 255, 0), 2)

    if results.multi_hand_landmarks:
        for hand_id, hand_landmarks in enumerate(results.multi_hand_landmarks):
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get index finger tip position to determine screen side
            index_finger_tip_x = int(hand_landmarks.landmark[INDEX_FINGER_TIP].x * frame_width)
            hand_side = "Left" if index_finger_tip_x < center_x else "Right"

            # Check only Index & Middle Finger movements
            for finger_id in TRACKED_FINGERS:
                curr_y = hand_landmarks.landmark[finger_id].y
                movement = detect_finger_movement(hand_id, finger_id, curr_y)

                # Assign actions based on finger and movement
                if movement == "up":
                    if finger_id == INDEX_FINGER_TIP:
                        print(f"🔼 {hand_side} Window Opening (Index Finger)")
                    elif finger_id == MIDDLE_FINGER_TIP:
                        print(f"🔼 {hand_side} Window Opening (Middle Finger)")

                elif movement == "down":
                    if finger_id == INDEX_FINGER_TIP:
                        print(f"🔽 {hand_side} Window Closing (Index Finger)")
                    elif finger_id == MIDDLE_FINGER_TIP:
                        print(f"🔽 {hand_side} Window Closing (Middle Finger)")

    # Display the frame
    cv2.imshow("Hand Gesture Window Control", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
