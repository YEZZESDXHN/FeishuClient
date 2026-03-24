# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QSpacerItem, QStatusBar,
    QTextEdit, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(585, 502)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_4 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.groupBox_2 = QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName(u"label_3")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy1)
        self.label_3.setMinimumSize(QSize(75, 20))

        self.horizontalLayout_3.addWidget(self.label_3)

        self.lineEdit_AppID = QLineEdit(self.groupBox_2)
        self.lineEdit_AppID.setObjectName(u"lineEdit_AppID")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.lineEdit_AppID.sizePolicy().hasHeightForWidth())
        self.lineEdit_AppID.setSizePolicy(sizePolicy2)
        self.lineEdit_AppID.setMinimumSize(QSize(120, 0))

        self.horizontalLayout_3.addWidget(self.lineEdit_AppID)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_4 = QLabel(self.groupBox_2)
        self.label_4.setObjectName(u"label_4")
        sizePolicy1.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy1)
        self.label_4.setMinimumSize(QSize(75, 20))

        self.horizontalLayout_4.addWidget(self.label_4)

        self.lineEdit_AppSecret = QLineEdit(self.groupBox_2)
        self.lineEdit_AppSecret.setObjectName(u"lineEdit_AppSecret")
        sizePolicy2.setHeightForWidth(self.lineEdit_AppSecret.sizePolicy().hasHeightForWidth())
        self.lineEdit_AppSecret.setSizePolicy(sizePolicy2)
        self.lineEdit_AppSecret.setMinimumSize(QSize(120, 0))
        self.lineEdit_AppSecret.setInputMethodHints(Qt.InputMethodHint.ImhHiddenText|Qt.InputMethodHint.ImhNoAutoUppercase|Qt.InputMethodHint.ImhNoPredictiveText|Qt.InputMethodHint.ImhSensitiveData)
        self.lineEdit_AppSecret.setEchoMode(QLineEdit.EchoMode.Password)

        self.horizontalLayout_4.addWidget(self.lineEdit_AppSecret)


        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer_2)

        self.pushButton_FeishuTest = QPushButton(self.groupBox_2)
        self.pushButton_FeishuTest.setObjectName(u"pushButton_FeishuTest")

        self.horizontalLayout_7.addWidget(self.pushButton_FeishuTest)


        self.verticalLayout_2.addLayout(self.horizontalLayout_7)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_5 = QLabel(self.groupBox_2)
        self.label_5.setObjectName(u"label_5")
        sizePolicy1.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy1)
        self.label_5.setMinimumSize(QSize(75, 20))

        self.horizontalLayout_5.addWidget(self.label_5)

        self.lineEdit_BitableUrl = QLineEdit(self.groupBox_2)
        self.lineEdit_BitableUrl.setObjectName(u"lineEdit_BitableUrl")
        sizePolicy2.setHeightForWidth(self.lineEdit_BitableUrl.sizePolicy().hasHeightForWidth())
        self.lineEdit_BitableUrl.setSizePolicy(sizePolicy2)
        self.lineEdit_BitableUrl.setMinimumSize(QSize(120, 0))

        self.horizontalLayout_5.addWidget(self.lineEdit_BitableUrl)


        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_6 = QLabel(self.groupBox_2)
        self.label_6.setObjectName(u"label_6")
        sizePolicy1.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy1)
        self.label_6.setMinimumSize(QSize(75, 20))

        self.horizontalLayout_8.addWidget(self.label_6)

        self.comboBox_BitableDateTable = QComboBox(self.groupBox_2)
        self.comboBox_BitableDateTable.setObjectName(u"comboBox_BitableDateTable")
        sizePolicy2.setHeightForWidth(self.comboBox_BitableDateTable.sizePolicy().hasHeightForWidth())
        self.comboBox_BitableDateTable.setSizePolicy(sizePolicy2)
        self.comboBox_BitableDateTable.setEditable(True)

        self.horizontalLayout_8.addWidget(self.comboBox_BitableDateTable)


        self.verticalLayout_2.addLayout(self.horizontalLayout_8)


        self.horizontalLayout_12.addWidget(self.groupBox_2)

        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        sizePolicy1.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy1)
        self.label.setMinimumSize(QSize(0, 20))

        self.horizontalLayout.addWidget(self.label)

        self.lineEdit_Username = QLineEdit(self.groupBox)
        self.lineEdit_Username.setObjectName(u"lineEdit_Username")
        sizePolicy2.setHeightForWidth(self.lineEdit_Username.sizePolicy().hasHeightForWidth())
        self.lineEdit_Username.setSizePolicy(sizePolicy2)
        self.lineEdit_Username.setMinimumSize(QSize(120, 0))
        self.lineEdit_Username.setInputMethodHints(Qt.InputMethodHint.ImhNone)
        self.lineEdit_Username.setEchoMode(QLineEdit.EchoMode.Normal)

        self.horizontalLayout.addWidget(self.lineEdit_Username)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")
        sizePolicy1.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy1)

        self.horizontalLayout_2.addWidget(self.label_2)

        self.lineEdit_Password = QLineEdit(self.groupBox)
        self.lineEdit_Password.setObjectName(u"lineEdit_Password")
        sizePolicy2.setHeightForWidth(self.lineEdit_Password.sizePolicy().hasHeightForWidth())
        self.lineEdit_Password.setSizePolicy(sizePolicy2)
        self.lineEdit_Password.setMinimumSize(QSize(120, 0))
        self.lineEdit_Password.setEchoMode(QLineEdit.EchoMode.Password)

        self.horizontalLayout_2.addWidget(self.lineEdit_Password)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer)

        self.pushButton_CBTest = QPushButton(self.groupBox)
        self.pushButton_CBTest.setObjectName(u"pushButton_CBTest")

        self.horizontalLayout_6.addWidget(self.pushButton_CBTest)


        self.verticalLayout.addLayout(self.horizontalLayout_6)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.horizontalLayout_12.addWidget(self.groupBox)


        self.verticalLayout_4.addLayout(self.horizontalLayout_12)

        self.textEdit = QTextEdit(self.centralwidget)
        self.textEdit.setObjectName(u"textEdit")

        self.verticalLayout_4.addWidget(self.textEdit)

        self.verticalLayout_4.setStretch(1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 585, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"\u98de\u4e66", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"App ID\uff1a", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"App Secret\uff1a", None))
        self.pushButton_FeishuTest.setText(QCoreApplication.translate("MainWindow", u"\u6d4b\u8bd5", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"\u591a\u7ef4\u8868\u683c\uff1a", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"\u6570\u636e\u8868", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"CodeBearm", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u8d26\u53f7\uff1a", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"\u5bc6\u7801\uff1a", None))
        self.pushButton_CBTest.setText(QCoreApplication.translate("MainWindow", u"\u6d4b\u8bd5", None))
    # retranslateUi

