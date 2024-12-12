from openai import OpenAI
import os
import base64
from io import BytesIO
import json

client= OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Encoding image file: base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def process_images_in_folder(folder_path):
    all_responses = []

    # Process each image file in the folder
    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):  # filter out image files
            image_path = os.path.join(folder_path, filename)
            image_base64 = encode_image_to_base64(image_path)

            # request OpenAI API
            response = client.chat.completions.create(
              model="gpt-4o",
              messages=[
                  { "role": "system", "content": "Analyze the provided diagram image by dividing it into major groups and organizing it into nodes and edges. Then, create a consistent JSON object based on the following requirements: \n \
                    - 'file_name' \n \
                    - 'summary': Description of the diagram in Korean \n \
                    - 'components': [{'id': '1', 'text': '', 'node': []},\n \
                    {'id': '2', 'text': '', 'node': []}] \n \
                    - 'connections': [{'from': '1', 'to': '2', 'text': '', 'type': 'line', 'color': '#000000', 'direction': 'true'},\n \
                    {'from': '2', 'to': '1', 'text': '', 'type': 'line', 'color': '#ffffff', 'direction': 'true'}]\n \
                    - 'node': If there are multiple lines of text within the diagram, represent them with line breaks in the 'text' field. \n \
                    - Each 'node' must include mandatory values 'id' and 'text'. If there are additional hierarchical structures within a group, use a recursive declaration of 'nodes'. \n \
                    - 'connections': Represents the relationships between connected nodes and must reflect the number of arrows or line segments shown in the diagram. \n \
                    - Each 'connection' must include the mandatory values 'from', 'to', 'text', 'type', 'color', and 'direction'. \n \
                    - 'type' must be one of the following values: 'line', 'dashed', 'dotted', or 'unknown'.\n \
                    - 'color' should contain the recognized color of the line segment in the format of a color code like '#ff0000'.\n \
                    - 'direction' should be set to 'true' if there is an arrow indicating direction, and 'false' if there is no direction, such as with a line segment.\n \
                    The JSON should be based strictly on the contents of the diagram and should not invent new information." 
                  },
                  {
                    "role": "user",
                    "content": [
                      {"type": "text", 
                      "text": "입력된 다이어그램 이미지를 분석해서 JSON 객체로 만들어주세요."
                      },
                      {
                        "type": "image_url",
                        "image_url": {
                          "url": f"data:image/jpeg;base64,{image_base64}"
                        },
                      },
                    ],
                  }
                ],
                temperature=0.1,
                top_p=1.0,
                max_tokens=10000,
                response_format={
                      "type": "json_schema",
                      "json_schema": {
                          "name": "pseudo_labeling",
                          "schema": {
                              "type": "object",
                              "properties": {
                                  "file_name": {"type": "string"},
                                  "summary": {"type": "string"},
                                  "node_count": {"type": "integer"},
                                  "connection_count": {"type": "integer"},
                                  "components": 
                                    { 
                                      "type": "object",
                                      "properties": {
                                          "id": {"type": "integer"},
                                          "text": {"type": "string"},
                                          "node": {"type": "object"},
                                      },
                                      "required": ["id", "text", "node"],
                                      "additionalProperties": False
                                    },
                                  "connections": {
                                      "type": "object",
                                      "properties": {
                                          "from": {"type": "integer"},
                                          "to": {"type": "integer"},
                                          "text": {"type": "string"},
                                          "type": {"type": "string"},
                                          "color": {"type": "string"},
                                          "direction": {"type": "boolean"},
                                          "thickness": {"type": "integer"}
                                      },
                                      "required": ["from", "to", "text", "type", "color", "direction", "thickness"],
                                      "additionalProperties": False
                                  },
                                },
                                "required": ["file_name", "summary", "components", "connections"],
                                "additionalProperties": False
                              },
                          },
                      },
              )

            response_data = response.choices[0].message.content
            # print(response_data)
            output_file = f"{os.path.splitext(filename)[0]}.json"
            
            # Save individual JSON file for each image
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json.loads(response_data), f, ensure_ascii=False, indent=4, separators=(",", ": "))
            
            print(f"JSON file for {filename} saved as {output_file}")

    return all_responses

# Process all images in the folder
folder_path ="test"
all_responses = process_images_in_folder(folder_path)