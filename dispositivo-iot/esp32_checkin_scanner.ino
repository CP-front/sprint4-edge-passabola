/****************************************************************************************
 * Visionary Solutions:
 * Arthur Araújo Tenório - 562272
 * Breno Gonçalves Báo - 564037
 * Rodrigo Cardoso Tadeo - 562010
 * Vinicius Cavalcanti dos Reis - 562063
 *
 * PROJETO "PASSA A BOLA ENCONTROS" (COM FIWARE DESCOMPLICADO)
 * Sistema de Check-in por Presença
 * Versão Final CORRIGIDA - Alinhada com a Collection do Postman (Modelo Estático)
 ****************************************************************************************/
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>

// ==========================================================
// ÁREA DE CONFIGURAÇÃO - PREENCHA COM SEUS DADOS
// ==========================================================
const char* ssid = "NOME_DA_SUA_REDE_WIFI"; // Seu SSID
const char* password = "SENHA_DA_SUA_REDE_WIFI."; // Sua Senha
const char* mqtt_server = "IP_PUBLICO_DA_SUA_VM"; // Seu IP da VM
// ==========================================================

// --- Configurações do Projeto (para alinhar com a collection "FIWARE Descomplicado") ---
const char* APIKEY = "TEF"; // API Key definida na collection do Postman
const char* DEVICE_ID = "scanner01"; // ID do nosso dispositivo estático
#define SERVICE_UUID "4fafc201-1fb5-459e-8fcc-c5c9c331914b"  // UUID

// --- Variáveis Globais ---
WiFiClient espClient;
PubSubClient client(espClient);
BLEScan* pBLEScan;
int scanTime = 5; // Tempo de escaneamento em segundos

// --- Função para Publicar o Check-in (FORMATO ULTRALIGHT 2.0) ---
void publishCheckin(String playerId) {
    if (!client.connected()) return;

    // Tópico para o dispositivo estático (continua o mesmo)
    String topic = String("/") + APIKEY + "/" + DEVICE_ID + "/attrs";

    // Payload no formato UltraLight 2.0: "chave|valor"
    String payload = "p|" + playerId; // A chave "p" corresponde ao object_id no Postman

    Serial.println("--- NOVO CHECK-IN (MODELO FIWARE - ULTRALIGHT) ---");
    Serial.print("Dispositivo Fixo reportando: ");
    Serial.println(DEVICE_ID);
    Serial.print("Tópico: ");
    Serial.println(topic);
    Serial.print("Payload (dados enviados): ");
    Serial.println(payload);

    // Publica a string de texto simples
    client.publish(topic.c_str(), payload.c_str());
}

// --- Classe de Callback: chamada quando um dispositivo BLE é encontrado ---
class MyAdvertisedDeviceCallbacks: public BLEAdvertisedDeviceCallbacks {
    void onResult(BLEAdvertisedDevice advertisedDevice) {
        if (advertisedDevice.haveServiceUUID() && advertisedDevice.getServiceUUID().equals(BLEUUID(SERVICE_UUID))) {
            String pId = advertisedDevice.getAddress().toString().c_str();
            pId.replace(":", "");
            Serial.print("Beacon detectado! ID: ");
            Serial.println(pId);
            publishCheckin(pId);
            pBLEScan->stop();
        }
    }
};

// --- Funções de Conexão (Wi-Fi e MQTT) ---
void setup_wifi() {
    delay(10);
    Serial.println();
    Serial.print("Conectando-se: ");
    Serial.println(ssid);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWi-Fi conectado!");
}

void reconnect_mqtt() {
    while (!client.connected()) {
        Serial.print("Tentando conexão MQTT...");
        if (client.connect("esp32-scanner")) {
            Serial.println(" conectado!");
        } else {
            Serial.print(" falhou, rc=");
            Serial.print(client.state());
            Serial.println(" tentando novamente em 5 segundos");
            delay(5000);
        }
    }
}

// --- Função Setup: executada uma vez ---
void setup() {
    Serial.begin(115200);
    setup_wifi();
    client.setServer(mqtt_server, 1883);
    BLEDevice::init("");
    pBLEScan = BLEDevice::getScan(); // Atribui o objeto de scanner à nossa variável global
    pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
    pBLEScan->setActiveScan(true);
    pBLEScan->setInterval(100);
    pBLEScan->setWindow(99);
}

// --- Função Loop: executada repetidamente ---
void loop() {
    if (!client.connected()) {
        reconnect_mqtt();
    }
    client.loop();
    Serial.println("\nIniciando nova varredura...");
    pBLEScan->start(scanTime, false);
    Serial.println("Varredura concluída.");
    delay(2000);
}