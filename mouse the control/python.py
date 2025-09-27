import cv2
import mediapipe as mp
import pyautogui
import threading
import tkinter as tk

# Screen size
screen_width, screen_height = pyautogui.size()

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
running = True

left_clicked = False
right_clicked = False

def close_app():
    global running
    running = False

def opencv_loop():
    global running, left_clicked, right_clicked
    while running:
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                lm_list = []
                for id, lm in enumerate(handLms.landmark):
                    h, w, c = img.shape
                    lm_list.append((int(lm.x * w), int(lm.y * h)))

                if len(lm_list) >= 13:
                    # Move mouse with index finger tip
                    x, y = lm_list[8]
                    screen_x = int(x * screen_width / w)
                    screen_y = int(y * screen_height / h)
                    pyautogui.moveTo(screen_x, screen_y)

                    # Left click: thumb tip (4) close to index tip (8)
                    thumb_x, thumb_y = lm_list[4]
                    if abs(x - thumb_x) < 40 and abs(y - thumb_y) < 40:
                        if not left_clicked:
                            pyautogui.click(button='left')
                            left_clicked = True
                    else:
                        left_clicked = False

                    # Right click: thumb tip (4) close to middle tip (12)
                    mid_x, mid_y = lm_list[12]
                    if abs(mid_x - thumb_x) < 40 and abs(mid_y - thumb_y) < 40:
                        if not right_clicked:
                            pyautogui.click(button='right')
                            right_clicked = True
                    else:
                        right_clicked = False

                mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

        cv2.imshow("Hand Mouse Control", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False
            break

    cap.release()
    cv2.destroyAllWindows()

# Start OpenCV in a separate thread
opencv_thread = threading.Thread(target=opencv_loop)
opencv_thread.start()

# Create Tkinter window with Close button
root = tk.Tk()
root.title("Close Hand Mouse Control")
root.geometry("200x100")
close_btn = tk.Button(root, text="Close", command=close_app)
close_btn.pack(expand=True)

root.mainloop()