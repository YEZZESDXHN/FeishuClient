import json

from lark_oapi.api.im.v1 import *
import lark_oapi as lark


class FeishuMessageApi:
    def __init__(self, feishu_api_client):
        self._feishu_api_client = feishu_api_client

    def send_message(self, receive_id_type: str, receive_id: str, msg_type: str, content: dict, uuid: str = ''):
        if not self._feishu_api_client.client:
            lark.logger.error(f"Client未初始化")
            return
        content_json = json.dumps(content, ensure_ascii=False)
        request: CreateMessageRequest = CreateMessageRequest.builder() \
            .receive_id_type(receive_id_type) \
            .request_body(CreateMessageRequestBody.builder()
                          .receive_id(receive_id)
                          .msg_type(msg_type)
                          .content(content_json)
                          .uuid(uuid)
                          .build()) \
            .build()
        response: CreateMessageResponse = self._feishu_api_client.client.im.v1.message.create(request)

        # 处理失败返回
        if not response.success():
            lark.logger.error(
                f"client.im.v1.message.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return

    def send_reply_message(self, message_id: str, msg_type: str, content: dict, reply_in_thread: bool = True,
                           uuid: str = ''):
        if not self._feishu_api_client.client:
            lark.logger.error(f"Client未初始化")
            return
        content_json = json.dumps(content, ensure_ascii=False)
        request: ReplyMessageRequest = (
            ReplyMessageRequest.builder()
            .message_id(message_id)
            .request_body(
                ReplyMessageRequestBody.builder()
                .content(content_json)
                .reply_in_thread(reply_in_thread)
                .msg_type(msg_type)
                .uuid(uuid)
                .build()
            )
            .build()
        )

        response: ReplyMessageResponse = self._feishu_api_client.client.im.v1.message.reply(request)
        if not response.success():
            lark.logger.error(
                f"client.im.v1.message.reply failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return

