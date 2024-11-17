from keras.models import load_model
import numpy as np
import cv2
import socket
import time

model = load_model("keras_model.h5", compile=False)
class_names = open("labels.txt", "r").readlines()


raspberry_pi_ip = '192.168.x.x' 
port = 12345

client_socket = socket.socket()
client_socket.connect((raspberry_pi_ip, port))

cap = cv2.VideoCapture(2)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

last_command = None

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        image = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)
        image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)
        image = (image / 127.5) - 1

        try:
            prediction = model.predict(image)
            index = np.argmax(prediction)
            class_name = class_names[index].strip()
            confidence_score = prediction[0][index]

            output_text = f"Category: {class_name}, Confidence: {confidence_score:.2f}"
            cv2.putText(frame, output_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # Control the servo based on class prediction only if confidence is greater than 80%
            if confidence_score > 0.80:  # Confidence threshold
                command = b'rotate_servo_120' if index in [0, 1, 4] else b'rotate_servo_0'
                if command != last_command:
                    client_socket.sendall(command)
                    last_command = command

        except Exception as e:
            print(f"Error during prediction: {e}")

        cv2.imshow('Live Camera Feed', frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Interrupted by user.")

finally:
    cap.release()
    cv2.destroyAllWindows()
    client_socket.close()
    print("Connection closed.")
