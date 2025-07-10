#include <PZEM004Tv30.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h> // For creating JSON objects

// Define the UART2 RX and TX pins on ESP32 (Connect these to PZEM-004T)
#define PZEM_RX_PIN 16  // ESP32 RX (Connect to PZEM TX)
#define PZEM_TX_PIN 17  // ESP32 TX (Connect to PZEM RX)

// Initialize the PZEM sensor using Hardware Serial2
PZEM004Tv30 pzem(Serial2, PZEM_RX_PIN, PZEM_TX_PIN);

// WiFi credentials
const char* ssid = "iPhone"; // Replace with your WiFi SSID
const char* password = "patosgordos"; // Replace with your WiFi password

// Flask server details
const char* serverName = "http://YOUR_FLASK_SERVER_IP:5000/update"; // Replace with your Flask server IP

void setup() {
    Serial.begin(115200);
    Serial.println("PZEM-004T V3.0 Power Meter - ESP32");

    // Connect to WiFi
    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi...");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());

    // Uncomment to reset the energy counter
    // pzem.resetEnergy();
}

void sendDataToServer(float voltage, float current, float power, float energy) {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(serverName); // Specify the URL
        http.addHeader("Content-Type", "application/json");

        // Create JSON document
        StaticJsonDocument<200> jsonDoc;
        jsonDoc["voltaje"] = voltage;
        jsonDoc["corriente"] = current;
        jsonDoc["potencia"] = power;
        jsonDoc["energia"] = energy;

        String requestBody;
        serializeJson(jsonDoc, requestBody);

        int httpResponseCode = http.POST(requestBody);

        if (httpResponseCode > 0) {
            String response = http.getString();
            Serial.print("HTTP Response code: ");
            Serial.println(httpResponseCode);
            Serial.print("Response: ");
            Serial.println(response);
        } else {
            Serial.print("Error on sending POST: ");
            Serial.println(httpResponseCode);
        }
        http.end(); // Free resources
    } else {
        Serial.println("WiFi Disconnected. Cannot send data.");
    }
}

void loop() {
    Serial.print("Custom Address: ");
    Serial.println(pzem.readAddress(), HEX);

    // Read data from the PZEM sensor
    float voltage   = pzem.voltage();
    float current   = pzem.current();
    float power     = pzem.power();
    float energy    = pzem.energy();
    float frequency = pzem.frequency();
    float pf        = pzem.pf();

    if(isnan(voltage)){
        Serial.println("Error reading voltage");
    } else if (isnan(current)) {
        Serial.println("Error reading current");
    } else if (isnan(power)) {
        Serial.println("Error reading power");
    } else if (isnan(energy)) {
        Serial.println("Error reading energy");
    } else if (isnan(frequency)) {
        Serial.println("Error reading frequency");
    } else if (isnan(pf)) {
        Serial.println("Error reading power factor");
    } else {
        // Print values
        Serial.print("Voltage: ");      Serial.print(voltage);   Serial.println(" V");
        Serial.print("Current: ");      Serial.print(current);   Serial.println(" A");
        Serial.print("Power: ");        Serial.print(power);     Serial.println(" W");
        Serial.print("Energy: ");       Serial.print(energy, 3); Serial.println(" kWh"); // kWh is usually more standard for energy than Wh
        Serial.print("Frequency: ");    Serial.print(frequency); Serial.println(" Hz");
        Serial.print("Power Factor: "); Serial.println(pf);

        // Send data to server
        // Note: The Flask server expects 'energia' in Wh, but PZEM gives kWh.
        // We'll send kWh for now, and can adjust on server or here if needed.
        // For consistency with the original gui.py (which expected Wh), let's convert energy to Wh.
        sendDataToServer(voltage, current, power, energy * 1000); // Convert kWh to Wh
    }

    Serial.println();
    delay(5000);  // Wait 5 seconds before next reading (increased from 2 to allow for HTTP request time)
}
