from typing import Optional

from lark_oapi import LogLevel
from lark_oapi.api.application.v6 import P2ApplicationBotMenuV6
from lark_oapi.api.im.v1 import P2ImMessageReceiveV1
from lark_oapi.ws import Client

from app.FeishuApi.FeishuApiClient import FeishuApiClient


class WsClient:
    def __init__(self, app_id, app_secret, feishu_client: FeishuApiClient):

        self.feishu_client = feishu_client
        self.app_id = app_id
        self.app_secret = app_secret
        self.ws_client: Optional[Client] = None
        self.ws_client_event_handler = None

    def ws_client_init(self):
        self.ws_client_event_handler_init()
        client = Client(
            self.app_id,
            self.app_secret,
            event_handler=self.ws_client_event_handler,
            log_level=LogLevel.DEBUG,
        )
        self.ws_client = client

    def ws_client_start(self):
        self.ws_client_init()
        self.ws_client.start()

    def ws_client_event_handler_init(self):
        # self.ws_client_event_handler = (
        #     lark.EventDispatcherHandler.builder("", "")
        #     .register_p2_im_message_receive_v1(self.do_p2_im_message_receive_v1)
        #     .register_p2_application_bot_menu_v6(self.do_p2_application_bot_menu_v6)
        #     .build()
        # )
        raise NotImplementedError("ws_client_event_handler_init方法尚未实现，请在子类或当前类中完成逻辑")

    def do_p2_im_message_receive_v1(self, data: P2ImMessageReceiveV1):
        raise NotImplementedError("do_p2_im_message_receive_v1方法尚未实现，请在子类或当前类中完成逻辑")

    def do_p2_application_bot_menu_v6(self, data: P2ApplicationBotMenuV6):
        raise NotImplementedError("do_p2_application_bot_menu_v6方法尚未实现，请在子类或当前类中完成逻辑")