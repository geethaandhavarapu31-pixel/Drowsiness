import cv2
import mediapipe as mp
import math
import time
import serial
import threading
import subprocess

ARDUINO_PORT = "COM3"
BAUD_RATE = 9600

DROWSINESS_TIME = 5.0
CRITICAL_TIME = 10.0

EYE_CLOSED_THRESHOLD = 0.23

YAWN_THRESHOLD = 0.085
YAWN_TIME = 5.0

HEAD_TURN_TIME = 5.0

voice_lock = threading.Lock()


def speak(message):

    def voice_task():

        with voice_lock:

            try:

                safe_text = message.replace(
                    "'",
                    "''"
                )

                powershell_command = (
                    "Add-Type -AssemblyName System.Speech; "
                    "$speaker = New-Object "
                    "System.Speech.Synthesis.SpeechSynthesizer; "
                    "$speaker.Volume = 100; "
                    "$speaker.Rate = 0; "
                    f"$speaker.Speak('{safe_text}'); "
                    "$speaker.Dispose();"
                )

                subprocess.run(
                    [
                        "powershell",
                        "-NoProfile",
                        "-Command",
                        powershell_command
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

            except Exception as error:

                print(
                    "VOICE ERROR:",
                    error
                )

    threading.Thread(
        target=voice_task,
        daemon=True
    ).start()


try:

    arduino = serial.Serial(
        ARDUINO_PORT,
        BAUD_RATE,
        timeout=1
    )

    time.sleep(2)

    print("Arduino connected successfully.")

except Exception as error:

    print("Arduino connection failed.")
    print("Check COM3.")
    print(error)

    exit()


def send_command(command):

    try:

        arduino.write(
            (command + "\n").encode()
        )

    except Exception as error:

        print(
            "Arduino error:",
            error
        )


mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

LEFT_EYE = [
    33,
    160,
    158,
    133,
    153,
    144
]

RIGHT_EYE = [
    362,
    385,
    387,
    263,
    373,
    380
]

MOUTH_TOP = 13
MOUTH_BOTTOM = 14
MOUTH_LEFT = 78
MOUTH_RIGHT = 308


def calculate_ear(
    landmarks,
    eye_points,
    width,
    height
):

    points = []

    for index in eye_points:

        x = int(
            landmarks[index].x * width
        )

        y = int(
            landmarks[index].y * height
        )

        points.append(
            (x, y)
        )

    vertical_1 = math.dist(
        points[1],
        points[5]
    )

    vertical_2 = math.dist(
        points[2],
        points[4]
    )

    horizontal = math.dist(
        points[0],
        points[3]
    )

    if horizontal == 0:

        return 0.0

    return (
        vertical_1 +
        vertical_2
    ) / (
        2.0 * horizontal
    )


def calculate_mouth_ratio(
    landmarks,
    width,
    height
):

    top = landmarks[MOUTH_TOP]
    bottom = landmarks[MOUTH_BOTTOM]

    left = landmarks[MOUTH_LEFT]
    right = landmarks[MOUTH_RIGHT]

    top_point = (
        int(top.x * width),
        int(top.y * height)
    )

    bottom_point = (
        int(bottom.x * width),
        int(bottom.y * height)
    )

    left_point = (
        int(left.x * width),
        int(left.y * height)
    )

    right_point = (
        int(right.x * width),
        int(right.y * height)
    )

    vertical = math.dist(
        top_point,
        bottom_point
    )

    horizontal = math.dist(
        left_point,
        right_point
    )

    if horizontal == 0:

        return 0.0

    return vertical / horizontal


def get_head_direction(landmarks):

    nose_x = landmarks[1].x

    left_x = landmarks[234].x
    right_x = landmarks[454].x

    face_width = right_x - left_x

    if face_width <= 0:

        return "CENTER"

    position = (
        nose_x - left_x
    ) / face_width

    if position < 0.38:

        return "LEFT"

    elif position > 0.62:

        return "RIGHT"

    return "CENTER"


cap = cv2.VideoCapture(0)

if not cap.isOpened():

    print(
        "Webcam could not be opened."
    )

    arduino.close()

    exit()


eyes_closed_start = None
head_turn_start = None
yawn_start = None

yawn_count = 0
drowsiness_count = 0
critical_count = 0
distraction_count = 0

drowsiness_alerted = False
critical_alerted = False

yawn_alerted = False

distraction_alerted = False

face_missing = False


with mp_face_mesh.FaceMesh(

    max_num_faces=1,

    refine_landmarks=True,

    min_detection_confidence=0.5,

    min_tracking_confidence=0.5

) as face_mesh:

    while True:

        success, frame = cap.read()

        if not success:

            print(
                "Camera frame error."
            )

            break

        frame = cv2.flip(
            frame,
            1
        )

        height, width, _ = frame.shape

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        results = face_mesh.process(
            rgb
        )

        status = "FACE NOT DETECTED"

        status_color = (
            0,
            0,
            255
        )

        ear = 0.0
        mouth_ratio = 0.0
        head_direction = "UNKNOWN"

        if results.multi_face_landmarks:

            face = (
                results.multi_face_landmarks[0]
            )

            landmarks = face.landmark

            if face_missing:

                face_missing = False

            left_ear = calculate_ear(
                landmarks,
                LEFT_EYE,
                width,
                height
            )

            right_ear = calculate_ear(
                landmarks,
                RIGHT_EYE,
                width,
                height
            )

            ear = (
                left_ear +
                right_ear
            ) / 2.0

            mouth_ratio = calculate_mouth_ratio(
                landmarks,
                width,
                height
            )

            head_direction = get_head_direction(
                landmarks
            )

            if mouth_ratio > YAWN_THRESHOLD:

                if yawn_start is None:

                    yawn_start = time.time()

                mouth_time = (
                    time.time()
                    -
                    yawn_start
                )

                if mouth_time >= YAWN_TIME:

                    if not yawn_alerted:

                        yawn_alerted = True

                        yawn_count += 1

                        print(
                            f"YAWN DETECTED: "
                            f"{yawn_count}"
                        )

                        speak(
                            "Yawning detected."
                        )

            else:

                yawn_start = None

                yawn_alerted = False

            if ear < EYE_CLOSED_THRESHOLD:

                if eyes_closed_start is None:

                    eyes_closed_start = time.time()

                    drowsiness_alerted = False
                    critical_alerted = False

                closed_time = (
                    time.time()
                    -
                    eyes_closed_start
                )

                if closed_time >= CRITICAL_TIME:

                    status = (
                        "CRITICAL DROWSINESS"
                    )

                    status_color = (
                        0,
                        0,
                        255
                    )

                    if not critical_alerted:

                        critical_alerted = True

                        critical_count += 1

                        send_command(
                            "CRITICAL_DROWSY"
                        )

                        speak(
                            "Critical drowsiness detected. "
                            "Wake up immediately."
                        )

                elif closed_time >= DROWSINESS_TIME:

                    status = (
                        "DROWSINESS DETECTED"
                    )

                    status_color = (
                        0,
                        0,
                        255
                    )

                    if not drowsiness_alerted:

                        drowsiness_alerted = True

                        drowsiness_count += 1

                        send_command(
                            "DROWSY"
                        )

                        speak(
                            "Drowsiness detected. "
                            "Please stay awake."
                        )

                else:

                    status = (
                        f"EYES CLOSED "
                        f"{closed_time:.1f}s"
                    )

                    status_color = (
                        0,
                        255,
                        255
                    )

            else:

                if (
                    drowsiness_alerted
                    or
                    critical_alerted
                ):

                    speak(
                        "Now you are awake, good."
                    )

                send_command(
                    "SAFE"
                )

                status = (
                    "SAFE - DRIVER AWAKE"
                )

                status_color = (
                    0,
                    255,
                    0
                )

                eyes_closed_start = None

                drowsiness_alerted = False
                critical_alerted = False

                if head_direction in (
                    "LEFT",
                    "RIGHT"
                ):

                    if head_turn_start is None:

                        head_turn_start = time.time()

                        distraction_alerted = False

                    head_time = (
                        time.time()
                        -
                        head_turn_start
                    )

                    if head_time >= HEAD_TURN_TIME:

                        status = (
                            "DISTRACTION DETECTED"
                        )

                        status_color = (
                            0,
                            165,
                            255
                        )

                        if not distraction_alerted:

                            distraction_alerted = True

                            distraction_count += 1

                            speak(
                                "Keep your eyes on the road."
                            )

                else:

                    head_turn_start = None

                    distraction_alerted = False

            mp_drawing.draw_landmarks(
                frame,
                face,
                mp_face_mesh.FACEMESH_TESSELATION
            )

        else:

            status = (
                "FACE NOT DETECTED"
            )

            status_color = (
                0,
                0,
                255
            )

            send_command(
                "STOP"
            )

            eyes_closed_start = None
            head_turn_start = None
            yawn_start = None

            drowsiness_alerted = False
            critical_alerted = False

            yawn_alerted = False
            distraction_alerted = False

            if not face_missing:

                face_missing = True

                print(
                    "FACE NOT DETECTED"
                )

                speak(
                    "Where are you?"
                )

        cv2.putText(
            frame,
            "AI DRIVER SAFETY SYSTEM",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"STATUS: {status}",
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            status_color,
            2
        )

        cv2.putText(
            frame,
            f"EAR: {ear:.2f}",
            (20, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"YAWN COUNT: {yawn_count}",
            (20, 145),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.60,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"DROWSINESS COUNT: {drowsiness_count}",
            (20, 180),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"CRITICAL COUNT: {critical_count}",
            (20, 215),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"DISTRACTION COUNT: {distraction_count}",
            (20, 250),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"HEAD: {head_direction}",
            (20, 285),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            "SYSTEM: ACTIVE",
            (20, 325),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.60,
            (0, 255, 0),
            2
        )

        cv2.imshow(
            "AI Driver Safety System",
            frame
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):

            break


try:

    send_command(
        "STOP"
    )

    time.sleep(0.3)

    arduino.close()

except Exception:

    pass


cap.release()

cv2.destroyAllWindows()


print()
print("======================================")
print(" AI DRIVER SAFETY SYSTEM STOPPED")
print("======================================")
print(
    "Yawns:",
    yawn_count
)
print(
    "Drowsiness:",
    drowsiness_count
)
print(
    "Critical:",
    critical_count
)
print(
    "Distractions:",
    distraction_count
)
print("======================================")