import pyautogui
import time

while True:
    x, y = pyautogui.position()
    print(f"X: {x}, Y: {y}")
    time.sleep(0.5)