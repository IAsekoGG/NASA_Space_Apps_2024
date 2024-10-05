import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv
from langsmith import traceable

from prompts import *


# Function to preprocess data from a JSON file
def preprocess_data(input_path: str, output_path: str, source: str, min_post_length: int = 10) -> str:
    # Read input JSON file
    with open(input_path, "r", encoding="utf-8") as file:
        input_json = json.load(file) 

    posts_list = []

    # Process data if the source is Telegram ("tg")
    if source == "tg":
        for post in input_json:
            # Filter posts based on minimum length
            if len(post["text"]) > min_post_length:
                posts_list.append(post)
                # Remove specific fields from each post
                for field in ["forwarded_from", "reactions", "views"]:
                    post.pop(field, None)

    # Write processed data to output JSON file
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(posts_list, file, indent=4)

    return output_path


# Function to translate data using a specified model
@traceable(name="Translate data", metadata={"model": "GPT-4o-mini"}, project_name="nasa-hackathon")
def translate_data(model, input_path: str, output_path: str, source: str, batch_size: int, asset) -> str:
    # Read input JSON file
    with open(input_path, "r", encoding="utf-8") as file:
        input_json = json.load(file) 

    # Process data if the source is Telegram ("tg")
    if source == "tg":
        output_json = input_json.copy()
        translate_chain = TRANSLATE_ENG | model | JsonOutputParser()

        # Translate channel name
        channel_name_ua = input_json[0]["channel_name"]
        channel_name_eng = translate_chain.invoke({"messages": [{"message_id": 1, "text": channel_name_ua}], "kpi_asset": asset})["messages"][0]["text"]
        print(channel_name_eng)

        # Create message_id to index mapping for efficient updates
        message_id_map = {msg.get("message_id"): i for i, msg in enumerate(output_json)}
        
        # Process messages in batches
        total_messages = len(input_json)
        for i in range(0, total_messages, batch_size):
            print(f"{total_messages}: {i}")
            batch = input_json[i:i+batch_size]
            translated_batch = translate_chain.invoke({"messages": batch, "kpi_asset": asset})
            
            # Update output_json with translated text
            for translated_post in translated_batch["messages"]:
                message_id = translated_post["message_id"]
                if message_id in message_id_map:
                    index = message_id_map[message_id]
                    output_json[index]["channel_name"] = channel_name_eng
                    output_json[index]["text"] = translated_post["text"]
        
        # Write translated data to output JSON file
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(output_json, file, indent=4)

        return output_path


# Function to extract news and classify them as positive, negative, or neutral
# def extract_news(model, input_path: str, output_path: str, source: str, batch_size: int):
#     # Read input JSON file
#     with open(input_path, "r", encoding="utf-8") as file:
#         input_json = json.load(file) 

#     output_dict = {"positive": [], "negative": [], "neutral": []}

#     # Use a chain to extract and classify news
#     chain = EXTRACT_NEEDED | model | JsonOutputParser()

#     for i in range(0, len(input_json), batch_size):
#         classified_indices = chain.invoke({"messages": input_json[i:i+batch_size]})

#         # Categorize news based on classification
#         for item in input_json:
#             if item["message_id"] in classified_indices["positive"]:
#                 output_dict["positive"].append(item)
#             elif item["message_id"] in classified_indices["negative"]:
#                 output_dict["negative"].append(item)
    
#     # Write classified news to output JSON file
#     with open(output_path, "w", encoding="utf-8") as file:
#         json.dump(output_dict, file, indent=4)

#     return output_path


# Function to extract news and classify them as positive, negative, or neutral
@traceable(name="Extract news", metadata={"model": "GPT-4o-mini"}, project_name="nasa-hackathon")
def extract_news(model, input_path: str, output_path: str, source: str, batch_size: int, save_neutral: bool, asset) -> str:
    # Read input JSON file
    with open(input_path, "r", encoding="utf-8") as file:
        input_json = json.load(file) 

    output_dict = []

    # Use a chain to extract and classify news
    chain = EXTRACT_NEEDED | model | JsonOutputParser()

    for i in range(0, len(input_json), batch_size):
        classified_indices = chain.invoke({"messages": input_json[i:i+batch_size], "kpi_asset": asset})

        # Categorize news based on classification
        for item in input_json:
            if item["message_id"] in classified_indices["positive"]:
                item["sentiment"] = "positive"
                output_dict.append(item)
            elif item["message_id"] in classified_indices["negative"]:
                item["sentiment"] = "negative"
                output_dict.append(item)
            else:
                if save_neutral is True:
                    item["sentiment"] = "neutral"
                    output_dict.append(item)
                else:
                    pass
    
    # Write classified news to output JSON file
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(output_dict, file, indent=4)

    return output_path


@traceable(name="Classify news", metadata={"model": "GPT-4o-mini"}, project_name="nasa-hackathon")
def classify_news(model, input_path: str, output_path:str, source: str, batch_size: int, asset) -> str:
    # Read input JSON file
    with open(input_path, "r", encoding="utf-8") as file:
        input_json = json.load(file)

    # Split input_json based on sentiment
    input_json_positive = [item for item in input_json if item.get("sentiment") == "positive"]
    input_json_negative = [item for item in input_json if item.get("sentiment") == "negative"]

    # Use a chain
    chain_positive = CLASSIFY_MESSAGES_POSITIVE | model | JsonOutputParser()
    chain_negative = CLASSIFY_MESSAGES_NEGATIVE | model | JsonOutputParser()


    for i in range(0, len(input_json_positive), batch_size):
        classified_news_batch = chain_positive.invoke({"messages": input_json_positive[i:i+batch_size], "kpi_asset": asset})

        # Categorize news based on classification
        for classified_news_item in classified_news_batch["news"]:
            for item in input_json:
                if item["message_id"] == classified_news_item["id"]:
                    item["topic"] = classified_news_item["topic"]


    for i in range(0, len(input_json_negative), batch_size):
        classified_news_batch = chain_negative.invoke({"messages": input_json_negative[i:i+batch_size], "kpi_asset": asset})

        # Categorize news based on classification
        for classified_news_item in classified_news_batch["news"]:
            for item in input_json:
                if item["message_id"] == classified_news_item["id"]:
                    item["topic"] = classified_news_item["topic"]

    # Write  to output JSON file
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(input_json, file, indent=4)

    return output_path 


@traceable(name="Rephrase news", metadata={"model": "GPT-4o-mini"}, project_name="nasa-hackathon")
def rephrase_news(model, input_path: str, output_path:str, source: str, batch_size: int, asset) -> str:
    # Read input JSON file
    with open(input_path, "r", encoding="utf-8") as file:
        input_json = json.load(file)

    # Use a chain
    chain = REPHRASE_NEWS | model | JsonOutputParser()

    for i in range(0, len(input_json), batch_size):
        rephrased_news_batch = chain.invoke({"messages": input_json[i:i+batch_size], "kpi_asset": asset})

        # Categorize news based on classification
        for rephrased_news_item in rephrased_news_batch["news"]:
            for item in input_json:
                if item["message_id"] == rephrased_news_item["id"]:
                    item["rephrased_news"] = rephrased_news_item["rephrased_news"]

    # Write updated data to output JSON file
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(input_json, file, indent=4)

    return output_path 


# Function to extract location information from news items
@traceable(name="Extract location", metadata={"model": "GPT-4o-mini"}, project_name="nasa-hackathon")
def extract_location(model, input_path: str, output_path: str, source: str, batch_size: int, asset) -> str: 
    # Read input JSON file
    with open(input_path, "r", encoding="utf-8") as file:
        input_json = json.load(file) 

    # Use a chain to extract location information
    chain = EXTRACT_LOCATION | model | JsonOutputParser()
    
    # Process messages in batches
    for i in range(len(input_json)//batch_size):
        locations_batch_json = chain.invoke({"messages": input_json[i*batch_size:(i+1)*batch_size], "kpi_asset": asset})

        # Add extracted location information to each post
        for post_json, extracted_location_json in zip(input_json[i*batch_size:(i+1)*batch_size], locations_batch_json["news"]):
            post_json["location_type"] = extracted_location_json["location_type"]
            post_json["location"] = extracted_location_json["location"]

        break  # Note: This break statement limits processing to only the first batch

    # Write updated data with location information to output JSON file
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(input_json, file, indent=4)

    return output_path


def add_coordinates(model, input_path: str, output_path:str, source: str, batch_size: int, asset):
    
    return output_path

@traceable(name="Full pipeline", metadata={"version": "v.1.0.0", "model": "GPT-4o-mini"}, project_name="nasa-hackathon")
def main(files_list: list):
    for file in files_list:
        file_path = os.path.join(dir_path, file)

        search_terms = ["kpi", "dorm", "кпі", "гуртожиток", "кпи", "общежитие"]
        if any(term in file.lower() for term in search_terms):
            kpi_asset = {
                "name": "KPI (National Technical University of Ukraine 'Igor Sikorsky Kyiv Polytechnic Institute')",
                "description": "KPI, officially known as the National Technical University of Ukraine 'Igor Sikorsky Kyiv Polytechnic Institute', is one of Ukraine's largest technical universities. It is located in Kyiv, the capital of Ukraine."
            }
        else:
            kpi_asset = False

        # Step 1: Preprocess the data
        preprocessed_data_path = preprocess_data(input_path=file_path, output_path=f"{file_path[:-5]}_1_preprocessed.json", source="tg", min_post_length=10)

        # Step 2: Translate the preprocessed data
        translated_data_path = translate_data(model=gpt_4o_mini, input_path=preprocessed_data_path, output_path=f"{file_path[:-5]}_2_translated.json", source="tg", batch_size=50, asset=kpi_asset)

        # Step 3: Extract important news from the translated data
        important_data_path = extract_news(model=gpt_4o_mini, input_path=translated_data_path, output_path=f"{file_path[:-5]}_3_pos_neg.json", source="tg", batch_size=10, save_neutral=False, asset=kpi_asset)

        # Step 4: Rephrase the news (Note: input_path is empty, might be an error)
        rephrased_data_path = rephrase_news(model=gpt_4o_mini, input_path=important_data_path, output_path=f"{file_path[:-5]}_4_rephrased.json", source="tg", batch_size=10, asset=kpi_asset)

        # Step 5: Classify the news (Note: input_path is empty, might be an error)
        classified_data_path = classify_news(model=gpt_4o_mini, input_path=rephrased_data_path, output_path=f"{file_path[:-5]}_5_classified.json", source="tg", batch_size=10, asset=kpi_asset)

        # Step 6: Extract location information (Note: input_path is empty, might be an error)
        locations_data = extract_location(model=gpt_4o_mini, input_path=classified_data_path, output_path=f"{file_path[:-5]}_6_locations.json", source="tg", batch_size=50, asset=kpi_asset)

        # Step 7: Add coordinates to the data (Note: input_path is empty, might be an error)
        # coordinates_data = add_coordinates(model=gpt_4o_mini, input_path=locations_data, output_path=f"{file_path[:-5]}_7_coordinates_final.json", source="tg", batch_size=50)


if __name__ == "__main__":
    OPENAI_API_KEY = "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" # Andrii
    OPENAI_API_KEY = "sk-y0VjAvBP8mVWsHj-LDhRVzmZFXiALIEOnXAg1ljaeDT3BlbkFJR6cQXiAB0DLlVJoOTKmT7807HRuBRHg6pHdAo9jd8A" # Bohdan

    load_dotenv()

    kpi = "KPI (National Technical University of Ukraine 'Igor Sikorsky Kyiv Polytechnic Institute')"
    kpi_description = "KPI, officially known as the National Technical University of Ukraine 'Igor Sikorsky Kyiv Polytechnic Institute', is one of Ukraine's largest technical universities. It is located in Kyiv, the capital of Ukraine."

    # Initialize the GPT-4 model with specific parameters
    gpt_4o_mini = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.0000000000000001,
        api_key=OPENAI_API_KEY
    )

    # Set the directory path and get list of files
    dir_path = "data1"
    files_list = os.listdir(dir_path)

    # Process each file in the directory
    main(files_list)
