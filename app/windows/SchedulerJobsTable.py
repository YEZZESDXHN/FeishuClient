import uuid

from PySide6.QtGui import QStandardItemModel, QStandardItem, Qt
from PySide6.QtWidgets import QWidget, QDialog, QMessageBox, QMenu

from app.DBManager import DBManager
from app.ui.SchedulerEdit import Ui_SchedulerEdit
from app.ui.SchedulerTable import Ui_SchedulerJobsTable

class JobEditDialog(Ui_SchedulerEdit, QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setupUi(self)
        self.data = {}
        if data:
            # 如果有数据传入，说明是编辑模式，设置输入框初始值
            if 'job_id' in data and data['job_id']:
                self.lineEdit_JobID.setText(data['job_id'])
                self.lineEdit_JobID.setEnabled(False)
            if 'job_name' in data and data['job_name']:
                self.comboBox_JobName.setCurrentText(data['job_name'])
                self.comboBox_JobName.setEnabled(False)
            self.comboBox_JobType.setCurrentText(data['job_type'])
            self.lineEdit_JobParam.setText(data['job_param'])
        else:
            self.lineEdit_JobID.setVisible(False)
            self.label.setVisible(False)


    def accept(self):
        if not self.lineEdit_JobParam.text():
            QMessageBox.warning(self, "提示", "参数不能为空")
            return
        self.data['job_id'] = self.lineEdit_JobID.text()
        self.data['job_name'] = self.comboBox_JobName.currentText()
        self.data['job_type'] = self.comboBox_JobType.currentText()
        self.data['job_param'] = self.lineEdit_JobParam.text()
        super().accept()

class SchedulerJobsTable(Ui_SchedulerJobsTable, QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.parent_window = self.window()
        self.db_manager: DBManager = self.parent_window.db_manager
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["任务名称", "类型", "运行参数", "Job ID"])
        self.tableView.setModel(self.model)
        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self.show_context_menu)
        self.refresh_table()

    def show_context_menu(self, pos):
        menu = QMenu(self)
        add_action = menu.addAction("新增任务")
        edit_action = menu.addAction("编辑任务")
        del_action = menu.addAction("删除任务")
        index = self.tableView.indexAt(pos)
        if not index.isValid():
            edit_action.setEnabled(False)
            del_action.setEnabled(False)

        action = menu.exec(self.tableView.mapToGlobal(pos))

        if action == add_action:
            self.handle_add()
        elif action == edit_action:
            self.handle_edit(index.row())
        elif action == del_action:
            self.handle_delete(index.row())

    def refresh_table(self):
        """从数据库读取并刷新 UI 列表"""
        self.model.setRowCount(0)
        jobs = self.db_manager.scheduler_db.get_all_jobs()
        for job in jobs:
            items = [
                QStandardItem(str(job['job_name'])),
                QStandardItem(str(job['job_type'])),
                QStandardItem(str(job['job_param'])),
                QStandardItem(str(job['job_id']))  # ID 通常隐藏或放在最后
            ]
            self.model.appendRow(items)

    def handle_edit(self, row):
        job_id = self.model.item(row, 3).text()
        job_data = self.db_manager.scheduler_db.get_job_by_id(job_id)
        edit_dialog = JobEditDialog(parent=self, data=job_data)
        if edit_dialog.exec() == QDialog.Accepted:
            try:
                job_type = edit_dialog.data['job_type']
                job_param = edit_dialog.data['job_param']

                self.parent_window.reschedule_job(job_id, job_type, job_param)

                self.db_manager.scheduler_db.update_job_param(
                    job_id, job_param
                )
                self.refresh_table()
            except Exception as e:
                print(e)

    def handle_delete(self, row):
        job_id = self.model.item(row, 3).text()
        self.parent_window.remove_job(job_id)
        self.db_manager.scheduler_db.delete_job_by_job_id(job_id)
        self.refresh_table()

    def handle_add(self):
        edit_dialog = JobEditDialog(parent=self)
        if edit_dialog.exec() == QDialog.Accepted:
            try:
                job_name = edit_dialog.data['job_name']
                job_type = edit_dialog.data['job_type']
                job_param = edit_dialog.data['job_param']
                job_id = str(uuid.uuid4())[:8]

                self.parent_window.add_job(job_id, job_name, job_type, job_param)

                self.db_manager.scheduler_db.add_job_record(
                    job_id, job_name, job_type, job_param
                )
                self.refresh_table()
            except Exception as e:
                print(e)



