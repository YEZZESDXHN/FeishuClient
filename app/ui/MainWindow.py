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
    QPushButton, QSizePolicy, QSpacerItem, QSplitter,
    QTabWidget, QTextEdit, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(697, 468)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_5 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.splitter = QSplitter(self.centralwidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        self.tabWidget = QTabWidget(self.splitter)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.verticalLayout_4 = QVBoxLayout(self.tab_2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.groupBox_2 = QGroupBox(self.tab_2)
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

        self.pushButton_FeishuClient = QPushButton(self.groupBox_2)
        self.pushButton_FeishuClient.setObjectName(u"pushButton_FeishuClient")

        self.horizontalLayout_7.addWidget(self.pushButton_FeishuClient)

        self.pushButton_FeishuWsClient = QPushButton(self.groupBox_2)
        self.pushButton_FeishuWsClient.setObjectName(u"pushButton_FeishuWsClient")

        self.horizontalLayout_7.addWidget(self.pushButton_FeishuWsClient)


        self.verticalLayout_2.addLayout(self.horizontalLayout_7)


        self.horizontalLayout_12.addWidget(self.groupBox_2)

        self.groupBox = QGroupBox(self.tab_2)
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
        self.label_8 = QLabel(self.groupBox)
        self.label_8.setObjectName(u"label_8")
        sizePolicy1.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy1)

        self.horizontalLayout_6.addWidget(self.label_8)

        self.comboBox_CBProject = QComboBox(self.groupBox)
        self.comboBox_CBProject.setObjectName(u"comboBox_CBProject")

        self.horizontalLayout_6.addWidget(self.comboBox_CBProject)

        self.pushButton_GetProject = QPushButton(self.groupBox)
        self.pushButton_GetProject.setObjectName(u"pushButton_GetProject")
        sizePolicy1.setHeightForWidth(self.pushButton_GetProject.sizePolicy().hasHeightForWidth())
        self.pushButton_GetProject.setSizePolicy(sizePolicy1)

        self.horizontalLayout_6.addWidget(self.pushButton_GetProject)


        self.verticalLayout.addLayout(self.horizontalLayout_6)


        self.horizontalLayout_12.addWidget(self.groupBox)


        self.verticalLayout_4.addLayout(self.horizontalLayout_12)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_5 = QLabel(self.tab_2)
        self.label_5.setObjectName(u"label_5")
        sizePolicy1.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy1)
        self.label_5.setMinimumSize(QSize(75, 20))

        self.horizontalLayout_5.addWidget(self.label_5)

        self.lineEdit_BitableUrl = QLineEdit(self.tab_2)
        self.lineEdit_BitableUrl.setObjectName(u"lineEdit_BitableUrl")
        sizePolicy2.setHeightForWidth(self.lineEdit_BitableUrl.sizePolicy().hasHeightForWidth())
        self.lineEdit_BitableUrl.setSizePolicy(sizePolicy2)
        self.lineEdit_BitableUrl.setMinimumSize(QSize(120, 0))

        self.horizontalLayout_5.addWidget(self.lineEdit_BitableUrl)


        self.verticalLayout_3.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_6 = QLabel(self.tab_2)
        self.label_6.setObjectName(u"label_6")
        sizePolicy1.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy1)
        self.label_6.setMinimumSize(QSize(75, 20))

        self.horizontalLayout_8.addWidget(self.label_6)

        self.comboBox_BitableDateTable = QComboBox(self.tab_2)
        self.comboBox_BitableDateTable.setObjectName(u"comboBox_BitableDateTable")
        sizePolicy2.setHeightForWidth(self.comboBox_BitableDateTable.sizePolicy().hasHeightForWidth())
        self.comboBox_BitableDateTable.setSizePolicy(sizePolicy2)
        self.comboBox_BitableDateTable.setEditable(False)

        self.horizontalLayout_8.addWidget(self.comboBox_BitableDateTable)

        self.pushButton_RefreshDataTable = QPushButton(self.tab_2)
        self.pushButton_RefreshDataTable.setObjectName(u"pushButton_RefreshDataTable")
        sizePolicy1.setHeightForWidth(self.pushButton_RefreshDataTable.sizePolicy().hasHeightForWidth())
        self.pushButton_RefreshDataTable.setSizePolicy(sizePolicy1)
        self.pushButton_RefreshDataTable.setMaximumSize(QSize(50, 16777215))

        self.horizontalLayout_8.addWidget(self.pushButton_RefreshDataTable)


        self.verticalLayout_3.addLayout(self.horizontalLayout_8)


        self.verticalLayout_4.addLayout(self.verticalLayout_3)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.label_7 = QLabel(self.tab_2)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout_9.addWidget(self.label_7)

        self.comboBox_ManualTrigger = QComboBox(self.tab_2)
        self.comboBox_ManualTrigger.setObjectName(u"comboBox_ManualTrigger")
        self.comboBox_ManualTrigger.setEnabled(True)
        sizePolicy2.setHeightForWidth(self.comboBox_ManualTrigger.sizePolicy().hasHeightForWidth())
        self.comboBox_ManualTrigger.setSizePolicy(sizePolicy2)

        self.horizontalLayout_9.addWidget(self.comboBox_ManualTrigger)

        self.pushButton_ManualTrigger = QPushButton(self.tab_2)
        self.pushButton_ManualTrigger.setObjectName(u"pushButton_ManualTrigger")
        self.pushButton_ManualTrigger.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButton_ManualTrigger.sizePolicy().hasHeightForWidth())
        self.pushButton_ManualTrigger.setSizePolicy(sizePolicy1)

        self.horizontalLayout_9.addWidget(self.pushButton_ManualTrigger)


        self.verticalLayout_4.addLayout(self.horizontalLayout_9)

        self.verticalSpacer = QSpacerItem(20, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer)

        self.tabWidget.addTab(self.tab_2, "")
        self.tab_scheduler = QWidget()
        self.tab_scheduler.setObjectName(u"tab_scheduler")
        self.verticalLayout_7 = QVBoxLayout(self.tab_scheduler)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.tabWidget.addTab(self.tab_scheduler, "")
        self.splitter.addWidget(self.tabWidget)
        self.textEdit = QTextEdit(self.splitter)
        self.textEdit.setObjectName(u"textEdit")
        self.splitter.addWidget(self.textEdit)

        self.verticalLayout_5.addWidget(self.splitter)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 697, 33))
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"\u98de\u4e66", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"App ID\uff1a", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"App Secret\uff1a", None))
        self.pushButton_FeishuClient.setText(QCoreApplication.translate("MainWindow", u"\u521d\u59cb\u5316", None))
        self.pushButton_FeishuWsClient.setText(QCoreApplication.translate("MainWindow", u"\u957f\u8fde\u63a5", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"CodeBearm", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u8d26\u53f7\uff1a", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"\u5bc6\u7801\uff1a", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"\u9879\u76ee\uff1a", None))
        self.pushButton_GetProject.setText(QCoreApplication.translate("MainWindow", u"\u5237\u65b0", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"\u591a\u7ef4\u8868\u683c\uff1a", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"\u6570\u636e\u8868", None))
        self.pushButton_RefreshDataTable.setText(QCoreApplication.translate("MainWindow", u"\u5237\u65b0", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"\u624b\u52a8\u89e6\u53d1\u4efb\u52a1\uff1a", None))
        self.pushButton_ManualTrigger.setText(QCoreApplication.translate("MainWindow", u"\u8fd0\u884c", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"\u914d\u7f6e", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_scheduler), QCoreApplication.translate("MainWindow", u"\u4efb\u52a1", None))
    # retranslateUi

