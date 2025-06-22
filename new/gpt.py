import openai
from config import OPENAI_API_KEY

def chatgpt_request(prompt):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ти трейдер-аналітик. Варто чекати чи купляти пару? Відповідь в форматі json"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
        )
        result = response.choices[0].message.content.strip()
        print(result)
        if not result:
            return None
        return result

    except Exception as e:
        print(f"❌ Помилка в chatgpt_request: {e}")
        return None
