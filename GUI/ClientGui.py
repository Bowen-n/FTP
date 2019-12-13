# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ClientGui.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication,QMainWindow
import sys
from PyQt5.QtGui import QIcon
import os
app_icon_path = os.path.join(os.path.dirname(__file__), '../icons')
qIcon = lambda name: QIcon(os.path.join(app_icon_path, name))


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1100, 685)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.Local_label = QtWidgets.QLabel(Form)
        self.Local_label.setObjectName("Local_label")
        self.gridLayout.addWidget(self.Local_label, 0, 0, 1, 3)
        self.Remote_label = QtWidgets.QLabel(Form)
        self.Remote_label.setObjectName("Remote_label")
        self.gridLayout.addWidget(self.Remote_label, 0, 5, 1, 3)
        self.Local_Return = QtWidgets.QPushButton(Form)
        self.Local_Return.setObjectName("Local_Return")
        self.gridLayout.addWidget(self.Local_Return, 2, 0, 1, 1)
        self.Remote_Return = QtWidgets.QPushButton(Form)
        self.Remote_Return.setObjectName("Remote_Return")
        self.gridLayout.addWidget(self.Remote_Return, 2, 5, 1, 1)
        self.Remote_Filelist = QtWidgets.QTreeWidget(Form)
        self.Remote_Filelist.setObjectName("Remote_Filelist")
        self.gridLayout.addWidget(self.Remote_Filelist, 3, 5, 1, 4)
        self.Local_Filelist = QtWidgets.QTreeWidget(Form)
        self.Local_Filelist.setObjectName("Local_Filelist")
        self.gridLayout.addWidget(self.Local_Filelist, 3, 0, 1, 4)
        self.Local_Next = QtWidgets.QPushButton(Form)
        self.Local_Next.setObjectName("Local_Next")
        self.gridLayout.addWidget(self.Local_Next, 2, 1, 1, 1)
        self.Local_Home = QtWidgets.QPushButton(Form)
        self.Local_Home.setObjectName("Local_Home")
        self.gridLayout.addWidget(self.Local_Home, 1, 0, 1, 1)
        self.Local_Upload = QtWidgets.QPushButton(Form)
        self.Local_Upload.setObjectName("Local_Upload")
        self.gridLayout.addWidget(self.Local_Upload, 2, 2, 1, 1)
        self.Local_Connect = QtWidgets.QPushButton(Form)
        self.Local_Connect.setObjectName("Local_Connect")
        self.gridLayout.addWidget(self.Local_Connect, 2, 3, 1, 1)
        self.Local_path = QtWidgets.QLineEdit(Form)
        self.Local_path.setObjectName("Local_path")
        self.gridLayout.addWidget(self.Local_path, 1, 1, 1, 3)
        self.Remote_Home = QtWidgets.QPushButton(Form)
        self.Remote_Home.setObjectName("Remote_Home")
        self.gridLayout.addWidget(self.Remote_Home, 1, 5, 1, 1)
        self.Remote_Next = QtWidgets.QPushButton(Form)
        self.Remote_Next.setObjectName("Remote_Next")
        self.gridLayout.addWidget(self.Remote_Next, 2, 6, 1, 1)
        self.Remote_Download = QtWidgets.QPushButton(Form)
        self.Remote_Download.setObjectName("Remote_Download")
        self.gridLayout.addWidget(self.Remote_Download, 2, 7, 1, 2)
        self.Remote_path = QtWidgets.QLineEdit(Form)
        self.Remote_path.setObjectName("Remote_path")
        self.gridLayout.addWidget(self.Remote_path, 1, 6, 1, 3)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        self.Local_Home.setIcon(qIcon('home.png'))
        self.Local_Next.setIcon(qIcon('next.png'))
        self.Local_Upload.setIcon(qIcon('upload.png'))
        self.Local_Connect.setIcon(qIcon('connect.png'))
        self.Local_Return.setIcon(qIcon('back.png'))

        self.Remote_Download.setIcon(qIcon('download.png'))
        self.Remote_Next.setIcon(qIcon('next.png'))
        self.Remote_Return.setIcon(qIcon('back.png'))
        self.Remote_Home.setIcon(qIcon('home.png'))


        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "FTP"))
        self.Local_label.setText(_translate("Form", "Local"))
        self.Remote_label.setText(_translate("Form", "Remote"))
        # self.Local_Return.setText(_translate("Form", "←"))
        # self.Remote_Return.setText(_translate("Form", "←"))
        self.Remote_Filelist.headerItem().setText(0, _translate("Form", "Name"))
        self.Remote_Filelist.headerItem().setText(1, _translate("Form", "Size"))
        self.Remote_Filelist.headerItem().setText(2, _translate("Form", "Time"))
        self.Local_Filelist.headerItem().setText(0, _translate("Form", "Name"))
        self.Local_Filelist.headerItem().setText(1, _translate("Form", "Size"))
        self.Local_Filelist.headerItem().setText(2, _translate("Form", "Time"))
        # self.Local_Next.setText(_translate("Form", "→"))
        # self.Local_Home.setText(_translate("Form", "Home"))
        self.Local_Upload.setText(_translate("Form", "Upload"))
        self.Local_Connect.setText(_translate("Form", "Connect"))
        # self.Remote_Home.setText(_translate("Form", "Home"))
        # self.Remote_Next.setText(_translate("Form", "→"))
        self.Remote_Download.setText(_translate("Form", "Download"))
        
'''
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(widget)
    widget.show()
    sys.exit(app.exec_())
'''

