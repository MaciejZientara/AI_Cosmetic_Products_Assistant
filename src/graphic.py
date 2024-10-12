import global_vars
from PyQt5.QtWidgets import QApplication, QMainWindow
from sys import exit, argv

def run_app(args):
  app = QApplication(argv)
  win = QMainWindow()
  # initial X,Y position on screen, initial X, Y window size 
  win.setGeometry(200,200,1200,800)
  win.setWindowTitle(global_vars.APP_NAME)

  win.show()
  exit(app.exec_()) # close python script on app exit
