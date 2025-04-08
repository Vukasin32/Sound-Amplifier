from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

devices = AudioUtilities.GetSpeakers()

interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)

volume = interface.QueryInterface(IAudioEndpointVolume)  # Object that can adjust speakers volume

import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands  # This object is used to detect hands
mp_drawing = mp.solutions.drawing_utils  # This object is used to draw landmarks on image
mp_drawing_styles = mp.solutions.drawing_styles  # This object is used to set style of landmarks

hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    h, w, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    data = []  # List for keeping both landmarks (x,y) of current prediction
    x_ = []  # List of landmarks x coord. of current prediction
    y_ = []  # List of landmarks y coord. of current prediction

    result = hands.process(frame_rgb)  # Result of detection
    if result.multi_hand_landmarks and len(result.multi_hand_landmarks) == 1:  # First condition makes sure to go inside loop if hand is detected, second condition makes sure to go inside loop if one and only one hand is detected
        hand_landmarks = result.multi_hand_landmarks[0]
        mp_drawing.draw_landmarks(
            frame,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.DrawingSpec(color=(255, 0, 255), thickness=3, circle_radius=3),
            mp_drawing_styles.DrawingSpec(color=(0, 0, 0), thickness=1)
        )

        for i in range(len(hand_landmarks.landmark)):
            x = hand_landmarks.landmark[i].x
            y = hand_landmarks.landmark[i].y

            data.append(x)
            data.append(y)
            x_.append(x)
            y_.append(y)

        if len(data) == 42:  # Controller can be used only if all landmarks can be registered in image
            x1 = int(min(x_) * w) - 10
            x2 = int(max(x_) * w) + 10
            y1 = int(min(y_) * h) - 10
            y2 = int(max(y_) * h) + 10

            rec_width = (x2 - x1) ** 2  # Squared width of rectangle in which hand is detected
            print(f'Area: {rec_width}')
            x_thumb = int(x_[4] * w)  # Landmark with index 4 of array x_ belongs to thumb
            x_index = int(x_[8] * w)  # Landmark with index 8 of array x_ belongs to index
            y_thumb = int(y_[4] * h)
            y_index = int(y_[8] * h)

            dist = (x_thumb - x_index) ** 2 + (y_thumb - y_index) ** 2  # Squared Euclidean distance between thumb and index

            # Key part of having robust controller is finding relative measure of distance
            # between thumb and index
            quotient = rec_width / dist  # Role of Variable quotient is relative

            # Empirically, it is shown that piece by piece linear function, which is described by
            # points (1, 100), (15, 12.5), (50, 0), is a good choice.
            # First coord. represents value of quotient while second coord. represents
            # desired volume of speaker which is represented bu variable speaker_volume

            if 15 <= quotient < 50:
                speaker_volume = -0.357 * quotient + 17.857
            elif 1 <= quotient < 15:
                speaker_volume = -6.25 * quotient + 106.25
            elif quotient < 1:
                speaker_volume = 100
            else:
                speaker_volume = 0

            # Previous equations were simply derived by conditions about 3 points
            # which piece by piece linear function should go through

            print(f'Dist: {dist}')
            print(f'Quotient: {quotient}')

            cv2.circle(frame, (x_thumb, y_thumb), 8, (255, 0, 0), -1)
            cv2.circle(frame, (x_index, y_index), 8, (255, 0, 0), -1)

            cv2.line(frame, (x_thumb, y_thumb), (x_index, y_index), (255, 0, 0), 2)

            cv2.putText(frame, f'{speaker_volume:.2f}%', (x1 - 5, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        (255, 255, 0), 3)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 3)

            volume.SetMasterVolumeLevelScalar(speaker_volume / 100, None)  # Object volume sets speakers strength to value of speaker_volume

    cv2.imshow('APP WINDOW', frame)
    if cv2.waitKey(5) & 0xFF == ord('q'):  # Pressing q on keyboard breaks out from process
        break

cap.release()
cv2.destroyAllWindows()

