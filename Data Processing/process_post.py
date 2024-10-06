from openai import OpenAI
client = OpenAI()

response = client.chat.completions.create(
  model="gpt-4o",
  messages=[
    {
      "role": "system",
      "content": [
        {
          "type": "text",
          "text": "Your goal is to read post  with comments in json format and return json. This is the template of return\n[{\"short _description\": [short description of post 1], \"location\": \"[location of post 1, full address]\", \"positive\": \"[True if post is positive]\", \"post_classification\": \"[classification of post 1]\",\"address_type\": [type of address:  exexact location or street or district or city, etc. ]}, {\"short _description\": [short description of post 2], \"location\": \"[location of post 2, full address]\", \"positive\": \"[True if post is positive]\", \"post_classification\": \"[classification of post 2]\", \"address_type\": [type of address:  exexact location or street or district or city, etc. ]}]\nSPLIT RESPONSE IN LIST OF JSON IF POST CONTAIN MULTIPLE LOCATIONS\nWRITE RESPONCE IN ENGLISH\nTHE CHANEL IS ABOUT Solomianskyi District in Kyiv\nthis is the list of classes of changes: \n[\n    \"Traffic Congestion\",\n    \"Air Pollution\",\n    \"Overpopulation\",\n    \"Housing Affordability\",\n    \"Homelessness\",\n    \"Crime Rates\",\n    \"Infrastructure Strain\",\n    \"Waste Management\",\n    \"Water and Sanitation Issues\",\n    \"Income Inequality\",\n    \"Public Health Challenges\",\n    \"Noise Pollution\",\n    \"Urban Sprawl\",\n    \"Limited Green Spaces\",\n    \"Education System Strain\",\n    \"Economic Instability\",\n    \"Energy Demand\",\n    \"Climate Change Impact\",\n    \"Transportation Issues\",\n    \"Social Isolation\",\n    \"Improved public transportation routes\",\n    \"Development of new green spaces and parks\",\n    \"Implementation of renewable energy projects\",\n    \"Expansion of affordable housing initiatives\",\n    \"Launch of community health programs\",\n    \"Upgrading of urban infrastructure\",\n    \"Introduction of bike lanes and pedestrian zones\",\n    \"Enhancement of waste recycling systems\",\n    \"Installation of smart city technologies\",\n    \"Promotion of cultural and educational events\",\n    \"Community engagement and participation initiatives\",\n    \"Revitalization of historic districts\",\n    \"Education system improvements\",\n    \"Economic development programs\",\n    \"Increased accessibility for people with disabilities\",\n    \"Public safety enhancements\",\n    \"Environmental conservation efforts\",\n    \"Affordable internet and technology access\",\n    \"Water and sanitation system upgrades\",\n    \"Disaster preparedness and resilience planning\"\n]"
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
          "text": "```json\n[\n    {\n        \"short_description\": \"Traffic congestion due to a tram stopping at the intersection.\",\n        \"location\": \"Hlybochytska Street, Kyiv\",\n        \"positive\": \"False\",\n        \"post_classification\": \"Traffic Congestion\",\n        \"address_type\": \"Street\"\n    },\n    {\n        \"short_description\": \"Traffic congestion due to a tram stopping at the intersection.\",\n        \"location\": \"Sichovykh Striltsiv Street, Kyiv\",\n        \"positive\": \"False\",\n        \"post_classification\": \"Traffic Congestion\",\n        \"address_type\": \"Street\"\n    },\n    {\n        \"short_description\": \"Traffic congestion due to a tram stopping at the intersection.\",\n        \"location\": \"Illyenka Street, Kyiv\",\n        \"positive\": \"False\",\n        \"post_classification\": \"Traffic Congestion\",\n        \"address_type\": \"Street\"\n    }\n]\n```"
        }
      ]
    }
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