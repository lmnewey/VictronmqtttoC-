import json
import time
import paho.mqtt.client as mqtt
import re

# List to store MQTT topics that were published to
published_topics = []

# Dictionary to store MQTT topic structure and data
mqtt_data = {}

def on_message(client, userdata, message):
    global mqtt_data, published_topics
    mqtt_topic = message.topic
    mqtt_payload = json.loads(message.payload.decode("utf-8"))

    # Append the MQTT topic to the list of published topics
    published_topics.append(mqtt_topic)

    # Parse the MQTT topic to create a nested structure in the dictionary
    topic_parts = mqtt_topic.split("/")
    current_level = mqtt_data
    for part in topic_parts:
        if part not in current_level:
            current_level[part] = {}
        current_level = current_level[part]

    # Store the MQTT payload data in the final leaf node
    current_level["data"] = mqtt_payload

# Create an MQTT client
client = mqtt.Client()

# Set up the message callback
client.on_message = on_message

# Connect to the MQTT broker
client.connect("192.168.0.200", 1883, 60)

# Subscribe to all MQTT topics
client.subscribe("#")

# Listen for MQTT messages for 30 minutes
client.loop_start()
time.sleep(2 * 60)
client.loop_stop()

# Serialize the MQTT data dictionary to JSON
mqtt_data_json = json.dumps(mqtt_data, indent=4)

# Save the JSON data to a text file
with open("mqtt_data.txt", "w") as file:
    file.write(mqtt_data_json)

# Save the list of published topics to a separate file
with open("published_topics.txt", "w") as topics_file:
    topics_file.write("\n".join(published_topics))

# Convert the published topics to regular expressions and save to a file
topic_patterns = []
for topic in published_topics:
    regex_pattern = re.escape(topic)
    regex_pattern = regex_pattern.replace("\\#", ".*?")
    topic_patterns.append(regex_pattern)

with open("topic_patterns.txt", "w") as regex_file:
    regex_file.write("\n".join(topic_patterns))

print("Data saved to mqtt_data.txt")
print("Published topics saved to published_topics.txt")
print("Topic patterns saved to topic_patterns.txt")


