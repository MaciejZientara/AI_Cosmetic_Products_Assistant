import global_vars
import logger
from sys import exit, argv
from scrapper import isDataPresent, get_data

from PyQt5 import QtCore, QtGui, QtWidgets


class CustomDialog(QtWidgets.QMessageBox):
    existingDialog = None

    def __init__(self, title, msg):
        if self.existingDialog != None:
            self.existingDialog.deleteLater()
            self.existingDialog = None

        super().__init__()
        self.existingDialog = self

        self.setWindowTitle(title)
        self.setText(msg)

        self.setIcon(QtWidgets.QMessageBox.Question)

        self.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

class console(QtWidgets.QScrollArea):
    def __init__(self, parent = None, textInput = None):
        super().__init__(parent)
        self.textInput = textInput
        
        self.ConsoleLayoutHolder = QtWidgets.QWidget()
        self.setWidget(self.ConsoleLayoutHolder)

        self.setWidgetResizable(True)
        self.setGeometry(QtCore.QRect(0, 0, 840, 750))
        self.setObjectName("Console")
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        self.ConsoleLayout = QtWidgets.QVBoxLayout(self.ConsoleLayoutHolder)
        self.ConsoleLayout.setObjectName("ConsoleLayout")

        logger.UIconsole = self
        self.initConsole()

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

    def keepScrollDown(self):
        self.verticalScrollBar().setValue(
            self.verticalScrollBar().maximum()
        )


    def addTextLabel(self, text, side):
        label = QtWidgets.QLabel(self)
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
        itemObject = QtWidgets.QPushButton(self)
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

    def processInput(self):
        if self.textInput.text() == "":
            return # do not process empty input text

        if self.paddingCount > 0:
            self.paddingCount -= 1
            padding = self.ConsoleLayout.itemAt(0).widget()
            self.ConsoleLayout.removeWidget(padding)
            padding.deleteLater()
            padding = None

        self.addTextLabel(self.textInput.text(), "USER")
        # pass text to AI
        self.textInput.clear()


class customGUI(object):
    def setupUi(self, Window):
        self.windowGrid = QtWidgets.QGridLayout(Window)
        self.windowGrid.setObjectName("windowGrid")

        # addWidget( a0: QWidget, row: int, column: int, rowSpan: int, columnSpan: int, alignment: Alignment | AlignmentFlag)

        self.DownloadDataButton = QtWidgets.QPushButton(Window)
        self.DownloadDataButton.setObjectName("DownloadData")
        self.DownloadDataButton.setText("Download Data")
        self.windowGrid.addWidget(self.DownloadDataButton, 0, 0, 1, 1)
        
        self.ClearButton = QtWidgets.QPushButton(Window)
        self.ClearButton.setObjectName("Clear")
        self.ClearButton.setText("Clear")
        self.windowGrid.addWidget(self.ClearButton, 0, 1, 1, 1)
        
        self.ProcessDataButton = QtWidgets.QPushButton(Window)
        self.ProcessDataButton.setObjectName("ProcessData")
        self.ProcessDataButton.setText("Process Data")
        self.windowGrid.addWidget(self.ProcessDataButton, 1, 0, 1, 1)

        self.SaveConsoleButton = QtWidgets.QPushButton(Window)
        self.SaveConsoleButton.setObjectName("SaveConsole")
        self.SaveConsoleButton.setText("Save Console")
        self.windowGrid.addWidget(self.SaveConsoleButton, 1, 1, 1, 1)

        self.textInput = QtWidgets.QLineEdit(Window)
        self.textInput.setObjectName("textInput")
        self.windowGrid.addWidget(self.textInput, 3, 0, 1, 2)
        
        self.Console = console(Window, self.textInput)
        self.windowGrid.addWidget(self.Console, 2, 0, 1, 2)

        QtCore.QMetaObject.connectSlotsByName(Window)


    def downloadButtonFunction(self):
        rescrap = False
        if isDataPresent():
            dialogResponse = CustomDialog(
                "Data already exists",
                "Data already exists in data directory. Do you want to delete existing data and download new data?"
                ).exec()
            
            if dialogResponse == QtWidgets.QMessageBox.No:
                return
            
            rescrap = True

        get_data(rescrap)


    def processButtonFunction(self):
        if not isDataPresent():
            dialog = CustomDialog(
                "Data missing",
                "No data found in data directory. Do you want to download data now?"
                ).exec()
            
            if dialog == QtWidgets.QMessageBox.Yes:
                get_data()
            else:
                return

        print("processData")


    def connectSignals(self):
        self.Console.verticalScrollBar().rangeChanged.connect(self.Console.keepScrollDown)
        self.textInput.returnPressed.connect(self.Console.processInput)
        self.ClearButton.clicked.connect(self.Console.resetConsole)
        self.DownloadDataButton.clicked.connect(self.downloadButtonFunction)
        self.ProcessDataButton.clicked.connect(self.processButtonFunction)


class CustomWindow(QtWidgets.QWidget,customGUI):
    def __init__(self, parent = None,):
        super().__init__(parent)
        # self.setObjectName("Window")
        self.setWindowTitle("CosmeticAssistant")
        self.resize(880, 840)
        self.setupUi(self)
        self.connectSignals()
        # initial X,Y position on screen, initial X, Y window size 
        # self.setGeometry(200,200,1200,800)


# to get python code from app_design.ui run: pyuic5 app_design.ui
def run_app(args):
  app = QtWidgets.QApplication([])
  win = CustomWindow()
  win.show()
  exit(app.exec_()) # close python script on app exit
