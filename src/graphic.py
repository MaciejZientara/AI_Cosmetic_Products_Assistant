import global_vars
import logger
import webbrowser
from pathlib import Path
from os.path import dirname
from sys import exit, argv
from scrapper import is_data_present, get_data

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

        # Add check for downloaded data and processed (inform to click buttons)
        self.addTextLabel("Witaj! Jak mogę ci pomóc?","AI")

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

    def saveConsoleToFile(self):
        dir_path = dirname(dirname(__file__))
        with open(Path(dir_path, "consolLog.txt"), "w", encoding="utf8") as txt_file:
            for i in range(self.ConsoleLayout.count()): 
                widget = self.ConsoleLayout.itemAt(i).widget()
                if type(widget) == QtWidgets.QPushButton: # itemObject
                    txt_file.write("Product: " + widget.objectName())
                else: # label -> AI/User message
                    if "AI" in widget.objectName():
                        txt_file.write("AI: " + widget.text())
                    elif "USER" in widget.objectName():
                        txt_file.write("USER: " + widget.text())
                    else:
                        continue # padding, skip saving to file
                txt_file.write("\n")


    def addTextLabel(self, text, side):
        label = QtWidgets.QLabel(self)
        self.ConsoleLayout.addWidget(label)
        # label.setLayoutDirection(QtCore.Qt.LeftToRight)
        label.setAutoFillBackground(True)
        if side == "USER":
            label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
            label.setObjectName("USER_Msg")
        elif side == "AI":
            label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
            label.setObjectName("AI_Msg")
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
        itemObject.setObjectName(item["url"])
        self.ConsoleLayout.addWidget(itemObject)
        itemLayout = QtWidgets.QGridLayout(itemObject)

        #                                    Horizontal                         Vertical
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)

        itemObject.setSizePolicy(size_policy)
        itemObject.setMinimumHeight(50)

        labelName = QtWidgets.QLabel(itemObject)
        labelName.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        labelName.setText(item["title"])
        labelName.setSizePolicy(size_policy)
        labelName.setMinimumHeight(25)
        labelName.setWordWrap(True)
        labelName.setMinimumSize(labelName.sizeHint())

        labelCost = QtWidgets.QLabel(itemObject)
        labelCost.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        labelCost.setText(item["price"]+" zł")
        labelCost.setSizePolicy(size_policy)
        labelCost.setMinimumHeight(25)
        labelCost.setWordWrap(True)

        labelDescr = QtWidgets.QLabel(itemObject)
        labelDescr.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        labelDescr.setText(item["description"])
        labelDescr.setSizePolicy(size_policy)
        labelDescr.setMinimumHeight(25)
        labelDescr.setWordWrap(True)
        labelDescr.setMinimumSize(labelDescr.sizeHint())

        labelQuantity = QtWidgets.QLabel(itemObject)
        labelQuantity.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        labelQuantity.setText(item["capacity"])
        labelQuantity.setSizePolicy(size_policy)
        labelQuantity.setMinimumHeight(25)
        labelQuantity.setWordWrap(True)

        itemLayout.addWidget(labelName,     0, 0, 1, 4)
        itemLayout.addWidget(labelDescr,    1, 0, 1, 4)
        itemLayout.addWidget(labelCost,     0, 4, 1, 1)
        itemLayout.addWidget(labelQuantity, 1, 4, 1, 1)
        
        itemObject.updateGeometry()
        itemObject.clicked.connect(lambda: webbrowser.open(item["url"]))


    def processInput(self):
        # if self.textInput.text() == "": # used to test addItemObject
        #     self.addItemObject(
        #         {
        #             "ingridients": "Isododecane, Hydrogenated Polyisobutene, Mica, Hydrogenated Polydecene, Quaternium-18 Bentonite, Parfum, Sorbitan Isostearate, Caprylyl Glycol, Phenoxyethanol, Ethylhexylglycerin, Limnanthes Alba Seed Oil, Camellia Japonica Seed Oil, Simmondsia Chinensis Seed Oil, Olea Europaea Fruit Oil, Benzyl Alcohol, Benzyl Salicylate, Cinnamyl Alcohol, Citronellol, Eugenol, Geraniol, Linalool, [+/-: CI 77891, CI 45410, CI 15850].",
        #             "title": "WIBO Lady of My Heart  róż do policzków, w formie kwiatu róży, nr 2;",
        #             "price": "49.99",
        #             "url": "https://www.rossmann.pl/Produkt/Lakiery-hybrydowe/Hi-Hybrid-Easy-3in1-lakier-hybrydowy-602-Pink-Lemonade-5-ml,2095288,13032",
        #             "description": "Delikatnie rozświetlający róż do policzków Lady of My Heart to produkt utrzymany w ciepłej tonacji, inspirowany płatkami kwiatów róży.\nMocno napigmentowana",
        #             "capacity": "10 g"
        #         }
        #     )
        #     return

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

        # when adding widget to grid:
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
        if is_data_present():
            dialogResponse = CustomDialog(
                "Data already exists",
                "Data already exists in data directory. Do you want to delete existing data and download new data?"
                ).exec()
            
            if dialogResponse == QtWidgets.QMessageBox.No:
                return
            
            rescrap = True

        get_data(rescrap)


    def processButtonFunction(self):
        if not is_data_present():
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
        self.SaveConsoleButton.clicked.connect(self.Console.saveConsoleToFile)


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
