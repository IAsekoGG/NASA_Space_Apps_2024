from http.client import responses

from openai import OpenAI
import json
import re
from tqdm import tqdm

client = OpenAI(
    api_key='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')

with open("Солома INFO - Солом'янський район_no_comments.json", 'r') as f:
    data = json.load(f)

res = []

def get_response(input_text):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "Your goal is to read post  with comments in json format and return json. This is the template of return\n[{\"short _description\": [short description of post 1], \"location\": \"[location of post 1, full address]\", \"positive\": \"[True if post is positive]\", \"post_classification\": \"[classification of post 1]\",\"address_type\": [type of address:  exexact location or street or district or city, etc. ]}, {\"short _description\": [short description of post 2], \"location\": \"[location of post 2, full address]\", \"positive\": \"[True if post is positive]\", \"post_classification\": \"[classification of post 2]\", \"address_type\": [type of address:  exexact location or street or district or city, etc. ]}]\n-SPLIT RESPONSE IN LIST OF JSON IF POST CONTAIN MULTIPLE LOCATIONS\n-WRITE RESPONCE IN ENGLISH\n-THE CHANEL IS ABOUT Solomianskyi District in Kyiv\nthis is the list of classes of changes: \n[\n    \"Traffic Congestion\",\n    \"Air Pollution\",\n    \"Overpopulation\",\n    \"Housing Affordability\",\n    \"Homelessness\",\n    \"Crime Rates\",\n    \"Infrastructure Strain\",\n    \"Waste Management\",\n    \"Water and Sanitation Issues\",\n    \"Income Inequality\",\n    \"Public Health Challenges\",\n    \"Noise Pollution\",\n    \"Urban Sprawl\",\n    \"Limited Green Spaces\",\n    \"Education System Strain\",\n    \"Economic Instability\",\n    \"Energy Demand\",\n    \"Climate Change Impact\",\n    \"Transportation Issues\",\n    \"Social Isolation\",\n    \"Improved public transportation routes\",\n    \"Development of new green spaces and parks\",\n    \"Implementation of renewable energy projects\",\n    \"Expansion of affordable housing initiatives\",\n    \"Launch of community health programs\",\n    \"Upgrading of urban infrastructure\",\n    \"Introduction of bike lanes and pedestrian zones\",\n    \"Enhancement of waste recycling systems\",\n    \"Installation of smart city technologies\",\n    \"Promotion of cultural and educational events\",\n    \"Community engagement and participation initiatives\",\n    \"Revitalization of historic districts\",\n    \"Education system improvements\",\n    \"Economic development programs\",\n    \"Increased accessibility for people with disabilities\",\n    \"Public safety enhancements\",\n    \"Environmental conservation efforts\",\n    \"Affordable internet and technology access\",\n    \"Water and sanitation system upgrades\",\n    \"Disaster preparedness and resilience planning\"\n]"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "❗️Великий затор на вулиці Глибочицькій, Січових Стрільців та Іллєнка\\n\\nСтав трамвай прямо на перехресті, рух перекрито в усіх напрямках"
                    }
                ]
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "```json\n[\n    {\n        \"short_description\": \"Large traffic jam due to a stopped tram at the intersection.\",\n        \"location\": \"Hlybochytska Street, Kyiv\",\n        \"positive\": \"False\",\n        \"post_classification\": \"Traffic Congestion\",\n        \"address_type\": \"street\"\n    },\n    {\n        \"short_description\": \"Traffic congestion due to a tram stopped at the intersection.\",\n        \"location\": \"Sichovykh Striltsiv Street, Kyiv\",\n        \"positive\": \"False\",\n        \"post_classification\": \"Traffic Congestion\",\n        \"address_type\": \"street\"\n    },\n    {\n        \"short_description\": \"Complete halt in traffic at the intersection caused by a tram.\",\n        \"location\": \"Illienka Street, Kyiv\",\n        \"positive\": \"False\",\n        \"post_classification\": \"Traffic Congestion\",\n        \"address_type\": \"street\"\n    }\n]\n```"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": input_text

                    }
                ]
            },
        ],
        temperature=0.85,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={
            "type": "text"
        }
    )
    response_text = response.choices[0].message.content

    pattern = r'\{\s*"short_description":\s*".+?",\s*"location":\s*".+?",\s*"positive":\s*".+?",\s*"post_classification":\s*".+?",\s*"address_type":\s*".+?"\s*\}'

    # Find all matches in the string
    matches = re.findall(pattern, response_text)

    # Parsing the found matches as JSON objects
    parsed_matches = [json.loads(match) for match in matches]

    # Print out the parsed matches
    return parsed_matches


for post in tqdm(data[::-1][:30]):
    text = post['text']
    gpt_response = get_response(text)
    post['gpt_response'] = gpt_response
    res.append(post)

with open("Солома INFO - Солом'янський район_no_comments_gpt_resp.json", 'w', encoding='utf-8') as f:
    json.dump(res, f,  ensure_ascii=False, indent=4)

