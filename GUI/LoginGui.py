# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'LoginDialog.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_LoginDialog(object):
    def setupUi(self, LoginDialog):
        LoginDialog.setObjectName("LoginDialog")
        LoginDialog.resize(400, 171)
        self.buttonBox = QtWidgets.QDialogButtonBox(LoginDialog)
        self.buttonBox.setGeometry(QtCore.QRect(200, 120, 191, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.label = QtWidgets.QLabel(LoginDialog)
        self.label.setGeometry(QtCore.QRect(40, 40, 72, 15))
        self.label.setObjectName("label")
        self.passwdLabel = QtWidgets.QLabel(LoginDialog)
        self.passwdLabel.setGeometry(QtCore.QRect(40, 80, 72, 15))
        self.passwdLabel.setObjectName("passwdLabel")
        self.nameEdit = QtWidgets.QLineEdit(LoginDialog)
        self.nameEdit.setGeometry(QtCore.QRect(142, 40, 181, 21))
        self.nameEdit.setObjectName("nameEdit")
        self.passwdEdit = QtWidgets.QLineEdit(LoginDialog)
        self.passwdEdit.setGeometry(QtCore.QRect(142, 80, 181, 21))
        self.passwdEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.passwdEdit.setObjectName("passwdEdit")
        self.registerRadio = QtWidgets.QRadioButton(LoginDialog)
        self.registerRadio.setGeometry(QtCore.QRect(10, 130, 91, 19))
        self.registerRadio.setChecked(True)
        self.registerRadio.setObjectName("registerRadio")
        self.visitorRadio = QtWidgets.QRadioButton(LoginDialog)
        self.visitorRadio.setGeometry(QtCore.QRect(110, 130, 81, 19))
        self.visitorRadio.setObjectName("visitorRadio")

        self.retranslateUi(LoginDialog)
        self.buttonBox.accepted.connect(LoginDialog.accept)
        self.buttonBox.rejected.connect(LoginDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(LoginDialog)

    def retranslateUi(self, LoginDialog):
        _translate = QtCore.QCoreApplication.translate
        LoginDialog.setWindowTitle(_translate("LoginDialog", "登陆界面"))
        self.label.setText(_translate("LoginDialog", "Name:"))
        self.passwdLabel.setText(_translate("LoginDialog", "Password:"))
        self.registerRadio.setText(_translate("LoginDialog", "Register"))
        self.visitorRadio.setText(_translate("LoginDialog", "Visitor"))


