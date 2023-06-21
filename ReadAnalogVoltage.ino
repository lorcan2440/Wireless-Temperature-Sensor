void setup() {
  // initialize serial communication at 115200 bits per second:
  pinMode(NINA_RESETN, OUTPUT);
  digitalWrite(NINA_RESETN, LOW);
  Serial.begin(115200);
  SerialNina.begin(115200);
}

void loop() {
  static int i = 0;  // Static variable to retain the value of 'i' between function calls

  int sensorValue = analogRead(A0);
  byte packet[2 * sizeof(int)];
  memcpy(packet, &sensorValue, sizeof(int));
  memcpy(packet + sizeof(int), &i, sizeof(int));

  SerialNina.write(packet, sizeof(packet));

  i += 1;
  delay(1000);
}
