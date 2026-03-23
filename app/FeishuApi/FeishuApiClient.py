import json

import lark_oapi as lark
from lark_oapi.api.application.v6 import *
from lark_oapi.api.im.v1 import *

from app.FeishuApi.FeishuBitableApi import FeishuBitableApi
from app.FeishuApi.FeishuMessageApi import FeishuMessageApi
# from app.FeishuApi.FeishuWsClient import WsClient


class FeishuApiClient:
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.client: Optional[lark.client.Client] = None
        self.message_api = FeishuMessageApi(self)
        self.bitable_api = FeishuBitableApi(self)

    def send_message(self, receive_id_type: str, receive_id: str, msg_type: str, content: dict, uuid: str = ''):
        return self.message_api.send_message(receive_id_type, receive_id, msg_type, content, uuid)

    def send_reply_message(self, message_id: str, msg_type: str, content: dict, reply_in_thread: bool = True,
                           uuid: str = ''):
        return self.message_api.send_reply_message(message_id, msg_type, content, reply_in_thread, uuid)

    def client_init(self):
        client = lark.Client.builder() \
            .app_id(self.app_id) \
            .app_secret(self.app_secret) \
            .log_level(lark.LogLevel.ERROR) \
            .timeout(5) \
            .build()
        self.client = client
