import cv2
import mediapipe as mp
import time
import pyautogui
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from collections import deque

# ---------- Swipe tracking ----------
wrist_x_history = deque(maxlen=10)
swipe_threshold = 0.25
swipe_cooldown = 1.0
last_swipe_time = 0

# ---------- Setup pycaw (volume control) ----------
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
current_vol = volume.GetMasterVolumeLevelScalar()

# ---------- Setup MediaPipe ----------
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)

FINGER_TIPS = [8, 12, 16, 20]
FINGER_PIPS = [6, 10, 14, 18]

last_action_time = 0
cooldown = 1.5

prev_wrist_y = None
vol_change_threshold = 0.015

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    gesture_text = "No hand"

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            landmarks = hand_landmarks.landmark

            # ---------- Fist detection (play/pause) ----------
            fingers_curled = 0
            for tip_id, pip_id in zip(FINGER_TIPS, FINGER_PIPS):
                if landmarks[tip_id].y > landmarks[pip_id].y:
                    fingers_curled += 1

            print(f"Fingers curled: {fingers_curled}")  # DEBUG

            if fingers_curled == 4:
                gesture_text = "FIST detected"
                current_time = time.time()
                if current_time - last_action_time > cooldown:
                    print("Play/Pause triggered!")
                    pyautogui.press('playpause')
                    last_action_time = current_time

            else:
                gesture_text = "Open hand"

                # ---------- Volume control ----------
                wrist_y = landmarks[0].y

                if prev_wrist_y is not None:
                    delta = prev_wrist_y - wrist_y

                    if abs(delta) > vol_change_threshold:
                        current_vol = volume.GetMasterVolumeLevelScalar()

                        if delta > 0:
                            new_vol = min(current_vol + 0.03, 1.0)
                            gesture_text = "Volume UP"
                        else:
                            new_vol = max(current_vol - 0.03, 0.0)
                            gesture_text = "Volume DOWN"

                        volume.SetMasterVolumeLevelScalar(new_vol, None)

                prev_wrist_y = wrist_y

                # ---------- Swipe detection ----------
                wrist_x = landmarks[0].x
                wrist_x_history.append(wrist_x)

                print(f"History length: {len(wrist_x_history)}")  # DEBUG

                if len(wrist_x_history) == wrist_x_history.maxlen:
                    movement = wrist_x_history[-1] - wrist_x_history[0]
                    print(f"Swipe movement: {movement:.3f}")  # DEBUG

                    current_time = time.time()
                    if abs(movement) > swipe_threshold and (current_time - last_swipe_time) > swipe_cooldown:
                        if movement > 0:
                            print(">>> SWIPE RIGHT TRIGGERED <<<")
                            gesture_text = "SWIPE RIGHT - Next track"
                            pyautogui.press('nexttrack')
                            
                        else:
                            print(">>> SWIPE LEFT TRIGGERED <<<")
                            gesture_text = "SWIPE LEFT - Previous track"
                            pyautogui.press('prevtrack')

                        last_swipe_time = current_time
                        wrist_x_history.clear()

    else:
        prev_wrist_y = None

    vol_percent = int(volume.GetMasterVolumeLevelScalar() * 100)
    cv2.putText(frame, gesture_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 255, 0), 2)
    cv2.putText(frame, f"Volume: {vol_percent}%", (20, 90), cv2.FONT_HERSHEY_SIMPLEX,
                1, (255, 255, 0), 2)
    cv2.putText(frame, "Fist: Play/Pause | Palm Up/Down: Volume | Swipe: Next/Prev",
                (20, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (255, 255, 255), 1)


    cv2.imshow("Gesture Media Controller", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()