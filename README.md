# AI Driver Drowsiness & Distraction Detection System

## 1. Project Overview

The AI Driver Drowsiness & Distraction Detection System is a real-time driver safety prototype designed to identify signs of driver fatigue, yawning, prolonged eye closure, head distraction, and face absence.

The system uses a laptop webcam for real-time monitoring. Computer vision and facial landmark analysis are performed using Python, OpenCV, and MediaPipe. An Arduino UNO is connected through USB to control physical warning devices such as LEDs and a buzzer.

The system provides both software-based voice alerts and hardware-based visual/audio alerts.

---

## 2. Problem Statement

Driver drowsiness and distraction are major causes of road accidents.

A driver may become sleepy, close their eyes for a prolonged period, yawn repeatedly, or look away from the road. If these conditions are detected early, an alert can help the driver regain attention.

Our prototype continuously monitors the driver's face and provides alerts when unsafe conditions are detected.

---

## 3. Proposed Solution

The system uses a webcam to monitor the driver in real time.

The captured video is processed using OpenCV and MediaPipe Face Mesh. Facial landmarks are analyzed to determine:

- Eye closure
- Drowsiness
- Critical drowsiness
- Yawning
- Head direction/distraction
- Face absence

When an unsafe condition is detected, the system generates an appropriate voice alert and communicates with the Arduino UNO through USB serial communication.

The Arduino controls the red LED, green LED, and buzzer according to the received command.

---

## 4. Key Features

### Eye-Based Drowsiness Detection

The system calculates the Eye Aspect Ratio (EAR) using eye landmarks.

If the driver's eyes remain closed for a predefined period, drowsiness is detected.

### Critical Drowsiness Detection

If the driver's eyes remain closed for a longer critical duration, the system generates a stronger alert.

### Yawning Detection

The system analyzes mouth landmarks to identify prolonged mouth opening.

Each detected yawn increases the yawning counter.

### Distraction Detection

The system monitors the driver's head direction.

If the driver continuously turns their head away from the center for the defined duration, a distraction warning is generated.

### Face Not Detected

If the driver's face is not visible to the camera, the system generates a voice alert indicating that the face is not detected.

### Voice Alerts

The system uses Windows built-in speech synthesis to provide audible warnings to the driver.

### Hardware Alert System

Arduino UNO controls:

- Green LED for safe/awake state
- Red LED for warning conditions
- Buzzer for drowsiness/critical alerts

### Real-Time Status Display

The camera window displays:

- Current status
- EAR value
- Yawning count
- Drowsiness count
- Critical drowsiness count
- Distraction count
- Head direction
- System status

---

## 5. Technologies Used

### Software

- Python
- OpenCV
- MediaPipe
- PySerial
- Visual Studio Code
- Arduino IDE

### Hardware

- Arduino UNO
- Laptop/USB webcam
- Red LED
- Green LED
- Buzzer
- Resistors
- Jumper wires
- USB cable

---

## 6. Python Libraries

The project uses the following Python packages:

- OpenCV
- MediaPipe 0.10.14
- PySerial

The required packages are listed in `requirements.txt`.

---

## 7. System Architecture

```text
              DRIVER
                |
                v
          Laptop Webcam
                |
                v
             OpenCV
                |
                v
        MediaPipe Face Mesh
                |
                v
       Facial Landmark Analysis
                |
       +--------+--------+
       |        |        |
       v        v        v
     Eyes     Mouth     Face
       |        |        |
       v        v        v
  Drowsiness  Yawning  Distraction
       |        |        |
       +--------+--------+
                |
                v
        Python Decision Logic
                |
        +-------+-------+
        |               |
        v               v
   Voice Alert       PySerial
                        |
                        v
                   Arduino UNO
                        |
              +---------+---------+
              |         |         |
              v         v         v
          Green LED   Red LED   Buzzer
          ## 8. Hardware Connections

The prototype uses an Arduino UNO to control the visual and audio alert components.

### Component Connections

| Component | Arduino UNO Pin | Connection |
|---|---|---|
| Green LED | D6 | LED positive/anode through resistor |
| Red LED | D7 | LED positive/anode through resistor |
| Buzzer | D8 | Positive pin |
| Green LED | GND | LED cathode |
| Red LED | GND | LED cathode |
| Buzzer | GND | Negative pin |
| Arduino UNO | USB | Connected to laptop |
| Laptop Webcam | USB/Integrated | Used for driver monitoring |

### Green LED

- Green LED positive (longer leg/anode) → resistor → Arduino D6
- Green LED negative (shorter leg/cathode) → GND

### Red LED

- Red LED positive (longer leg/anode) → resistor → Arduino D7
- Red LED negative (shorter leg/cathode) → GND

### Buzzer

- Buzzer positive (+) → Arduino D8
- Buzzer negative (-) → Arduino GND

### USB Communication

The Arduino UNO is connected to the laptop using a USB cable.

The USB connection provides:

- Power to the Arduino
- Serial communication between Python and Arduino
- Transfer of safety commands from Python to Arduino

The Python program communicates with the Arduino through the configured serial port, such as `COM3`, at `9600` baud rate.

### Hardware Working

```text
                 LAPTOP
              +-----------+
              |  Webcam   |
              +-----+-----+
                    |
                    v
              Python Program
                    |
             USB Serial / COM3
                    |
                    v
              +-----------+
              | Arduino   |
              |    UNO    |
              +-----------+
                |    |    |
               D6   D7   D8
                |    |    |
                v    v    v
             Green  Red  Buzzer
              LED   LED
              ## 9. Arduino-Python Communication

The Python application communicates with the Arduino UNO through USB serial communication.

The configured communication settings are:

- Serial Port: COM3
- Baud Rate: 9600
- Communication Type: USB Serial

Python sends commands to the Arduino according to the driver's condition.

Commands used:

- `SAFE` – Driver is awake and safe
- `DROWSY` – Drowsiness detected
- `CRITICAL_DROWSY` – Critical drowsiness detected
- `STOP` – Stop all hardware alerts

The Arduino receives these commands and controls the LEDs and buzzer.
## 10. Software Workflow

1. The webcam captures the driver's face.
2. OpenCV processes the camera frames.
3. MediaPipe Face Mesh detects facial landmarks.
4. Eye landmarks are analyzed using Eye Aspect Ratio (EAR).
5. Mouth landmarks are analyzed for yawning.
6. Facial position is analyzed for head distraction.
7. The system checks whether the face is visible.
8. Python determines the driver's current safety condition.
9. A voice alert is generated when required.
10. Python sends the corresponding command to Arduino.
11. Arduino controls the green LED, red LED, and buzzer.
12. The live camera screen displays the current status and detection counts.
## 11. Detection Conditions

### Safe State

When the driver's eyes are open and the face is detected normally, the system displays:

`SAFE - DRIVER AWAKE`

The green LED is activated and the buzzer remains off.

### Drowsiness State

If the driver's eyes remain closed for the configured drowsiness duration, the system detects drowsiness.

A voice warning is generated and the Arduino activates the warning output.

### Critical Drowsiness State

If the driver's eyes remain closed for the critical duration, the system generates a stronger warning.

### Yawning State

When prolonged mouth opening is detected, the yawning counter increases and an audible yawning warning is generated.

### Distraction State

If the driver's head remains turned away from the center for the configured duration, the system generates:

`Keep your eyes on the road.`

### Face Not Detected State

If the driver's face is not visible to the camera, the system generates:

`Where are you?`
## 12. Testing

The prototype was tested using a laptop webcam and Arduino UNO.

The following conditions were tested:

- Normal eye-open condition
- Prolonged eye closure
- Critical eye closure
- Yawning
- Head turning/distraction
- Face not detected
- Driver returning to normal position
- Arduino LED operation
- Arduino buzzer operation
- Python-Arduino serial communication
- Voice alert generation
## 13. Project Advantages

- Real-time driver monitoring
- Non-contact detection
- Uses a standard webcam
- Low-cost hardware prototype
- AI/computer-vision based detection
- Audible and physical alerts
- Real-time detection counters
- Simple Arduino integration
- Can be extended for real-world applications
## 14. Future Scope

The prototype can be further enhanced with:

- Mobile notifications
- Emergency contact alerts
- GPS location tracking
- WhatsApp/SMS alerts
- Cloud-based monitoring
- Vehicle integration
- Advanced head-pose estimation
- Improved machine-learning models
- Driver identification
- Data logging and analytics
- Dedicated automotive camera
## 15. Safety Note

This project is a prototype developed for educational, research, and demonstration purposes.

It is not a certified automotive safety system and should not be considered a replacement for professional driver-assistance or vehicle safety systems.
## 16. Conclusion

The AI Driver Drowsiness & Distraction Detection System combines computer vision, facial landmark analysis, voice alerts, and Arduino-based hardware alerts to monitor driver behavior in real time.

The prototype demonstrates the feasibility of detecting drowsiness, yawning, distraction, and face absence using a low-cost setup.

The combination of software and hardware alerts provides a practical foundation for developing more advanced intelligent driver-monitoring systems in the future.
## 📸 Project Demonstration

### 1. Hardware Setup
Shows the complete hardware setup used for the AI Driver Drowsiness Detection System.

![Hardware Setup](images/image1.jpeg)

### 2. Normal Driver Condition
Shows the system monitoring the driver in a normal, awake condition.

![Normal Condition](images/image2.jpeg)

### 3. Driver Monitoring
Shows the real-time face and eye monitoring using the webcam and MediaPipe.

![Driver Monitoring](images/image3.jpeg)

### 4. Drowsiness Detection
Shows the system detecting drowsiness and displaying the alert status.

![Drowsiness Detection](images/image4.png)

### 5. Real-Time System Output
Shows the final real-time output with detection status and system information.

![System Output](images/image5.png)