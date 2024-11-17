#This code is for simultaneous operation on raspberry pi
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
import socket
from time import sleep

factory = PiGPIOFactory()

# Create a Servo object on GPIO pin 18 (change if needed)
servo = Servo(18, pin_factory=factory)

# Socket setup
server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 12345))  
server_socket.listen(1)
print("Waiting for a connection...")

conn, addr = server_socket.accept()
print(f"Connection from {addr}")

try:
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        try:
            if data == 'rotate_servo_0':
                servo.value = 0  # 0 degrees position
            elif data == 'rotate_servo_120':
                servo.value = 1  # 120 degrees position
                #sleep(5)
        except ValueError:
            print("Invalid command received.")

except KeyboardInterrupt:
    print("Exiting...")
finally:
    servo.value = None  
    conn.close()
    server_socket.close()
    print("Connection closed.")
