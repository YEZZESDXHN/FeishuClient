import json
import sys

from PySide6.QtWidgets import QApplication
from app.windows.MainWindow import MainWindow
# from lark_oapi.api.im.v1 import *
#
# from app.FeishuApi.FeishuApiClient import FeishuApiClient
# from app.FeishuApi.FeishuWsClient import WsClient
# import lark_oapi as lark
#
#
# class MyWsClient(WsClient):
#     def __init__(self, app_id, app_secret, feishu_client):
#         super().__init__(app_id, app_secret, feishu_client)
#
#     def ws_client_event_handler_init(self):
#         self.ws_client_event_handler = (
#             lark.EventDispatcherHandler.builder("", "")
#             .register_p2_im_message_receive_v1(self.do_p2_im_message_receive_v1)
#             .build()
#         )
#
#     def do_p2_im_message_receive_v1(self, data: P2ImMessageReceiveV1):
#         if data.event.message.message_type == "text":
#             res_content = json.loads(data.event.message.content)["text"]
#         else:
#             res_content = "解析消息失败，请发送文本消息\nparse message failed, please send text message"
#
#         content = json.dumps(
#             {
#                 "text": "收到你发送的消息："
#                         + res_content
#             }
#         )
#
#         if data.event.message.chat_type == "p2p":
#             request: CreateMessageRequest = (
#                 CreateMessageRequest.builder()
#                 .receive_id_type("chat_id")
#                 .request_body(
#                     CreateMessageRequestBody.builder()
#                     .receive_id(data.event.message.chat_id)
#                     .msg_type("text")
#                     .content(content)
#                     .build()
#                 )
#                 .build()
#             )
#             # 使用OpenAPI发送消息
#             # Use send OpenAPI to send messages
#             # https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/create
#             response: CreateMessageResponse = self.feishu_client.client.im.v1.message.create(request)
#             print('self.client.im.v1.message.create(request)')
#
#             if not response.success():
#                 raise Exception(
#                     f"client.im.v1.message.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
#                 )
#         else:
#             request: ReplyMessageRequest = (
#                 ReplyMessageRequest.builder()
#                 .message_id(data.event.message.message_id)
#                 .request_body(
#                     ReplyMessageRequestBody.builder()
#                     .content(content)
#                     .msg_type("text")
#                     .build()
#                 )
#                 .build()
#             )
#             # 使用OpenAPI回复消息
#             # Reply to messages using send OpenAPI
#             # https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/reply
#             response: ReplyMessageResponse = self.feishu_client.client.im.v1.message.reply(request)
#             if not response.success():
#                 raise Exception(
#                     f"client.im.v1.message.reply failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
#                 )
#
#
# def main():
#     feishu_client = FeishuApiClient(app_id='', app_secret='')
#     feishu_client.client_init()
#
#     # feishu_ws_client = MyWsClient(app_id='',
#     #                               app_secret='',
#     #                               feishu_client=feishu_client)
#     #
#     # feishu_ws_client.ws_client_init()
#     # feishu_ws_client.ws_client_start()
#     tables = feishu_client.bitable_api.get_data_tables('')
#     print(tables)


if __name__ == "__main__":
    # main()
    app = QApplication(sys.argv)
    app.setStyle("WindowsVista")
    # app.setStyle("Fusion")
    w = MainWindow()
    # version = 'v0.1.9'
    # w.custom_status_bar.label_Version.setText(version)
    w.show()
    sys.exit(app.exec())