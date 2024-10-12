import openai


# APIKey = ''
# # openai.api_key = APIKey

# client = openai.OpenAI(api_key=APIKey)

system_prompt = "Wpisz prompt systemowy tutaj"
context = "Tutaj wiedza asystenta"
user_query = "Tutaj pytanie"

messages=[ 
  {"role": "system", "content": system_prompt},
  {"role": "user", "content": user_query},
  {"role": "assistant", "content": context}
]

# chat_completion = client.chat.completions.create(
#   messages=messages,
#   model="gpt-4o-mini",
#   temperature=0,
# )

# print(chat_completion.choices[0].message.content.strip())
# print(chat_completion.usage)
