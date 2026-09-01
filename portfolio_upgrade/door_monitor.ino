/*
 * DoorSense portfolio firmware
 * Hardware: Arduino Uno/Nano, HC-SR04, LED, buzzer
 * Serial output: one JSON reading every 500 ms.
 */

const uint8_t TRIG_PIN = 9;
const uint8_t ECHO_PIN = 10;
const uint8_t LED_PIN = 6;
const uint8_t BUZZER_PIN = 5;
const float OPEN_THRESHOLD_CM = 22.0;
const float HYSTERESIS_CM = 2.0;

bool doorOpen = false;
unsigned long lastSampleAt = 0;

float readDistanceCm() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  unsigned long duration = pulseIn(ECHO_PIN, HIGH, 30000UL);
  if (duration == 0) return -1.0;
  return duration * 0.0343 / 2.0;
}

void updateState(float distanceCm) {
  if (!doorOpen && distanceCm >= OPEN_THRESHOLD_CM + HYSTERESIS_CM) {
    doorOpen = true;
    tone(BUZZER_PIN, 1800, 160);
  } else if (doorOpen && distanceCm <= OPEN_THRESHOLD_CM - HYSTERESIS_CM) {
    doorOpen = false;
    tone(BUZZER_PIN, 900, 100);
  }
  digitalWrite(LED_PIN, doorOpen ? HIGH : LOW);
}

void publishReading(float distanceCm) {
  Serial.print("{\"distance_cm\":");
  Serial.print(distanceCm, 2);
  Serial.print(",\"state\":\"");
  Serial.print(doorOpen ? "open" : "closed");
  Serial.println("\"}");
}

void setup() {
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  Serial.begin(115200);
}

void loop() {
  if (millis() - lastSampleAt < 500) return;
  lastSampleAt = millis();
  float distanceCm = readDistanceCm();
  if (distanceCm < 0 || distanceCm > 500) return;
  updateState(distanceCm);
  publishReading(distanceCm);
}
