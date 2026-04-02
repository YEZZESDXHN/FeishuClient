# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SchedulerTable.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QHBoxLayout, QHeaderView,
    QPushButton, QSizePolicy, QSpacerItem, QTableView,
    QVBoxLayout, QWidget)

class Ui_SchedulerJobsTable(object):
    def setupUi(self, SchedulerJobsTable):
        if not SchedulerJobsTable.objectName():
            SchedulerJobsTable.setObjectName(u"SchedulerJobsTable")
        SchedulerJobsTable.resize(438, 109)
        self.verticalLayout = QVBoxLayout(SchedulerJobsTable)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(3, 3, 3, 3)
        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.pushButton_AddJob = QPushButton(SchedulerJobsTable)
        self.pushButton_AddJob.setObjectName(u"pushButton_AddJob")

        self.horizontalLayout_9.addWidget(self.pushButton_AddJob)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_3)


        self.verticalLayout.addLayout(self.horizontalLayout_9)

        self.tableView = QTableView(SchedulerJobsTable)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.verticalLayout.addWidget(self.tableView)


        self.retranslateUi(SchedulerJobsTable)

        QMetaObject.connectSlotsByName(SchedulerJobsTable)
    # setupUi

    def retranslateUi(self, SchedulerJobsTable):
        SchedulerJobsTable.setWindowTitle(QCoreApplication.translate("SchedulerJobsTable", u"Form", None))
        self.pushButton_AddJob.setText(QCoreApplication.translate("SchedulerJobsTable", u"\u65b0\u5efa", None))
    # retranslateUi

