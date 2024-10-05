from openai import OpenAI

# Ініціалізація OpenAI клієнта
client = OpenAI(api_key='sk-jMEOk_AeFqsriX4e9WlvXuiW6xdIiDWoIaImApR-3CT3BlbkFJVeXbABn_hQ3Hb23_XLNa0lxq6MKKRSQUc_PMoAPuYA')

def get_gpt_response(user_prompt, system_prompt = "",  model="gpt-4o-mini"):
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        response_text = completion.choices[0].message.content
        total_tokens = completion.usage.total_tokens
        
        return response_text, total_tokens
    except Exception as e:
        return f"An error occurred: {e}", 0


# Приклад використання функції
if __name__ == "__main__":
    system_message = "You are a helpful assistant."
    user_message = "Say hello to the world in multiple languages."
    
    response, tokens_used = get_gpt_response(system_message, user_message)
    
    # Виведення результатів
    print("Response from GPT-4o-mini:", response)
    print("Tokens used:", tokens_used)
