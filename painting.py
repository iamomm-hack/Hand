import cv2
import mediapipe as mp
import numpy as np

# MediaPipe Hand module initialize karte hain
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Webcam ko open karna
cap = cv2.VideoCapture(0)

# Painting properties
drawing = False  # Initially drawing off hai
last_x, last_y = None, None  # Starting point
pen_color = (0, 0, 255)  # Default color red hai
brush_size = 5  # Default brush size

# Loop for frame capture and hand tracking
while True:
    ret, frame = cap.read()  # Webcam se ek frame read karte hain
    if not ret:
        print("Failed to grab frame")
        break
    
    # Flip the frame (optional) for better user experience
    frame = cv2.flip(frame, 1)

    # Convert the frame to RGB (MediaPipe ka requirement hai)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Hand tracking karte hain
    results = hands.process(rgb_frame)

    # Agar hand detect hoti hai
    if results.multi_hand_landmarks:
        print("Hand landmarks detected")
        for landmarks in results.multi_hand_landmarks:
            # Hand landmarks ko draw karte hain
            mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Hand ke finger ke tips ka coordinates nikalte hain
            for id, landmark in enumerate(landmarks.landmark):
                # Finger tip (for example, index finger tip) ka coordinates
                if id == 8:  # Index finger tip
                    x = int(landmark.x * frame.shape[1])
                    y = int(landmark.y * frame.shape[0])
                    
                    # Drawing start ya stop ka logic (finger ke movement par)
                    if drawing and last_x is not None and last_y is not None:
                        print(f"Drawing line from ({last_x}, {last_y}) to ({x}, {y})")
                        cv2.line(frame, (last_x, last_y), (x, y), pen_color, brush_size)
                    
                    # Update the last position
                    last_x, last_y = x, y
                    drawing = True  # Start drawing
                else:
                    drawing = False  # Stop drawing if not on the finger tip

    # Show the frame with drawing
    cv2.imshow("Live Hand Painting", frame)

    # Key events (escape to exit, 'c' to clear, 'r' to reset color)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):  # Press 'q' to quit
        break
    if key == ord('c'):  # Press 'c' to clear screen
        frame = np.zeros_like(frame)  # Black background clear
    if key == ord('r'):  # Press 'r' to reset color
        pen_color = (0, 0, 255)  # Reset to red color

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()
