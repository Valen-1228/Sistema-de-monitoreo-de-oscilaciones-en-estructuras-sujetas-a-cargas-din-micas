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
int pulse = 11;       //Pin del puslo

int long contador = 0;

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
  secondSerial.begin(9600);  // Para el enviar al dispositivo
  Serial.println("inicio");
  digitalWrite(pulse, LOW);
}

void loop() {
  // Almacenamiento de datos cada intervalo de tiempo
  int accX = (int)JY901.stcAcc.a[0];
  readings[readIndex] = accX;
  //secondSerial.print(accX);
  //Serial.print(".");
  readIndex++;
  //Serial.print(".");

  if (readIndex >= numReadings) {
    readIndex = 0;

    //Toma de caractersticas
    detectarpicos();
    calcularSumaLecturas();
    detectarTiempoActividad();
    calcularDerivada();
    calcularIntegral();
    calcularRMS();

    Serial.println("__________________________");
    digitalWrite(pulse, HIGH);
    delay(10);
    digitalWrite(pulse, LOW);
    contador++;
  }

  if (secondSerial.available() > 0) {         // Verifica si hay datos disponibles en Serial2
    char receivedData = secondSerial.read();  // Lee el dato
    Serial.print(receivedData);
    switch (receivedData) {
      case '1':
        Serial.print("contador: ");
        Serial.println(contador);
        secondSerial.print(contador);
        break;
      case '2':
        Serial.print("numero de picos: ");
        Serial.println(numpiks);
        secondSerial.print(numpiks);
        break;
      case '3':
        Serial.print("pico maximo: ");
        Serial.println(maxpik);
        secondSerial.print(maxpik);
        break;
      case '4':
        Serial.print("suma de datos: ");
        Serial.println(sumpik);
        secondSerial.print(sumpik);
        break;
      case '5':
        Serial.print("Tiempo de actividad: ");
        Serial.println(timact);
        secondSerial.print(timact);
        break;
      case '6':
        Serial.print("Maxima derivada negativa: ");
        Serial.println(maxdervneg);
        secondSerial.print(maxdervneg);
        break;
      case '7':
        Serial.print("Maxima derivada positiva: ");
        Serial.println(maxdervpos);
        secondSerial.print(maxdervpos);
        break;
      case '8':
        Serial.print("Integral acumulada: ");
        Serial.println(acuminteg);
        secondSerial.print(acuminteg);
        break;
      case '9':
        Serial.print("RMS: ");
        Serial.println(RMS);
        secondSerial.print(RMS);
        break;
      default:
        Serial.println("Dato no reconocido");
        break;
    }
  }
  

  // Esperar el tiempo de muestreo antes de enviar el siguiente conjunto de datos
  delay(sampleTime);
}


void detectarpicos() {
  float peaks[numReadings];
  int peakIndex = 0;
  int minDiff = 10;           // Diferencia mínima entre picos consecutivos
  bool buscandoPico = true;  // Flag para controlar la detección de picos

  for (int i = 1; i < numReadings - 1; i++) {
    if (readings[i] > readings[i - 1] && readings[i] > readings[i + 1] && readings[i] > humbral && readings[i] > readings[i + 3] && readings[i] > readings[i - 3]) {
      if (buscandoPico || (readings[i] - peaks[peakIndex - 1]) > minDiff) {
        // Detectar el pico si estamos en modo de búsqueda o si el nuevo pico es significativamente diferente del anterior
        peaks[peakIndex] = readings[i];
        peakIndex++;
        buscandoPico = false;  // Desactivar la búsqueda temporalmente hasta que se detecte una caída en la señal
      }
    } else if (readings[i] < humbral) {
      // Si la señal cae por debajo del umbral, reinicia la búsqueda de un nuevo pico
      buscandoPico = true;
    }
  }

  // Número de picos encontrados
  numpiks = peakIndex;

  // Encuentra y envía el valor más alto registrado en la ventana
  int maxValor = readings[0];  // Inicia con el primer valor del array

  for (int i = 1; i < numReadings; i++) {
    if (readings[i] > maxValor) {
      maxValor = readings[i];
    }
  }

  maxpik = maxValor;  // Almacena el valor máximo encontrado
}


void calcularSumaLecturas() {
  long suma = 0;
  for (int i = 0; i < numReadings; i++) {
    suma += readings[i];
  }
  //Serial.print("Suma de lecturas: ");
  //Serial.println(suma);
  sumpik = suma;
}

void detectarTiempoActividad() {
  unsigned long tiempoActividad = 0;
  bool enActividad = false;
  int numeroActividades = 0;

  for (int i = 0; i < numReadings; i++) {
    if (readings[i] > humbral) {
      tiempoActividad += sampleTime;
      if (!enActividad) {
        enActividad = true;
        numeroActividades++;
      }
    } else {
      enActividad = false;
    }
  }

  //Serial.print("Tiempo de actividad (ms): ");
  //Serial.println(tiempoActividad);
  timact = tiempoActividad;
  //Serial.print("Número de actividades: ");
  //Serial.println(numeroActividades);
}

void calcularDerivada() {
  float derivada[numReadings - 1];
  float sumaDerivadas = 0;
  float maxDerivadaPositiva = -INFINITY;  // Para la máxima derivada positiva
  float maxDerivadaNegativa = INFINITY;   // Para la máxima derivada negativa
  float maxDerivadaAbsoluta = 0;          // Para la derivada de mayor magnitud (absoluta)

  for (int i = 1; i < numReadings; i++) {
    derivada[i - 1] = (readings[i] - readings[i - 1]) / (sampleTime / 1000.0);

    // Imprimir las derivadas calculadas
    /*
  Serial.println("Derivadas:");
  for (int i = 0; i < numReadings - 1; i++) {
    Serial.println(derivada[i]);
  }*/
    sumaDerivadas += derivada[i - 1];

    // Comparar la derivada actual para encontrar la máxima positiva y negativa
    if (derivada[i - 1] > maxDerivadaPositiva) {
      maxDerivadaPositiva = derivada[i - 1];
    }
    if (derivada[i - 1] < maxDerivadaNegativa) {
      maxDerivadaNegativa = derivada[i - 1];
    }

    // Comparar la magnitud de la derivada actual para encontrar la mayor en valor absoluto
    if (abs(derivada[i - 1]) > maxDerivadaAbsoluta) {
      maxDerivadaAbsoluta = abs(derivada[i - 1]);
    }
  }

  // Imprimir la suma de las derivadas
  //Serial.print("Suma de derivadas: ");
  //Serial.println(sumaDerivadas);

  // Imprimir la derivada máxima positiva
  //Serial.print("Máxima derivada positiva: ");
  //Serial.println(maxDerivadaPositiva);
  maxdervpos = maxDerivadaPositiva;

  // Imprimir la derivada máxima negativa
  //Serial.print("Máxima derivada negativa: ");
  //Serial.println(maxDerivadaNegativa);
  maxdervneg = maxDerivadaNegativa;

  // Imprimir la derivada de mayor magnitud (absoluta)
  //Serial.print("Máxima derivada en magnitud (absoluta): ");
  //Serial.println(maxDerivadaAbsoluta);
}

void calcularIntegral() {
  float integral = 0;

  for (int i = 0; i < numReadings; i++) {
    integral += readings[i] * (sampleTime / 1000.0);
  }

  // Imprimir el valor de la integral acumulada
  //Serial.print("Integral acumulada: ");
  //Serial.println(integral);
  acuminteg = integral;
}

void calcularRMS() {
  long sumrms = 0;
  for (int i = 0; i < numReadings; i++) {
    sumrms += (long)readings[i] * readings[i];
  }
  float rms = sqrt(sumrms / numReadings);
  //Serial.print("RMS: ");
  //Serial.println(rms);
  RMS = rms;
}

void serialEvent() {
  while (Serial.available()) {
    JY901.CopeSerialData(Serial.read());  // Call JY901 data cope function
  }
}