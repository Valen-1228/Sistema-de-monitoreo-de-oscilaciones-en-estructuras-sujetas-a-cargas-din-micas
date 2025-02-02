#include <I2Cdev.h>
#include <MPU6050.h>
#include <Wire.h>
#include <JY901.h>
#include <SoftwareSerial.h>

SoftwareSerial secondSerial(2, 3);  // RX, TX

const unsigned long sampleTime = 100;           // Tiempo de muestra en milisegundos
const unsigned long interval = 15000;           // Intervalo de envío en milisegundos (10 segundos)
const int numReadings = interval / sampleTime;  // Número de lecturas en el intervalo
int readings[numReadings];                      // Array para almacenar las lecturas
unsigned long lastTime = 0;
int readIndex = 0;
float humbral = 914;  // Ajusta este valor según sea necesario
int pulse = 11;       // Pin del pulso

// Variables para almacenar datos simulados
int numpiks = 0;      // Número de picos simulados
int maxpik = 0;       // Pico máximo simulado
long sumpik = 0;      // Suma de picos simulada
int timact = 0;       // Tiempo de actividad simulado
int maxdervneg = 0;   // Máxima derivada negativa simulada
int maxdervpos = 0;   // Máxima derivada positiva simulada
float acuminteg = 0;  // Integral acumulada simulada
float RMS = 0;        // Valor RMS simulado

void setup() {
  Serial.begin(9600);
  secondSerial.begin(9600);  // Para el envío al dispositivo
  Wire.begin();
  Serial.println("Inicio del sistema");
  digitalWrite(pulse, LOW);
  Serial.println("AccX");
}

void loop() {
  // Leer datos crudos del sensor
  int accX = (int)JY901.stcAcc.a[0];

  // Enviar datos crudos por Serial

  Serial.print(accX);
  Serial.print(" ");

  // Guardar datos crudos en el arreglo de lecturas
  readings[readIndex] = accX;
  readIndex++;

  if (readIndex >= numReadings) {
    readIndex = 0;

    // Procesar y caracterizar los datos
    detectarpicos();
    calcularSumaLecturas();
    detectarTiempoActividad();
    calcularDerivada();
    calcularIntegral();
    calcularRMS();

    Serial.println(" ");
    Serial.println("AccX");

    // Enviar datos caracterizados por secondSerial
    secondSerial.println("__________________________________________");
    secondSerial.print("NumPiks: ");
    secondSerial.println(numpiks);
    secondSerial.print("MaxPik: ");
    secondSerial.println(maxpik);
    secondSerial.print("SumaDatos: ");
    secondSerial.println(sumpik);
    secondSerial.print("TimAct: ");
    secondSerial.println(timact);
    secondSerial.print("MaxDerNeg: ");
    secondSerial.println(maxdervneg);
    secondSerial.print("MaxDerPos: ");
    secondSerial.println(maxdervpos);
    secondSerial.print("AcumInteg: ");
    secondSerial.println(acuminteg);
    secondSerial.print("RMS: ");
    secondSerial.println(RMS);
  }

  delay(sampleTime);
}

void detectarpicos() {
  int peakIndex = 0;
  maxpik = 0; 
  for (int i = 1; i < numReadings - 1; i++) {
    if (readings[i] > readings[i - 1] && readings[i] > readings[i + 1] && readings[i] > humbral) {
      peakIndex++;
      if (readings[i] > maxpik) {
        maxpik = readings[i];
      }
    }
  }
  numpiks = peakIndex;
}

void calcularSumaLecturas() {
  long suma = 0;
  for (int i = 0; i < numReadings; i++) {
    suma += readings[i];
  }
  sumpik = suma;
}

void detectarTiempoActividad() {
  unsigned long tiempoActividad = 0;
  for (int i = 0; i < numReadings; i++) {
    if (readings[i] > humbral) {
      tiempoActividad += sampleTime;
    }
  }
  timact = tiempoActividad;
}

void calcularDerivada() {
  maxdervneg = 0;
  maxdervpos = 0;
  for (int i = 1; i < numReadings; i++) {
    int derivada = readings[i] - readings[i - 1];
    if (derivada > maxdervpos) {
      maxdervpos = derivada;
    }
    if (derivada < maxdervneg) {
      maxdervneg = derivada;
    }
  }
}

void calcularIntegral() {
  float integral = 0;
  for (int i = 0; i < numReadings; i++) {
    integral += readings[i] * (sampleTime / 1000.0);
  }
  acuminteg = integral;
}

void calcularRMS() {
  long sumrms = 0;

  for (int i = 0; i < numReadings; i++) {
    sumrms += (long)readings[i] * readings[i];  // Asegurar precisión
  }

  // Evitar la división por cero
  if (numReadings > 0) {
    RMS = sqrt((double)sumrms / numReadings);
  } else {
    RMS = 0;
  }
}


void serialEvent() {
  while (Serial.available()) {
    JY901.CopeSerialData(Serial.read());
  }
}
