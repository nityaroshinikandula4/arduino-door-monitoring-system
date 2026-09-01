// DoorSense HC-SR04 monitoring firmware
// Emits one compact JSON reading every 500 ms over USB serial.

const uint8_t TRIG_PIN = 9;
const uint8_t ECHO_PIN = 10;
const uint8_t BUZZER_PIN = 6;
const float OPEN_THRESHOLD_CM = 35.0;
const float CLOSED_THRESHOLD_CM = 18.0;
const unsigned long SAMPLE_INTERVAL_MS = 500;

unsigned long lastSample = 0;
bool alarmEnabled = true;
String lastState = "unknown";

float readDistanceCm() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  const unsigned long duration = pulseIn(ECHO_PIN, HIGH, 30000UL);
  if (duration == 0) return -1.0;
  return (duration * 0.0343) / 2.0;
}

String classifyDoor(float distanceCm) {
  if (distanceCm < 0) return "unknown";
  if (distanceCm <= CLOSED_THRESHOLD_CM) return "closed";
  if (distanceCm >= OPEN_THRESHOLD_CM) return "open";
  return "ajar";
}

void setup() {
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);
  Serial.begin(115200);
}

void loop() {
  if (millis() - lastSample < SAMPLE_INTERVAL_MS) return;
  lastSample = millis();

  const float distance = readDistanceCm();
  const String state = classifyDoor(distance);
  const bool changed = state != lastState;
  lastState = state;

  const bool alarm = alarmEnabled && state == "open";
  digitalWrite(BUZZER_PIN, alarm ? HIGH : LOW);

  Serial.print("{\"distance_cm\":");
  Serial.print(distance, 2);
  Serial.print(",\"state\":\"");
  Serial.print(state);
  Serial.print("\",\"changed\":");
  Serial.print(changed ? "true" : "false");
  Serial.print(",\"alarm\":");
  Serial.print(alarm ? "true" : "false");
  Serial.println("}");
}
