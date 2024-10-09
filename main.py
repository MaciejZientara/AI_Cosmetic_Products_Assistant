import openai
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys

####################### graphic ####################### 

def run_app():
  app = QApplication(sys.argv)
  win = QMainWindow()
  # initial X,Y position on screen, initial X, Y window size 
  win.setGeometry(200,200,1200,800)
  win.setWindowTitle("BuisnessAI")

  win.show()
  sys.exit(app.exec_()) # close python script on app exit


####################### functionality - RAG ####################### 



####################### functionality - openAI ####################### 

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


####################### main ####################### 

if __name__ == '__main__':
  run_app()
