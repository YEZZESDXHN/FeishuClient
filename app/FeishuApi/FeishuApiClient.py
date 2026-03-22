import json

import lark_oapi as lark
from lark_oapi.api.application.v6 import *
from lark_oapi.api.im.v1 import *


class FeishuApiClient:
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.client = None
        self.ws_client = None
        self.ws_client_event_handler = None

    def create_lark_client(self):
        client = lark.Client.builder() \
            .app_id(self.app_id) \
            .app_secret(self.app_secret) \
            .log_level(lark.LogLevel.ERROR) \
            .timeout(5) \
            .build()
        return client

    def create_lark_ws_client(self):
        client = lark.ws.Client(
            self.app_id,
            self.app_secret,
            event_handler=self.ws_client_event_handler,
            log_level=lark.LogLevel.DEBUG,
        )
        return client

    def do_p2_im_message_receive_v1(self, data: P2ImMessageReceiveV1):
        pass

    def do_p2_application_bot_menu_v6(self, data: P2ApplicationBotMenuV6):
        print(f'[ do_p2_application_bot_menu_v6 access ], data: {lark.JSON.marshal(data, indent=4)}')


class MyFeishuApiClient(FeishuApiClient):
    def __init__(self, app_id, app_secret):
        super().__init__(app_id, app_secret)

    def do_p2_im_message_receive_v1(self, data: P2ImMessageReceiveV1):
        if data.event.message.message_type == "text":
            res_content = json.loads(data.event.message.content)["text"]
        else:
            res_content = "解析消息失败，请发送文本消息\nparse message failed, please send text message"

        content = json.dumps(
            {
                "text": "收到你发送的消息："
                        + res_content
                        + "\nReceived message:"
                        + res_content
            }
        )

        if data.event.message.chat_type == "p2p":
            request = (
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
            response = self.client.im.v1.message.create(request)

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
            response: ReplyMessageResponse = self.client.im.v1.message.reply(request)
            if not response.success():
                raise Exception(
                    f"client.im.v1.message.reply failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
                )


def main():
    feishu_client = MyFeishuApiClient(app_id='cli_a937821c0a789ccf', app_secret='s9Jsldxb0PH7MuNDgU33OfFD1eb5v8Gf')
    feishu_client.client = feishu_client.create_lark_client()

    feishu_client.ws_client_event_handler = (
        lark.EventDispatcherHandler.builder("", "")
        .register_p2_im_message_receive_v1(feishu_client.do_p2_im_message_receive_v1)
        .register_p2_application_bot_menu_v6(feishu_client.do_p2_application_bot_menu_v6)
        .build()
    )
    feishu_client.ws_client = feishu_client.create_lark_ws_client()
    feishu_client.ws_client.start()


if __name__ == "__main__":
    main()
