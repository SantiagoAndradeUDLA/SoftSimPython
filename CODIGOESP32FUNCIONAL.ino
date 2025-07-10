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
const char* ssid = "iPhone"; // TODO: Replace with your WiFi SSID
const char* password = "patosgordos"; // TODO: Replace with your WiFi password

// Flask server details
// IMPORTANT: Replace YOUR_FLASK_SERVER_IP with the actual IP address of the computer running the Flask server.
// For example, if your computer's IP address is 192.168.1.100, then serverName should be:
// const char* serverName = "http://192.168.1.100:5000/update";
const char* serverName = "http://172.20.10.14:5000/update";

void setup() {
    // Start serial communication for debugging
    Serial.begin(115200);
    Serial.println("PZEM-004T V3.0 Power Meter - ESP32");
    Serial.println("Verifique que los pines PZEM_RX_PIN (GPIO16) y PZEM_TX_PIN (GPIO17) esten conectados correctamente al PZEM-004T.");

    // Connect to WiFi
    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi...");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi Connected!");
    Serial.print("IP Address (ESP32): ");
    Serial.println(WiFi.localIP());
    Serial.print("Flask Server URL: ");
    Serial.println(serverName);


    // Uncomment to reset the energy counter on the PZEM module
    // if (pzem.resetEnergy()) {
    //     Serial.println("Energy counter has been reset.");
    // } else {
    //     Serial.println("Error resetting energy counter.");
    // }
}

// Function to send data to the Flask server
void sendDataToServer(float voltage, float current, float power, float energy) {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        
        Serial.print("Sending data to server: ");
        Serial.println(serverName);

        http.begin(serverName); // Specify the URL
        http.addHeader("Content-Type", "application/json"); // Specify content type as JSON

        // Create JSON document. Adjust size if more data fields are added.
        StaticJsonDocument<256> jsonDoc; 
        jsonDoc["voltaje"] = voltage;
        jsonDoc["corriente"] = current;
        jsonDoc["potencia"] = power;
        jsonDoc["energia"] = energy; // Energy in Wh

        String requestBody;
        serializeJson(jsonDoc, requestBody); // Convert JSON object to string

        Serial.print("Request body: ");
        Serial.println(requestBody);

        // Send HTTP POST request
        int httpResponseCode = http.POST(requestBody);

        if (httpResponseCode > 0) {
            String response = http.getString();
            Serial.print("HTTP Response code: ");
            Serial.println(httpResponseCode);
            Serial.print("Server response: ");
            Serial.println(response);
        } else {
            Serial.print("Error sending POST: ");
            Serial.println(httpResponseCode);
            // Print more details about the error if available (ESP32 HTTPClient specific)
            // Serial.printf("[HTTP] POST... failed, error: %s\n", http.errorToString(httpResponseCode).c_str());
        }
        http.end(); // Free resources
    } else {
        Serial.println("WiFi Disconnected. Cannot send data to server.");
    }
}

void loop() {
    // It's good practice to check if the PZEM module is connected and responding.
    // The readAddress() function can be used for this, or simply checking if readings are NaN.
    // Serial.print("PZEM Address: "); Serial.println(pzem.readAddress(), HEX);

    // Read data from the PZEM sensor
    float voltage   = pzem.voltage();
    float current   = pzem.current();
    float power     = pzem.power();
    float energy    = pzem.energy();
    float frequency = pzem.frequency();
    float pf        = pzem.pf();

    // Check if all readings are valid (not NaN - Not a Number)
    if (isnan(voltage) || isnan(current) || isnan(power) || isnan(energy) || isnan(frequency) || isnan(pf)) {
        Serial.println("Error reading data from PZEM-004T. Check connections and sensor address.");
        // Optionally, you could try to re-initialize the sensor or take other recovery actions here.
    } else {
        // Print values to Serial Monitor for debugging
        Serial.println("--- PZEM-004T Readings ---");
        Serial.print("Voltage: ");      Serial.print(voltage);   Serial.println(" V");
        Serial.print("Current: ");      Serial.print(current, 3);Serial.println(" A"); // Display current with 3 decimal places for mA resolution
        Serial.print("Power: ");        Serial.print(power);     Serial.println(" W");
        Serial.print("Energy: ");       Serial.print(energy, 3); Serial.println(" kWh");
        Serial.print("Frequency: ");    Serial.print(frequency); Serial.println(" Hz");
        Serial.print("Power Factor: "); Serial.println(pf);
        Serial.println("--------------------------");

        // Send data to the Flask server
        // The PZEM library returns energy in kWh. The Flask server/GUI expects Wh.
        // Therefore, multiply energy by 1000 before sending.
        float energyWh = energy * 1000.0;
        sendDataToServer(voltage, current, power, energyWh);
    }

    Serial.println(); // Add a blank line for readability in Serial Monitor
    // Wait before next reading. Adjust delay as needed.
    // Consider the time it takes for the HTTP request to complete.
    delay(5000); 
}