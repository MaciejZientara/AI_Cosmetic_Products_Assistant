import global_vars
from PyQt5.QtWidgets import QApplication
from sys import exit, argv

from PyQt5 import QtCore, QtGui, QtWidgets


class customGUI(object):
    def setupUi(self, Window):
        self.windowGrid = QtWidgets.QGridLayout(Window)
        self.windowGrid.setObjectName("windowGrid")

        self.DownloadDataButton = QtWidgets.QPushButton(Window)
        self.DownloadDataButton.setObjectName("DownloadData")
        self.windowGrid.addWidget(self.DownloadDataButton, 0, 0, 1, 1)
        
        self.ClearButton = QtWidgets.QPushButton(Window)
        self.ClearButton.setObjectName("Clear")
        self.windowGrid.addWidget(self.ClearButton, 0, 2, 1, 1)
        
        self.ProcessDataButton = QtWidgets.QPushButton(Window)
        self.ProcessDataButton.setObjectName("ProcessData")
        self.windowGrid.addWidget(self.ProcessDataButton, 0, 1, 1, 1)
        
        self.textInput = QtWidgets.QLineEdit(Window)
        self.textInput.setObjectName("textInput")
        self.windowGrid.addWidget(self.textInput, 2, 0, 1, 3)
        
        self.Console = QtWidgets.QScrollArea(Window)
        self.ConsoleLayoutHolder = QtWidgets.QWidget()
        self.Console.setWidget(self.ConsoleLayoutHolder)

        self.Console.setWidgetResizable(True)
        self.Console.setGeometry(QtCore.QRect(0, 0, 855, 751))
        self.Console.setObjectName("Console")
        self.Console.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.Console.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        self.ConsoleLayout = QtWidgets.QVBoxLayout(self.ConsoleLayoutHolder)
        self.ConsoleLayout.setObjectName("ConsoleLayout")
        self.windowGrid.addWidget(self.Console, 1, 0, 1, 3)

        self.initConsole()

        self.retranslateUi(Window)
        QtCore.QMetaObject.connectSlotsByName(Window)


    def initConsole(self):
        self.paddingCount = 20
        for i in range(self.paddingCount):
            self.addTextLabel("","") # empty labels

        self.addTextLabel("Hello!","AI")

    def clearConsole(self):
        for i in reversed(range(self.ConsoleLayout.count())): 
            padding = self.ConsoleLayout.itemAt(i).widget()
            self.ConsoleLayout.removeWidget(padding)
            padding.deleteLater()
            padding = None

    def resetConsole(self):
        self.clearConsole()
        self.initConsole()

    def addTextLabel(self, text, side):
        label = QtWidgets.QLabel(self.Console)
        self.ConsoleLayout.addWidget(label)
        # label.setLayoutDirection(QtCore.Qt.LeftToRight)
        label.setAutoFillBackground(True)
        if side == "USER":
            label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
            # label.setObjectName("UserMsg")
        elif side == "AI":
            label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
            # label.setObjectName("AiMsg")
        else:
            pass # incorrect side argument
        label.setText(text)
        #                                    Horizontal                         Vertical
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        label.setSizePolicy(size_policy)
        label.setMinimumHeight(25)
        label.setWordWrap(True)


    def addItemObject(self, item):
        itemObject = QtWidgets.QPushButton(self.Console)
        # itemObject.setObjectName("Item")
        self.ConsoleLayout.addWidget(itemObject)
        itemLayout = QtWidgets.QGridLayout(itemObject)

        labelName = QtWidgets.QLabel(itemObject)
        labelName.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        labelName.setText()

        labelCost = QtWidgets.QLabel(itemObject)
        labelCost.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        labelCost.setText()

        labelDescr = QtWidgets.QLabel(itemObject)
        labelDescr.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        labelDescr.setText()

        labelQuantity = QtWidgets.QLabel(itemObject)
        labelQuantity.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        labelQuantity.setText()

        itemLayout.addWidget(labelName,     0, 0, 1, 1)
        itemLayout.addWidget(labelDescr,    0, 1, 1, 1)
        itemLayout.addWidget(labelCost,     1, 0, 1, 1)
        itemLayout.addWidget(labelQuantity, 1, 1, 1, 1)
        

    def retranslateUi(self, Window):
        _translate = QtCore.QCoreApplication.translate
        Window.setWindowTitle(_translate("Window", "CosmeticAssistant"))
        self.DownloadDataButton.setText(_translate("Window", "Download Data"))
        self.ClearButton.setText(_translate("Window", "Clear"))
        self.ProcessDataButton.setText(_translate("Window", "Process Data"))
        
    def processInput(self):
        if self.paddingCount > 0:
            self.paddingCount -= 1
            padding = self.ConsoleLayout.itemAt(0).widget()
            self.ConsoleLayout.removeWidget(padding)
            padding.deleteLater()
            padding = None

        self.addTextLabel(self.textInput.text(), "USER")
        # pass text to AI
        self.textInput.clear()

    def connectSignals(self):
        self.textInput.returnPressed.connect(self.processInput)
        self.ClearButton.clicked.connect(self.resetConsole)


class CustomWindow(QtWidgets.QWidget,customGUI):
    def __init__(self, parent = None,):
        super().__init__(parent)
        # self.setObjectName("Window")
        self.resize(880, 840)
        self.setupUi(self)
        self.connectSignals()
        # initial X,Y position on screen, initial X, Y window size 
        # self.setGeometry(200,200,1200,800)


# to get python code from app_design.ui run: pyuic5 app_design.ui
def run_app(args):
  app = QApplication([])
  win = CustomWindow()
  win.show()
  exit(app.exec_()) # close python script on app exit
