#should Generate classes based on what was observed in the monitor

def generate_csharp_class(topic_list):
    class_definitions = {}

    for topic_entry in topic_list:
        topic_parts = topic_entry.split(',')[0].split(" ")[1].split('/')
        data_type = topic_entry.split(',')[2].split(":")[1].strip()

        if data_type == "NoneType":
            data_type = "object"

        if len(topic_parts) < 3:
            continue

        class_name = topic_parts[2].capitalize()
        attribute_parts = topic_parts[4:]

        if not attribute_parts:
            continue

        # Handle the "Devices" nested pattern
        if "Devices" in topic_parts:
            device_index = topic_parts.index("Devices")
            nested_class_name = f"{class_name}Device"
            attribute_parts = topic_parts[device_index+2:]

            if not attribute_parts:
                continue

            attribute_name = '_'.join(attribute_parts).replace(' ', '_').capitalize()

            if nested_class_name not in class_definitions:
                class_definitions[nested_class_name] = {}
                if class_name not in class_definitions:
                    class_definitions[class_name] = {}
                class_definitions[class_name]["Devices"] = {"type": f"List<{nested_class_name}>"}

            class_definitions[nested_class_name][attribute_name] = {"topic": topic_parts, "type": data_type}
            continue

        attribute_name = '_'.join(attribute_parts).replace(' ', '_').capitalize()

        # Handle History_daily pattern
        if "History_daily" in attribute_name:
            history_class = "HistoryDailyEntry"
            attribute_name = attribute_name.replace("History_daily_", "").split('_')
            index = attribute_name.pop(0)
            attribute_name = '_'.join(attribute_name)

            if history_class not in class_definitions:
                class_definitions[history_class] = {}

            class_definitions[history_class][attribute_name] = {"topic": topic_parts, "type": data_type}
            continue

        if class_name not in class_definitions:
            class_definitions[class_name] = {}

        # Avoid repeated properties
        if attribute_name in class_definitions[class_name]:
            continue

        class_definitions[class_name][attribute_name] = {"topic": topic_parts, "type": data_type}

    # Generate C# classes and write to output file
    with open('output_classes.cs', 'w') as output_file:
        for class_name, attributes in class_definitions.items():
            output_file.write(f"public class {class_name}\n{{\n")

            for attribute, info in attributes.items():
                if "topic" in info:
                    regex_topic = '/'.join(info['topic']).replace("+", "[^/]+").replace("#", ".*").replace(info['topic'][1], "{this.InstallationUniqueId}").replace(info['topic'][3], "{this.BusID}")
                    output_file.write(f"    public {info['type']} {attribute} {{ get; set; }}\n")
                else:
                    output_file.write(f"    public {info['type']} {attribute} {{ get; set; }} = new {info['type']}>();\n")

            output_file.write("}\n\n")

with open('mqtt_data.txt', 'r') as file:
    data = file.readlines()

generate_csharp_class(data)

# old attempt, kept for historic reasons
# def generate_csharp_class(topic_list):
#     class_definitions = {}

#     for topic_entry in topic_list:
#         topic_parts = topic_entry.split(',')[0].split(" ")[1].split('/')
#         data_type = topic_entry.split(',')[2].split(":")[1].strip()

#         if data_type == "NoneType":
#             data_type = "object"

#         if len(topic_parts) < 3:
#             continue

#         class_name = topic_parts[2].capitalize()
#         attribute_parts = topic_parts[4:]

#         if not attribute_parts:
#             continue

#         # Handle the "Devices" nested pattern
#         if "Devices" in topic_parts:
#             device_index = topic_parts.index("Devices")
#             nested_class_name = f"{class_name}_device"
#             attribute_parts = topic_parts[device_index+2:]

#             if not attribute_parts:
#                 continue

#             attribute_name = '_'.join(attribute_parts).replace(' ', '_').capitalize()
            
#             if nested_class_name not in class_definitions:
#                 class_definitions[nested_class_name] = {}

#             class_definitions[nested_class_name][attribute_name] = {"topic": topic_parts, "type": data_type}
#             continue

#         attribute_name = '_'.join(attribute_parts).replace(' ', '_').capitalize()

#         # Handle History_daily pattern
#         if "History_daily" in attribute_name:
#             history_class = "HistoryDailyEntry"
#             attribute_name = attribute_name.replace("History_daily_", "").split('_')
#             index = attribute_name.pop(0)
#             attribute_name = '_'.join(attribute_name)

#             if history_class not in class_definitions:
#                 class_definitions[history_class] = {}

#             class_definitions[history_class][attribute_name] = {"topic": topic_parts, "type": data_type}
#             continue

#         if class_name not in class_definitions:
#             class_definitions[class_name] = {}

#         # Avoid repeated properties
#         if attribute_name in class_definitions[class_name]:
#             continue

#         class_definitions[class_name][attribute_name] = {"topic": topic_parts, "type": data_type}

#     # Generate C# classes and write to output file
#     with open('output_classes.cs', 'w') as output_file:
#         for class_name, attributes in class_definitions.items():
#             output_file.write(f"public class {class_name}\n{{\n")

#             if class_name.endswith("_device"):
#                 parent_class_name = class_name.replace("_device", "")
#                 output_file.write(f"    public List<{class_name}> Devices {{ get; set; }} = new List<{class_name}>();\n\n")

#             output_file.write(f"    public string InstallationUniqueId {{ get; set; }}\n")  # Adding the unique installation id
#             output_file.write(f"    public string BusID {{ get; set; }}\n\n")  # Adding the BusID

#             for attribute, info in attributes.items():
#                 output_file.write(f"    public {info['type']} {attribute} {{ get; set; }}\n")

#             output_file.write("\n    public void HandleIncomingMessage(string topic, object payload)\n    {\n")
#             for attribute, info in attributes.items():
#                 # Convert topic to regex, make the unique ID and BusID a wildcard
#                 regex_topic = '/'.join(info['topic']).replace("+", "[^/]+").replace("#", ".*").replace(info['topic'][1], "{this.InstallationUniqueId}").replace(info['topic'][3], "{this.BusID}")
#                 output_file.write(f"        if (System.Text.RegularExpressions.Regex.IsMatch(topic, \"{regex_topic}\")\n        {{\n            {attribute} = ({info['type']})payload;\n        }}\n")
#             output_file.write("    }\n")
#             output_file.write("}\n\n")

# with open('mqtt_data.txt', 'r') as file:
#     data = file.readlines()

# generate_csharp_class(data)
