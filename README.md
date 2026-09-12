# Gesture Media Controller

Control media playback and system volume using hand gestures, detected live through your webcam.

## How It Works

MediaPipe tracks your hand and gives back 21 landmark points every frame (fingertips, knuckles, wrist). Simple checks on these points — like whether a fingertip is above or below its knuckle, or how far the wrist moved — decide which gesture you're making. That gesture then triggers a real system action through pycaw (volume) or pyautogui (media keys).

## Tech Stack

| Library   | Purpose                                              |
| --------- | ---------------------------------------------------- |
| OpenCV    | Webcam capture, frame processing, on-screen overlays |
| MediaPipe | Real-time hand landmark detection (pretrained model) |
| pycaw     | Direct system volume control on Windows              |
| pyautogui | Simulates OS-level media key presses                 |

## Gestures

| Gesture             | Action         | How it's Detected                                                           |
| ------------------- | -------------- | --------------------------------------------------------------------------- |
| ✊ Fist             | Play / Pause   | All four fingertips detected below their respective knuckle joints          |
| ✋ Palm moving up   | Volume Up      | Wrist y-coordinate decreasing across frames                                 |
| ✋ Palm moving down | Volume Down    | Wrist y-coordinate increasing across frames                                 |
| 👉 Swipe right      | Next Track     | Wrist x-coordinate shifts right beyond threshold within a short time window |
| 👈 Swipe left       | Previous Track | Wrist x-coordinate shifts left beyond threshold within a short time window  |

## Setup

Requires Python 3.11.

```powershell
py -3.11 -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```powershell
python main.py
```

Press `q` to quit.

## Where to Test It

Works with Spotify, YouTube playlists, or VLC