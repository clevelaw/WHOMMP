#include <Wire.h>
#include "MAX30105.h"
#include "heartRate.h"
#include "spo2_algorithm.h"


MAX30105 particleSensor;
#define NUM_ANALOG_PINS 5
const int analogPins[NUM_ANALOG_PINS] = {A0, A1, A2, A3, A9};
int analogValues[NUM_ANALOG_PINS];

void readAnalogSensors() {
  for (int i = 0; i < NUM_ANALOG_PINS; i++) {
    analogValues[i] = analogRead(analogPins[i]);
  }
}

void setup() {
  Serial.begin(9600);

  // initialize and configure MAX30105
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println("MAX30105 was not found. Please check wiring/power.");
    while (1);
  }
  particleSensor.setup();
  particleSensor.setPulseAmplitudeRed(0x0A);
  particleSensor.setPulseAmplitudeGreen(0);
  particleSensor.enableDIETEMPRDY();
}

void loop() {
  // synchronize to 1ms boundaries
  delayMicroseconds(1000 - (micros() % 1000));

  long irValue  = particleSensor.getIR();
  long redValue = particleSensor.getRed();
  readAnalogSensors();
  Serial.print(analogValues[0]);
  Serial.print("/");
  Serial.print(analogValues[1]);
  Serial.print("/");
  Serial.print(analogValues[2]);
  Serial.print("/");
  Serial.print(analogValues[3]);
  Serial.print("/");
  Serial.print(irValue);
  Serial.print("/");
  Serial.print(redValue);
  Serial.print("/");
  Serial.println(analogValues[9]);
}
