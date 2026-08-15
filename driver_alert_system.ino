const int BUZZER = 8;
const int RED_LED = 7;
const int GREEN_LED = 6;

void setup() {
  pinMode(BUZZER, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);

  digitalWrite(RED_LED, LOW);
  digitalWrite(GREEN_LED, LOW);
  noTone(BUZZER);

  Serial.begin(9600);
}

void loop() {

  if (Serial.available() > 0) {

    String command = Serial.readStringUntil('\n');
    command.trim();

    // SAFE
    if (command == "SAFE") {

      digitalWrite(GREEN_LED, HIGH);
      digitalWrite(RED_LED, LOW);
      noTone(BUZZER);
    }

    // NORMAL DROWSINESS
    else if (command == "DROWSY") {

      digitalWrite(GREEN_LED, LOW);

      digitalWrite(RED_LED, HIGH);
      tone(BUZZER, 1800);

      delay(500);

      digitalWrite(RED_LED, LOW);
      noTone(BUZZER);
    }

    // CRITICAL DROWSINESS
    else if (command == "CRITICAL_DROWSY") {

      digitalWrite(GREEN_LED, LOW);
      digitalWrite(RED_LED, HIGH);

      // Strong continuous buzzer
      tone(BUZZER, 2500);
    }

    // HEAD DISTRACTION
    else if (command == "DISTRACTION") {

      digitalWrite(GREEN_LED, LOW);
      digitalWrite(RED_LED, HIGH);

      tone(BUZZER, 1200);

      delay(400);

      noTone(BUZZER);
    }

    // STOP ALL
    else if (command == "STOP") {

      digitalWrite(GREEN_LED, LOW);
      digitalWrite(RED_LED, LOW);

      noTone(BUZZER);
    }
  }
}