import json
import logging
from typing import Optional
from pathlib import Path
import urllib3
from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import QMainWindow

from app.DBManager.DBManager import DBManager
from lark_oapi.api.im.v1 import P2ImMessageReceiveV1, CreateMessageRequest, CreateMessageRequestBody, \
    CreateMessageResponse, ReplyMessageRequest, ReplyMessageRequestBody, ReplyMessageResponse

from app.CodebeamerClient.CodebeamerClient import CodebeamerClient
# from app.FeishuApi.CustomEventDispatcherHandler import EventDispatcherHandler
from lark_oapi import EventDispatcherHandler
from app.FeishuApi.FeishuApiClient import FeishuApiClient
from app.FeishuApi.FeishuWsClient import WsClient
from app.ui.MainWindow import Ui_MainWindow
from app.user_data import CodeBeamerDefect

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger('FeishuClient.' + __name__)


class QWsClient(QObject, WsClient):
    def __init__(self, app_id, app_secret, feishu_client):
        super().__init__(app_id=app_id, app_secret=app_secret, feishu_client=feishu_client)

    def ws_client_event_handler_init(self):
        self.ws_client_event_handler = (
            EventDispatcherHandler.builder("", "")
            .register_p2_im_message_receive_v1(self.do_p2_im_message_receive_v1)
            .build()
        )

    def do_p2_im_message_receive_v1(self, data: P2ImMessageReceiveV1):
        if data.event.message.message_type == "text":
            res_content = json.loads(data.event.message.content)["text"]
        else:
            res_content = "解析消息失败，请发送文本消息\nparse message failed, please send text message"

        content = json.dumps(
            {
                "text": "收到你发送的消息："
                        + res_content
            }
        )

        if data.event.message.chat_type == "p2p":
            request: CreateMessageRequest = (
                CreateMessageRequest.builder()
                .receive_id_type("chat_id")
                .request_body(
                    CreateMessageRequestBody.builder()
                    .receive_id(data.event.message.chat_id)
                    .msg_type("text")
                    .content(content)
                    .build()
                )
                .build()
            )
            # 使用OpenAPI发送消息
            # Use send OpenAPI to send messages
            # https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/create
            response: CreateMessageResponse = self.feishu_client.client.im.v1.message.create(request)
            print('self.client.im.v1.message.create(request)')

            if not response.success():
                raise Exception(
                    f"client.im.v1.message.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
                )
        else:
            request: ReplyMessageRequest = (
                ReplyMessageRequest.builder()
                .message_id(data.event.message.message_id)
                .request_body(
                    ReplyMessageRequestBody.builder()
                    .content(content)
                    .msg_type("text")
                    .build()
                )
                .build()
            )
            # 使用OpenAPI回复消息
            # Reply to messages using send OpenAPI
            # https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/reply
            response: ReplyMessageResponse = self.feishu_client.client.im.v1.message.reply(request)
            if not response.success():
                raise Exception(
                    f"client.im.v1.message.reply failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
                )


class QFeishuApiClient(QObject, FeishuApiClient):
    signal_data_tables = Signal(object)
    def __init__(self, app_id, app_secret):
        super().__init__(app_id=app_id, app_secret=app_secret)

    def get_data_tables(self, app_token):
        data_tables = self.bitable_api.get_data_tables(app_token)
        self.signal_data_tables.emit(data_tables)


class QCodebeamerClient(QObject, CodebeamerClient):
    def __init__(self, username, password):
        super().__init__(username=username, password=password)


class QRunner(QObject):
    def __init__(self, parent: "MainWindow"):
        super().__init__()
        self.parent = parent
        self.code_beamer_defect_field_map = {
            'ID': 'defect_id',
            'Status': 'status',
            'Summary': 'summary',
            'Assigned To': 'assigned_to',
            'modified_at_unix': 'modified_at',
            'Modified by': 'modified_by',
            'Fixed in Release': 'fixed_in_release',
            'Reported in Release': 'reported_in_release',
            'Team': 'team',
            'Owner': 'owner',
            'Submitted by': 'submitted_by',
            'submitted_at_unix': 'submitted_at',
            'Frequency': 'frequency',
            'Severity': 'severity'
        }

    def code_beamer_defects_conversion_feishu_items(self, defects: list[CodeBeamerDefect]):
        feishu_items = []
        for defect in defects:
            feishu_item = {}
            for key, value in self.code_beamer_defect_field_map.items():
                if key == 'ID':
                    _id = getattr(defect, value, '')
                    feishu_item[key] = {
                        "text": str(_id),
                        "link": f"https://cb.alm.vnet.valeo.com/cb/issue/{_id}"
                    }

                else:
                    feishu_item[key] = getattr(defect, value, '')
            feishu_items.append(feishu_item)
        return feishu_items



    def sync_code_beamer_defect_to_feishu(self):
        code_beamer_client = self.parent.cb_client
        feishu_client = self.parent.feishu_client
        if not feishu_client.client:
            feishu_client.client_init()
        if code_beamer_client.client._authenticated or code_beamer_client.client.authenticate():
            project_id = 873
            tracker_id = code_beamer_client.get_tracker_id_by_name('Defect', project_id)
            items = code_beamer_client.get_all_items_by_query(tracker_id=tracker_id, filter_active=False)
            defs = code_beamer_client.convert_defect_items(items)
            result = self.parent.db_manager.defects_db.batch_upsert_defects(defs)
            print(result)
            table_index = self.parent.comboBox_BitableDateTable.currentIndex()
            table_id = self.parent.feishu_bitable_tables[table_index]['table_id']
            app_token = self.parent.feishu_bitable_app_token
            feishu_items = feishu_client.bitable_api.get_records(
                app_token=app_token,
                table_id=table_id,
                field_names=['Status']
            )
            record_ids = []
            for feishu_item in feishu_items:
                record_ids.append(feishu_item.record_id)

            feishu_client.bitable_api.delete_records(
                app_token=app_token,
                table_id=table_id,
                records=record_ids
            )

            records = self.code_beamer_defects_conversion_feishu_items(defs)
            feishu_client.bitable_api.add_records(
                app_token=app_token,
                table_id=table_id,
                records=records)
            print('ok')




class MainWindow(QMainWindow, Ui_MainWindow):
    """
    自定义的主窗口类，继承了 QMainWindow（Qt主窗口行为）
    """
    signal_update_data_tables = Signal(str)
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.db_path = 'Database/database.db'
        self.db_manager: Optional[DBManager] = None
        self.init_database(self.db_path)
        self.cb_username: str = ''
        self.cb_password: str = '.'

        self.feishu_app_id: str = ''
        self.feishu_secret: str = ''
        self.feishu_bitable_url: str = ''
        self.feishu_bitable_tables: list[dict] = []  # [{table_id: table_name}]
        self.feishu_bitable_app_token: str = ''

        self.feishu_client: Optional[QFeishuApiClient] = None
        self._feishu_client_init()

        self.feishu_ws_client: Optional[QWsClient] = None
        self._feishu_ws_client_init()

        self.cb_client: Optional[QCodebeamerClient] = None
        self._codebeamer_init()
        self._runner_init()
        self.signal_connect()
        self.init_ui()

    def init_ui(self):
        config = self.db_manager.info_db.get_config()
        if config:
            try:
                self.cb_username = config['cb_username']
                self.cb_password = config['cb_password']
                self.feishu_app_id = config['feishu_app_id']
                self.feishu_secret = config['feishu_secret']
                self.feishu_bitable_url = config['feishu_bitable_url']
                self.feishu_client.app_id = self.feishu_app_id
                self.feishu_client.app_secret = self.feishu_secret
                self.feishu_ws_client.app_id = self.feishu_app_id
                self.feishu_ws_client.app_secret = self.feishu_secret
                self.cb_client.update_password(self.cb_password)
                self.cb_client.update_username(self.cb_username)

                self.lineEdit_Username.setText(self.cb_username)
                self.lineEdit_Password.setText(self.cb_password)
                self.lineEdit_AppID.setText(self.feishu_app_id)
                self.lineEdit_AppSecret.setText(self.feishu_secret)
                self.lineEdit_BitableUrl.setText(self.feishu_bitable_url)
            except Exception as e:
                pass

    def init_database(self, db):
        db_path = Path(db)  # 转换为 Path 对象（方便处理路径）
        db_dir = db_path.parent  # 获取数据库文件所在的文件夹路径

        # 如果文件夹不存在，创建文件夹
        if not db_dir.exists():
            try:
                db_dir.mkdir(parents=True, exist_ok=True)  # parents=True：创建多级目录；exist_ok=True：已存在则不报错
                logger.info(f"数据库文件夹不存在，已自动创建：{db_dir}")
            except Exception as e:
                logger.exception(f"创建数据库文件夹失败：{str(e)}")
        self.db_manager = DBManager(db)

    def _runner_init(self):
        self.runner_thread = QThread()
        self.runner = QRunner(self)
        self.runner.moveToThread(self.runner_thread)
        self.runner_thread.start()

    def _codebeamer_init(self):
        self.cb_client_thread = QThread()
        self.cb_client = QCodebeamerClient(self.cb_username, self.cb_password)
        self.cb_client.moveToThread(self.cb_client_thread)
        self.cb_client_thread.start()

    def _feishu_client_init(self):
        self.feishu_client_thread = QThread()
        self.feishu_client = QFeishuApiClient(self.feishu_app_id, self.feishu_secret)
        self.feishu_client.moveToThread(self.feishu_client_thread)
        self.feishu_client_thread.start()

    def _feishu_ws_client_init(self):
        self.feishu_ws_client_thread = QThread()
        self.feishu_ws_client = QWsClient(self.feishu_app_id, self.feishu_secret, self.feishu_client)
        self.feishu_ws_client.moveToThread(self.feishu_ws_client_thread)
        self.feishu_ws_client_thread.start()

    def signal_connect(self):
        self.lineEdit_Username.editingFinished.connect(self.update_cb_username)
        self.lineEdit_Password.editingFinished.connect(self.update_cb_password)
        self.lineEdit_AppID.editingFinished.connect(self.update_feishu_app_id)
        self.lineEdit_AppSecret.editingFinished.connect(self.update_feishu_secret)
        self.lineEdit_BitableUrl.editingFinished.connect(self.update_feishu_bitable_url)
        self.pushButton_CBTest.clicked.connect(self.runner.sync_code_beamer_defect_to_feishu)
        self.pushButton_FeishuTest.clicked.connect(self.feishu_client.client_init)
        self.feishu_client.signal_data_tables.connect(self.update_feishu_bitable_tables)
        self.signal_update_data_tables.connect(self.feishu_client.get_data_tables)
        self.pushButton_RefreshDataTable.clicked.connect(self.update_feishu_bitable_url)

    def update_cb_username(self):
        self.cb_username = self.lineEdit_Username.text()
        self.cb_client.update_username(self.cb_username)
        self.db_manager.info_db.update_single_field(field_name='cb_username', value=self.cb_username)

    def update_cb_password(self):
        self.cb_password = self.lineEdit_Password.text()
        self.cb_client.update_password(self.cb_password)
        self.db_manager.info_db.update_single_field(field_name='cb_password', value=self.cb_password)

    def update_feishu_app_id(self):
        self.feishu_app_id = self.lineEdit_AppID.text()
        self.feishu_client.app_id = self.feishu_app_id
        self.feishu_ws_client.app_id = self.feishu_app_id
        self.db_manager.info_db.update_single_field(field_name='feishu_app_id', value=self.feishu_app_id)

    def update_feishu_secret(self):
        self.feishu_secret = self.lineEdit_AppSecret.text()
        self.feishu_client.app_secret = self.feishu_secret
        self.feishu_ws_client.app_secret = self.feishu_secret
        self.db_manager.info_db.update_single_field(field_name='feishu_secret', value=self.feishu_secret)

    def update_feishu_bitable_url(self):
        self.feishu_bitable_url = self.lineEdit_BitableUrl.text()
        self.feishu_bitable_app_token = self.feishu_client.bitable_api.get_feishu_app_token(self.feishu_bitable_url)
        self.signal_update_data_tables.emit(self.feishu_bitable_app_token)
        self.db_manager.info_db.update_single_field(field_name='feishu_bitable_url', value=self.feishu_bitable_url)


    def update_feishu_bitable_tables(self, tables: list):
        self.feishu_bitable_tables.clear()
        name_list = []
        for table in tables:
            self.feishu_bitable_tables.append({'table_id': table.table_id, "name": table.name})
            name_list.append(table.name)
        self.comboBox_BitableDateTable.blockSignals(True)
        self.comboBox_BitableDateTable.clear()
        self.comboBox_BitableDateTable.addItems(name_list)
        self.comboBox_BitableDateTable.blockSignals(False)

    def closeEvent(self, event) -> None:
        """重写关闭事件，优雅退出线程"""
        if self.runner_thread:
            self.runner_thread.quit()
            if self.runner_thread.wait(3000):  # 等待3秒超时
                logger.info("runner_thread线程已正常停止")
            else:
                logger.warning("runner_thread线程强制退出")

        if self.cb_client_thread:
            self.cb_client_thread.quit()
            if self.cb_client_thread.wait(3000):  # 等待3秒超时
                logger.info("cb_client_thread线程已正常停止")
            else:
                logger.warning("cb_client_thread线程强制退出")

        if self.feishu_client_thread:
            self.feishu_client_thread.quit()
            if self.feishu_client_thread.wait(3000):  # 等待3秒超时
                logger.info("feishu_client_thread线程已正常停止")
            else:
                logger.warning("feishu_client_thread线程强制退出")

        if self.feishu_ws_client_thread:
            self.feishu_ws_client_thread.quit()
            if self.feishu_ws_client_thread.wait(3000):  # 等待3秒超时
                logger.info("feishu_ws_client_thread线程已正常停止")
            else:
                logger.warning("feishu_ws_client_thread线程强制退出")
