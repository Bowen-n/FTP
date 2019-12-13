import sys
import PyQt5
from PyQt5.QtWidgets import *
from GUI.LoginGui import Ui_LoginDialog
import time
from threading import Thread

class LoginDialog(QDialog,Ui_LoginDialog):
    def __init__(self,parent=None):
        super(LoginDialog,self).__init__(parent)
        self.setupUi(self)
        self.registerRadio.clicked.connect(self.enableEdit)
        self.visitorRadio.clicked.connect(self.disableEdit)
        self.nameEdit.textEdited.connect(self.checkNameEdit)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.enableEdit()  #set register mode by default
        self.show()
        self.isAccepted = self.exec_() 

    def checkNameEdit(self):
        if not self.nameEdit.text() and not self.visitorRadio.isChecked():
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        elif self.nameEdit.text() and self.registerRadio.isChecked():
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)

    def enableEdit(self):
        self.nameEdit.setEnabled(True)
        self.passwdEdit.setEnabled(True)
        self.checkNameEdit()

    def disableEdit(self):
        self.nameEdit.setEnabled(False)
        self.passwdEdit.setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        self.buttonBox.button(QDialogButtonBox.Ok).setFocus()

class BaseProgressWidget(QWidget):
    updateProgress = PyQt5.QtCore.pyqtSignal([bytes])
    def __init__(self, text='', parent=None):
        super(BaseProgressWidget, self).__init__(parent)
        self.setFixedHeight(50)
        self.text  = text
        self.progressbar = QProgressBar()
        self.progressbar.setTextVisible(True)

        self.updateProgress.connect(self.set_value)

        self.bottomBorder = QWidget()
        self.bottomBorder.setStyleSheet("""
            background: palette(shadow);
        """)
        self.bottomBorder.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed))
        self.bottomBorder.setMinimumHeight(1)

        self.label  = QLabel(self.text)
        self.label.setStyleSheet("""
            font-weight: bold;
        """)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10,0,10,0)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.progressbar)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.mainLayout.addLayout(self.layout)
        self.mainLayout.addWidget(self.bottomBorder)
        self.setLayout(self.mainLayout)
        self.totalValue = 0


    def set_value(self, value):
        self.totalValue += len(value)
        self.progressbar.setValue(self.totalValue)

    def set_max(self, value):
        self.progressbar.setMaximum(value)


class DownloadProgressWidget(BaseProgressWidget):
    def __init__(self, text='Downloading', parent=None):
        super(DownloadProgressWidget, self).__init__(text, parent)
        style ="""
        QProgressBar {
            border: 2px solid grey;
            border-radius: 5px;
            text-align: center;
        }

        QProgressBar::chunk {
            background-color: #37DA7E;
            width: 20px;
        }"""
        self.progressbar.setStyleSheet(style)


class UploadProgressWidget(BaseProgressWidget):
    def __init__(self, text='Uploading', parent=None):
        super(UploadProgressWidget, self).__init__(text, parent)
        style ="""
        QProgressBar {
            border: 2px solid grey;
            border-radius: 5px;
            text-align: center;
        }

        QProgressBar::chunk {
            background-color: #88B0EB;
            width: 20px;
        }"""
        self.progressbar.setStyleSheet(style)

class ProgressDialog(QMainWindow):
    addProgress_sig = PyQt5.QtCore.pyqtSignal(str, str, int)
    show_sig = PyQt5.QtCore.pyqtSignal(int)
    def __init__(self, parent=None):
        super(ProgressDialog, self).__init__(parent)
        self.resize(500, 250)
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.setCentralWidget(self.scrollArea)

        self.centralWidget = QWidget()
        self.scrollArea.setWidget(self.centralWidget)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(PyQt5.QtCore.Qt.AlignTop)
        self.layout.setContentsMargins(0,10,0,0)
        self.centralWidget.setLayout(self.layout)

        self.addProgress_sig.connect(self.addProgress)
        self.widgetlist = []
        
        self.show_sig.connect(self.show_window)



    def addProgressbar(self, progressbar):
        self.layout.addWidget(progressbar)

    def addProgress(self, type, title, size):
        if type not in ['download', 'upload']:
            raise "type must 'download' or 'upload'"

        if type == 'download':
            pb = DownloadProgressWidget(text=title)
        else:
            pb = UploadProgressWidget(text=title)
        pb.set_max(size)
        self.addProgressbar(pb)
        self.widgetlist.append(pb)
        print('addProgress.done')
        # print(len(self.widgetlist))
    
    def show_window(self, show_):
        if show_:
            self.show()
        else:
            self.close()

def loginDialog(parent=None):
    login = LoginDialog(parent)
    if not login.isAccepted:
        return False
    elif login.visitorRadio.isChecked():
        return ('anonymous', 'anonymous', True)
    else:
        return (str(login.nameEdit.text()), str(login.passwdEdit.text()), True)


class MessageBox(QMessageBox):
    message_sig = PyQt5.QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        super(MessageBox, self).__init__(parent)
        self.message_sig.connect(self.inform)
    
    def inform(message):
        self.information(parent, 'Message', message)




if __name__ == '__main__':
    # app=QApplication(sys.argv)
    # myWin=LoginDialog()
    # #myWin.show()
    # sys.exit(app.exec_())

    def testProgressDialog():
        import random
        number = [x for x in range(1, 101)]
        progresses = [ ]
        while len(progresses) <= 20: progresses.append(random.choice(number))
        app = QApplication([])
        pbs = ProgressDialog()
        for i in progresses:
            pb = pbs.addProgress(type='download', title='/bowen.txt', size=100)
            pb.set_value(' '*i)

        for i in progresses:
            pb = pbs.addProgress(type='upload', title='upload', size=100)
            pb.set_value(' '*i)
        pbs.show()
        app.exec_()
    
    def test2():
        app = QApplication([])
        pbs = ProgressDialog()
        pb = pbs.addProgress(type='download', title='/bowen.txt', size=90)
        def _download():
            for i in range(101):
                pb.updateProgress.emit('a'*i)
                time.sleep(0.01)
                # print(i)
        Thread(target=_download).start()
        pbs.show()
        app.exec_()
            

    # testProgressDialog()
    test2()

