#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

#define TRIG_PIN 22
#define ECHO_PIN 21
#define PIR_PIN 23
#define BUZZER_PIN 19

// ---- WIFI ----
const char* ssid = "Ooredoo 5G_86561B_5G";
const char* password = "6P2PGS7ZH2";

// ---- API URL ----
String serverUrl = "http://192.168.1.194:5000/api/sensor";

void setup() {
  Serial.begin(115200);

  // pins
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(PIR_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  digitalWrite(BUZZER_PIN, LOW);

  // WiFi connection
  Serial.print("Connecting to WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected!");
  Serial.println(WiFi.localIP());
}

void loop() {
  // PIR
  int movement = digitalRead(PIR_PIN);

  // HC-SR04 measurement
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 30000);
  float distance = (duration > 0) ? (duration * 0.0343 / 2) : -1;

  // Buzzer logic
  int buzzerState = 0;
  if (distance > 0 && distance < 50) {
    buzzerState = 1;
    digitalWrite(BUZZER_PIN, HIGH);
  } else {
    buzzerState = 0;
    digitalWrite(BUZZER_PIN, LOW);
  }

  // ---- Create JSON ----
  StaticJsonDocument<200> jsonDoc;
  jsonDoc["distance"] = distance;
  jsonDoc["movement"] = movement;
  jsonDoc["buzzer"] = buzzerState;

  String jsonString;
  serializeJson(jsonDoc, jsonString);

  Serial.println("Sending JSON:");
  Serial.println(jsonString);

  // ---- HTTP POST ----
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    int httpResponseCode = http.POST(jsonString);

    Serial.print("Response: ");
    Serial.println(httpResponseCode);

    http.end();
  }

  delay(1000);
}
