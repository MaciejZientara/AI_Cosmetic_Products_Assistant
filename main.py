import openai
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys

APIKey = ''
# openai.api_key = APIKey

client = openai.OpenAI(api_key=APIKey)

system_prompt = "Wpisz prompt systemowy tutaj"
context = "Tutaj wiedza asystenta"
user_query = "Tutaj pytanie"

messages=[ 
  {"role": "system", "content": system_prompt},
  {"role": "user", "content": user_query},
  {"role": "assistant", "content": context}
]

chat_completion = client.chat.completions.create(
  messages=messages,
  model="gpt-4o-mini",
  temperature=0,
)

print(chat_completion.choices[0].message.content.strip())
# print(chat_completion.usage)





def app_init():
  app = QApplication(sys.argv)
  win = QMainWindow()
  # initial X,Y position on screen, initial X, Y window size 
  win.setGeometry(200,200,300,300)
  win.setWindowTitle("BuisnessAI")

  sys.exit(app.exec_()) # close python script with app
  return win


####################### main ####################### 

# initialize
window = app_init()
# run app
window.show()
