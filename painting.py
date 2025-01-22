import cv2
import mediapipe as mp
import numpy as np

# Initialize Mediapipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Variables for drawing
canvas = None
drawing_color = (255, 0, 0)  # Blue color
brush_thickness = 8
palm_open_threshold = 0.8

# Helper function to detect if the palm is open
def is_palm_open(landmarks):
    if landmarks:
        distances = []
        for i in range(1, 5):  # Fingers 1-4
            distances.append(np.linalg.norm(np.array([landmarks[i].x, landmarks[i].y]) - \
                                       np.array([landmarks[i+4].x, landmarks[i+4].y])))
        average_distance = np.mean(distances)
        return average_distance > palm_open_threshold
    return False

# Open webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    if canvas is None:
        canvas = np.zeros_like(frame)

    # Convert frame to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame
    results = hands.process(frame_rgb)

    # Draw landmarks and track hand
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Check if the palm is open
            if is_palm_open(hand_landmarks.landmark):
                canvas = np.zeros_like(frame)  # Clear the canvas if palm is open

            else:
                # Get index finger tip (landmark 8)
                index_tip = hand_landmarks.landmark[8]
                x, y = int(index_tip.x * frame.shape[1]), int(index_tip.y * frame.shape[0])

                # Draw on the canvas
                cv2.circle(canvas, (x, y), brush_thickness, drawing_color, -1)

    # Merge canvas with the frame
    frame = cv2.addWeighted(frame, 0.5, canvas, 0.5, 0)

    # Display the result
    cv2.imshow('Drawing App', frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
hands.close()
cv2.destroyAllWindows()
