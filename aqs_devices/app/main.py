from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import socket

app = Flask(__name__)

MQTT_BROKER = "homeassistant"
MQTT_PORT = 1883
MQTT_PREFIX = "homeassistant"

client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

def mqtt_discovery(sensor, value, sender_ip):
    sensor_id = f"{sensor}_{sender_ip.replace('.', '_')}"
    base_topic = f"{MQTT_PREFIX}/sensor/{sensor_id}"
    config_topic = f"{base_topic}/config"
    state_topic = f"{base_topic}/state"
    
    unit_map = {
        "temperature": "°C",
        "pressure": "mbar",
        "consumption": "ml",
        "rainlevel": "mm"
    }

    device_class_map = {
        "temperature": "temperature",
        "pressure": "pressure",
        "consumption": None,
        "rainlevel": "precipitation"
    }

    config_payload = {
        "name": f"{sensor}_{sender_ip}",
        "state_topic": state_topic,
        "unit_of_measurement": unit_map.get(sensor),
        "device_class": device_class_map.get(sensor),
        "unique_id": sensor_id,
        "force_update": True
    }

    client.publish(config_topic, payload=jsonify(config_payload).get_data(as_text=True), retain=True)
    client.publish(state_topic, payload=str(value), retain=True)

@app.route('/', methods=['POST'])
def receive():
    data = request.json
    sender_ip = request.remote_addr

    if not data:
        return jsonify({"error": "Kein JSON empfangen"}), 400

    for key in ['temperature', 'pressure', 'consumption', 'rainlevel']:
        if key in data:
            val = float(data[key])
            if key == 'temperature':
                val = val / 10.0
            elif key == 'rainlevel':
                val = val * 0.5
            mqtt_discovery(key, val, sender_ip)

    if 'valve' in data:
        valve_state = int(data['valve'])
        switch_id = f"valve_{sender_ip.replace('.', '_')}"
        config_topic = f"{MQTT_PREFIX}/switch/{switch_id}/config"
        command_topic = f"{MQTT_PREFIX}/switch/{switch_id}/set"
        state_topic = f"{MQTT_PREFIX}/switch/{switch_id}/state"

        config_payload = {
            "name": f"Valve {sender_ip}",
            "command_topic": command_topic,
            "state_topic": state_topic,
            "unique_id": switch_id,
            "payload_on": "100",
            "payload_off": "0"
        }

        client.publish(config_topic, payload=jsonify(config_payload).get_data(as_text=True), retain=True)
        client.publish(state_topic, payload=str(valve_state), retain=True)

    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)