import cv2
import math
import pyautogui
import mediapipe as mp
from cv2 import VideoCapture
from cv2 import cvtColor
from cv2 import COLOR_BGR2RGB
from cv2 import flip
from cv2 import imencode
from cv2.typing import MatLike
from typing import Any
from typing import Tuple
from typing import Generator


THUMB_TIP: int = 4
INDEX_FINGER_TIP: int = 8
DISTANCE_THRESHOLD: int = 50
FLIPCODE: int = 1
THICKNESS: int = 3
GREEN: Tuple[int, int, int] = (0, 255, 0)


mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
drawing_utils = mp.solutions.drawing_utils


def adjust_volume(
        image: MatLike,
        landmarks: Any,
        frame_width: int,
        frame_height: int
) -> None:
    """
    Adjust system volume based on the distance between index finger and thumb.
    """
    x1, y1, x2, y2 = [0] * 4
    for idx, lm in enumerate(landmarks.landmark):
        if idx in [THUMB_TIP, INDEX_FINGER_TIP]:
            x, y = int(lm.x * frame_width), int(lm.y * frame_height)
            if idx == THUMB_TIP:
                x1, y1 = x, y
            elif idx == INDEX_FINGER_TIP:
                x2, y2 = x, y

    if x1 and y1 and x2 and y2:
        cv2.line(image, (x1, y1), (x2, y2), GREEN, THICKNESS)
        dist: float = math.dist((x1, y1), (x2, y2))
        if dist > DISTANCE_THRESHOLD:
            pyautogui.press("volumeup")
        else:
            pyautogui.press("volumedown")


def process_frame(image: MatLike) -> MatLike:
    """
    Process the input frame to detect hands and draw landmarks.
    Controls volume based on the distance between index finger and thumb.
    """
    frame_height, frame_width, _ = image.shape
    rgb_image: MatLike = cvtColor(image, COLOR_BGR2RGB)
    results = hands.process(rgb_image)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            drawing_utils.draw_landmarks(
                image,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )
            adjust_volume(image, hand_landmarks, frame_width, frame_height)
    return image


def generate_frames() -> Generator[bytes, None, None]:
    """
    Capture video from the webcam and process each frame.
    """
    webcam: VideoCapture = cv2.VideoCapture(0)
    try:
        while True:
            success, frame = webcam.read()
            if not success:
                break

            frame: MatLike = flip(frame, FLIPCODE)
            processed_frame: MatLike = process_frame(frame)

            _, buffer = imencode('.jpg', processed_frame)
            frame_bytes: bytes = buffer.tobytes()
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        webcam.release()
