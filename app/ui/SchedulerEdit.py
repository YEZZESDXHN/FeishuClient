# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SchedulerEdit.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialog,
    QDialogButtonBox, QHBoxLayout, QLabel, QLineEdit,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_SchedulerEdit(object):
    def setupUi(self, SchedulerEdit):
        if not SchedulerEdit.objectName():
            SchedulerEdit.setObjectName(u"SchedulerEdit")
        SchedulerEdit.resize(403, 211)
        self.verticalLayout = QVBoxLayout(SchedulerEdit)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_2 = QLabel(SchedulerEdit)
        self.label_2.setObjectName(u"label_2")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_2.addWidget(self.label_2)

        self.comboBox_JobName = QComboBox(SchedulerEdit)
        self.comboBox_JobName.addItem("")
        self.comboBox_JobName.setObjectName(u"comboBox_JobName")

        self.horizontalLayout_2.addWidget(self.comboBox_JobName)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(SchedulerEdit)
        self.label.setObjectName(u"label")
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QSize(80, 0))

        self.horizontalLayout.addWidget(self.label)

        self.lineEdit_JobID = QLineEdit(SchedulerEdit)
        self.lineEdit_JobID.setObjectName(u"lineEdit_JobID")
        self.lineEdit_JobID.setEnabled(False)

        self.horizontalLayout.addWidget(self.lineEdit_JobID)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_3 = QLabel(SchedulerEdit)
        self.label_3.setObjectName(u"label_3")
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_3.addWidget(self.label_3)

        self.comboBox_JobType = QComboBox(SchedulerEdit)
        self.comboBox_JobType.addItem("")
        self.comboBox_JobType.addItem("")
        self.comboBox_JobType.setObjectName(u"comboBox_JobType")

        self.horizontalLayout_3.addWidget(self.comboBox_JobType)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_4 = QLabel(SchedulerEdit)
        self.label_4.setObjectName(u"label_4")
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_4.addWidget(self.label_4)

        self.lineEdit_JobParam = QLineEdit(SchedulerEdit)
        self.lineEdit_JobParam.setObjectName(u"lineEdit_JobParam")

        self.horizontalLayout_4.addWidget(self.lineEdit_JobParam)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.verticalSpacer = QSpacerItem(20, 18, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.buttonBox = QDialogButtonBox(SchedulerEdit)
        self.buttonBox.setObjectName(u"buttonBox")
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.horizontalLayout_5.addWidget(self.buttonBox)


        self.verticalLayout.addLayout(self.horizontalLayout_5)


        self.retranslateUi(SchedulerEdit)
        self.buttonBox.accepted.connect(SchedulerEdit.accept)
        self.buttonBox.rejected.connect(SchedulerEdit.reject)

        QMetaObject.connectSlotsByName(SchedulerEdit)
    # setupUi

    def retranslateUi(self, SchedulerEdit):
        SchedulerEdit.setWindowTitle(QCoreApplication.translate("SchedulerEdit", u"Dialog", None))
        self.label_2.setText(QCoreApplication.translate("SchedulerEdit", u"job_name", None))
        self.comboBox_JobName.setItemText(0, QCoreApplication.translate("SchedulerEdit", u"\u540c\u6b65Defects", None))

        self.label.setText(QCoreApplication.translate("SchedulerEdit", u"job_id", None))
        self.label_3.setText(QCoreApplication.translate("SchedulerEdit", u"job_type", None))
        self.comboBox_JobType.setItemText(0, QCoreApplication.translate("SchedulerEdit", u"cron", None))
        self.comboBox_JobType.setItemText(1, QCoreApplication.translate("SchedulerEdit", u"interval", None))

        self.label_4.setText(QCoreApplication.translate("SchedulerEdit", u"job_param", None))
    # retranslateUi

