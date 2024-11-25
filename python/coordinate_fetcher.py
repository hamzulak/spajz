import pyautogui
import keyboard
import time

print("Move your mouse to the desired position and press 'Enter'.")

while True:
    if keyboard.is_pressed('enter'):  # Check if 'Enter' is pressed
        x, y = pyautogui.position()
        print(f"Mouse position: x={x}, y={y}")
        break  # Exit the loop after printing the coordinates
    time.sleep(0.1)  # Sleep briefly to avoid high CPU usage
