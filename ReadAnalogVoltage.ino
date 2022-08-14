
void setup() {
  // initialise serial communications:
  pinMode(NINA_RESETN, OUTPUT);         
  digitalWrite(NINA_RESETN, LOW);
  Serial.begin(115200);
  SerialNina.begin(115200);
  
  int i = 0;  // measurement number (index)
  
  while (true) {
    int sensorValue = analogRead(A0);
    float voltage = sensorValue * (5.0 / 1023.0);
    float temperature = (voltage - 1.375) / 0.0225;

    SerialNina.print("Measurement #");
    SerialNina.print(i);
    SerialNina.print(" - Temperature = ");
    SerialNina.println(temperature);
    
    
    if (Serial.available()) {
      SerialNina.write(Serial.read());}
    /*
    if (SerialNina.available()) {
      Serial.write(SerialNina.read());}*/  // for two-way comms - disable for now
      
    i += 1;
    delay(1000);  // time delay between readings = 1000 ms = 1 s
  };
};
