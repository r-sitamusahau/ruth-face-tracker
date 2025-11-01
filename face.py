import cv2
import time
import serial


arduino = serial.Serial('COM9', 9600)
time.sleep(2)  # Wait for Arduino to initialize

# Load Haar Cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Start video capture
cap = cv2.VideoCapture(0)

prev_cx, prev_cy = None, None
prev_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))

    current_time = time.time()
    time_diff = current_time - prev_time if prev_time else 1.0

    direction = ""
    speed = 0.0

    for (x, y, w, h) in faces:
        cx, cy = x + w // 2, y + h // 2
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        if prev_cx is not None:
            dx = cx - prev_cx
            if abs(dx) > 15:
                direction = "Left" if dx > 0 else "Right"
                distance = abs(dx)
                speed = distance / time_diff if time_diff > 0 else 0

                print(f"Direction: {direction}, Speed: {speed:.2f}")

                if direction == "Left":
                    arduino.write(b'L')
                elif direction == "Right":
                    arduino.write(b'R')

        prev_cx, prev_cy = cx, cy
        prev_time = current_time
        break

    cv2.putText(frame, f"Direction: {direction}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow('Face Tracker', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
arduino.close()
cv2.destroyAllWindows()