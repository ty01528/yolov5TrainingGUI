import sys
from logging import info

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox, QMainWindow
from train import run
from ui.home_ui import Ui_MainWindow
from PyQt5.QtCore import QThread, pyqtSignal
from ui.cfgParser import getYaml, generate_dataset, setYaml


class setupUI(Ui_MainWindow):
    def __init__(self):
        self.cocoYaml = None
        self.startTrainThread = startTrain()

    def startUi(self, window):
        self.setupUi(window)
        self.setSlot()

    # 设置槽函数
    def setSlot(self):
        self.cocoYamlSelect.clicked.connect(self.cocoYamlSelect_click)
        self.picDirSelect.clicked.connect(self.picDirSelect_click)
        self.annoDirSelect.clicked.connect(self.annoDirSelect_click)
        self.startTrain.clicked.connect(self.startTrain_click)
        self.outputDirSelect.clicked.connect(self.outputDirSelect_click)

    # 选择配置文件
    def cocoYamlSelect_click(self):
        directory = QtWidgets.QFileDialog.getOpenFileName(None, "选取文件", "./", "Yaml Files (*.yml *.yaml)")[0]
        if directory == "" or directory is None:
            return
        self.cocoYamlText.setText(directory)
        self.cocoYaml = getYaml(directory)

    # 选择图片文件夹
    def picDirSelect_click(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(None, "选取图片文件夹", "./")
        if directory == "" or directory is None:
            return
        self.picDirText.setText(directory)
        print("图片文件夹："+directory)

    # 选择标注文件夹
    def annoDirSelect_click(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(None, "选取标注文件夹", "./")
        if directory == "" or directory is None:
            return
        self.annoDirText.setText(directory)
        print("标注文件夹"+directory)

    # 选择输出文件夹
    def outputDirSelect_click(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(None, "选取模型存储文件夹", "./")
        if directory == "" or directory is None:
            return
        self.outputDirText.setText(directory)
        print("模型输出文件夹"+directory)

    # 开始训练
    def startTrain_click(self):
        try:
            self.startTrain.setDisabled(True)
            self.statusBar.showMessage("开始训练")
            if (self.picDirText == "" or self.picDirText is None
                    or self.annoDirText == "" or self.annoDirText is None
                    or self.cocoYamlText == "" or self.cocoYamlText is None):
                raise Exception("请先选择图片文件夹、标注文件夹、配置文件！")
            print("开始训练")
            # 使用给定的文件夹与分割比例生成训练集与测试集
            print("分割生成训练集与测试集")

            trainPicDir, testPicDir = generate_dataset(self.picDirText.text(), self.annoDirText.text(),
                                                           self.trainPercentVal.text(), self.outputDirText.text())
            print("分割生成训练集与测试集完成！")

            # 使用以上生成的数据集生成新的yaml文件
            self.statusBar.showMessage("生成配置文件")
            print("生成配置文件")
            self.cocoYaml = getYaml(self.cocoYamlText.text())
            self.cocoYaml['train'] = trainPicDir
            self.cocoYaml['val'] = testPicDir
            setYaml(self.outputDirText.text() + "/train.yaml", self.cocoYaml)
            print("生成配置文件完成！")

            self.statusBar.showMessage("生成训练参数")
            print("生成训练参数")
            # 设置训练参数
            kwargs = {"data": self.outputDirText.text()+"/train.yaml",
                      "imgsz": int(self.picSizeVal.currentText()),
                      "weights": str.lower(self.modelSelVal.currentText()) + ".pt",
                      "batch_size": int(self.batchSizeVal.currentText()),
                      "epochs": int(self.epochsVal.text()),
                      "project": self.outputDirText.text(),
                      "name": "exp"}
            self.startTrainThread.setKwargs(kwargs)

            self.statusBar.showMessage("正在训练")
            print("正在训练")
            self.startTrainThread.start()
        except Exception as e:
            self.statusBar.showMessage("训练失败")
            print("训练失败！")
            QMessageBox.question(None, 'Error！', str(e), QMessageBox.Ok, QMessageBox.Cancel)
            return
        finally:
            self.startTrain.setEnabled(True)
            return


class startTrain(QThread, Ui_MainWindow):

    def __init__(self):
        super(startTrain, self).__init__()
        self.kwargs = None

    def __del__(self):
        self.wait()

    def run(self):
        # 开始训练
        run(**self.kwargs)
        print("训练完成！")

    def setKwargs(self, kwargs):
        self.kwargs = kwargs


def exceptOutConfig(exctype, value, tb):
    print('My Error Information:')
    print('Type:', exctype)
    print('Value:', value)
    print('Traceback:', tb)


# 重定向print输出到textBrowser
class EmittingStr(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)  # 定义一个发送str的信号

    def write(self, text):
        self.textWritten.emit(str(text))


class ControlBoard(QMainWindow, setupUI):
    def __init__(self):
        super(ControlBoard, self).__init__()
        self.setupUi(self)
        # 下面将输出重定向到textBrowser中
        sys.stdout = EmittingStr(textWritten=self.outputWritten)
        sys.stderr = EmittingStr(textWritten=self.outputWritten)

    def outputWritten(self, text):
        cursor = self.textBrowser.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.textBrowser.setTextCursor(cursor)
        self.textBrowser.ensureCursorVisible()
