#!/bin/bash

# Check if MQTT broker is reachable (standard Mosquitto port 1883)
echo "🔍 Prüfe MQTT-Verfügbarkeit..."

if nc -z homeassistant 1883; then
  echo "✅ MQTT ist erreichbar."
else
  echo "❌ MQTT ist nicht erreichbar. Bitte installiere den Mosquitto-Broker in Home Assistant."
  exit 1
fi

echo "🚀 Starte Webhook Server..."
python3 app/main.py