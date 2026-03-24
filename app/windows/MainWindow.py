import json
from typing import Optional

import urllib3
from PySide6.QtCore import QObject, QThread
from PySide6.QtWidgets import QMainWindow
from lark_oapi import EventDispatcherHandler
from lark_oapi.api.im.v1 import P2ImMessageReceiveV1, CreateMessageRequest, CreateMessageRequestBody, \
    CreateMessageResponse, ReplyMessageRequest, ReplyMessageRequestBody, ReplyMessageResponse

from app.CodebeamerClient.CodebeamerClient import CodebeamerClient
from app.FeishuApi.FeishuApiClient import FeishuApiClient
from app.FeishuApi.FeishuWsClient import WsClient
from app.ui.MainWindow import Ui_MainWindow
from app.user_data import CodeBeamerDefect

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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
    def __init__(self, app_id, app_secret):
        super().__init__(app_id=app_id, app_secret=app_secret)


class QCodebeamerClient(QObject, CodebeamerClient):
    def __init__(self, username, password):
        super().__init__(username=username, password=password)


class QRunner(QObject):
    def __init__(self, parent: "MainWindow"):
        super().__init__()
        self.parent = parent

    def sync_code_beamer_defect_to_feishu(self):
        print('sync_code_beamer_defect_to_feishu')
        code_beamer_client = self.parent.cb_client
        feishu_client = self.parent.feishu_client
        feishu_client.client_init()
        # if code_beamer_client.client._authenticated or code_beamer_client.client.authenticate():
        #     project_id = 873
        #     tracker_id = code_beamer_client.get_tracker_id_by_name('Defect', project_id)
        #     items = code_beamer_client.get_all_items_by_query(tracker_id=tracker_id, filter_active=False)
        #     defs = code_beamer_client.convert_defect_items(items)
        #     print(defs[0].to_dict())
        #     records = []
        #     records.append(defs[0].to_dict())
        #     feishu_client.bitable_api.add_records(app_token=feishu_client.bitable_api.get_feishu_app_token(self.parent.feishu_bitable_url),
        #                                           table_id='tblxcPJsx592qrPX',
        #                                           records=records)

        records = []
        records.append(CodeBeamerDefect().to_dict())
        feishu_client.bitable_api.add_records(
            app_token=feishu_client.bitable_api.get_feishu_app_token(self.parent.feishu_bitable_url),
            table_id='tblxcPJsx592qrPX',
            records=records)






class MainWindow(QMainWindow, Ui_MainWindow):
    """
    自定义的主窗口类，继承了 QMainWindow（Qt主窗口行为）
    """

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.cb_username: str = ''
        self.cb_password: str = ''

        self.feishu_app_id: str = ''
        self.feishu_secret: str = ''
        self.feishu_bitable_url: str = ''
        self.feishu_bitable_tables: dict = {}  # {table_id: table_name}
        self.feishu_bitable_app_token: str = ''

        self.feishu_client: Optional[QFeishuApiClient] = None
        self._feishu_client_init()

        self.feishu_ws_client: Optional[QWsClient] = None
        self._feishu_ws_client_init()

        self.cb_client: Optional[QCodebeamerClient] = None
        self._codebeamer_init()
        self._runner_init()
        self.signal_connect()

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

    def update_cb_username(self):
        self.cb_username = self.lineEdit_Username.text()
        self.cb_client.update_username(self.cb_username)

    def update_cb_password(self):
        self.cb_password = self.lineEdit_Password.text()
        self.cb_client.update_password(self.cb_password)

    def update_feishu_app_id(self):
        self.feishu_app_id = self.lineEdit_AppID.text()
        self.feishu_client.app_id = self.feishu_app_id
        self.feishu_ws_client.app_id = self.feishu_app_id

    def update_feishu_secret(self):
        self.feishu_secret = self.lineEdit_AppSecret.text()
        self.feishu_client.app_secret = self.feishu_secret
        self.feishu_ws_client.app_secret = self.feishu_secret

    def update_feishu_bitable_url(self):
        self.feishu_bitable_url = self.lineEdit_BitableUrl.text()
        self.feishu_bitable_app_token = self.feishu_client.bitable_api.get_feishu_app_token(self.feishu_bitable_url)

