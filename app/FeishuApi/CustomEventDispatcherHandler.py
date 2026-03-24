from lark_oapi.core.http.handler import HttpHandler
from lark_oapi.api.application.v6.processor import *
from lark_oapi.api.im.v1.processor import *
from lark_oapi.event.context import EventContext
from lark_oapi.event.processor import ICallBackProcessor, IEventProcessor
from lark_oapi.core import *
from lark_oapi.core.exception import *


class EventDispatcherHandler(HttpHandler):

    def __init__(self) -> None:
        self._processorMap: Dict[str, IEventProcessor] = {}
        self._callback_processor_map: Dict[str, ICallBackProcessor] = {}
        self._encrypt_key: Optional[str] = None
        self._verification_token: Optional[str] = None

    def do(self, req: RawRequest) -> RawResponse:
        logger.debug(f"event access, uri: {req.uri}, "
                     f"headers: {JSON.marshal(req.headers)}, "
                     f"body: {str(req.body, UTF_8) if req.body is not None else None}")

        resp = RawResponse()
        resp.status_code = 200
        resp.set_content_type(f"{APPLICATION_JSON}; charset=utf-8")

        try:
            if req.body is None:
                raise InvalidArgsException("request body is null")

            # 消息解密
            plaintext = self._decrypt(req.body)

            # 上下文结构化
            context = JSON.unmarshal(plaintext, EventContext)
            if Strings.is_not_empty(context.schema):
                # 解析 v2 事件
                context.schema = "p2"
                context.type = context.header.event_type
                context.token = context.header.token
            elif Strings.is_not_empty(context.uuid):
                # 解析 v1 事件
                context.schema = "p1"
                context.type = context.event.get("type")

            # 校验 token
            if context.token is not None and self._verification_token != context.token:
                raise AccessDeniedException("invalid verification_token")

            if URL_VERIFICATION == context.type:
                # 验证回调地址事件, 直接返回 Challenge Code
                resp_body = "{\"challenge\":\"%s\"}" % context.challenge
                resp.content = resp_body.encode(UTF_8)
                return resp
            else:
                # 否则验签
                self._verify_sign(req)

            event_key = f"{context.schema}.{context.type}"
            if event_key in self._callback_processor_map:
                processor: ICallBackProcessor = self._callback_processor_map.get(event_key)
                if processor is None:
                    raise EventException(f"callback processor not found, type: {context.type}")

                # 消息反序列化
                data = JSON.unmarshal(plaintext, processor.type())
                result = processor.do(data)

                # 返回成功
                resp.content = JSON.marshal(result).encode(UTF_8)
            else:
                processor: IEventProcessor = self._processorMap.get(event_key)
                if processor is None:
                    raise EventException(f"processor not found, type: {context.type}")

                # 消息反序列化
                data = JSON.unmarshal(plaintext, processor.type())
                processor.do(data)

                # 返回成功
                resp.content = "{\"msg\":\"success\"}".encode(UTF_8)
            return resp

        except Exception as e:
            logger.exception(
                f"handle event failed, uri: {req.uri}, request_id: {req.headers.get(X_REQUEST_ID)}, err: {e}")
            resp.status_code = 500
            resp_body = "{\"msg\":\"%s\"}" % str(e)
            resp.content = resp_body.encode(UTF_8)

            return resp

    def do_without_validation(self, payload: bytes) -> Any:
        pl = payload.decode(UTF_8)
        context = JSON.unmarshal(pl, EventContext)
        if Strings.is_not_empty(context.schema):
            # 解析 v2 事件
            context.schema = "p2"
            context.type = context.header.event_type
            context.token = context.header.token
        elif Strings.is_not_empty(context.uuid):
            # 解析 v1 事件
            context.schema = "p1"
            context.type = context.event.get("type")

        event_key = f"{context.schema}.{context.type}"
        if event_key in self._callback_processor_map:
            processor: ICallBackProcessor = self._callback_processor_map.get(event_key)
            if processor is None:
                raise EventException(f"callback processor not found, type: {context.type}")

            # 消息反序列化
            data = JSON.unmarshal(pl, processor.type())
            result = processor.do(data)

            # 返回成功
            return result
        else:
            processor: IEventProcessor = self._processorMap.get(f"{context.schema}.{context.type}")
            if processor is None:
                raise EventException(f"processor not found, type: {context.type}")

            # 消息反序列化
            data = JSON.unmarshal(pl, processor.type())
            processor.do(data)

    def _decrypt(self, content: bytes) -> str:
        plaintext: str
        encrypt = json.loads(content).get("encrypt")
        if Strings.is_not_empty(encrypt):
            if Strings.is_empty(self._encrypt_key):
                raise NoAuthorizationException("encrypt_key not found")
            plaintext = AESCipher(self._encrypt_key).decrypt_str(encrypt)
        else:
            plaintext = str(content, UTF_8)

        return plaintext

    def _verify_sign(self, request: RawRequest) -> None:
        if self._encrypt_key is None or self._encrypt_key == "":
            return
        timestamp = request.headers.get(LARK_REQUEST_TIMESTAMP)
        nonce = request.headers.get(LARK_REQUEST_NONCE)
        signature = request.headers.get(LARK_REQUEST_SIGNATURE)
        bs = (timestamp + nonce + self._encrypt_key).encode(UTF_8) + request.body
        h = hashlib.sha256(bs)
        if signature != h.hexdigest():
            raise AccessDeniedException("signature verification failed")

    @staticmethod
    def builder(encrypt_key: str, verification_token: str, level: LogLevel = None) -> "EventDispatcherHandlerBuilder":
        if level is not None:
            logger.setLevel(int(level.value))
        return EventDispatcherHandlerBuilder(encrypt_key, verification_token)


class EventDispatcherHandlerBuilder(object):
    def __init__(self, encrypt_key: str, verification_token: str) -> None:
        self._encrypt_key = encrypt_key
        self._verification_token = verification_token
        self._processorMap = {}
        self._callback_processor_map = {}

    def register_p2_im_message_receive_v1(self,
                                          f: Callable[[P2ImMessageReceiveV1], None]) -> "EventDispatcherHandlerBuilder":
        if "p2.im.message.receive_v1" in self._processorMap:
            raise EventException("processor already registered, type: p2.im.message.receive_v1")
        self._processorMap["p2.im.message.receive_v1"] = P2ImMessageReceiveV1Processor(f)
        return self

    def register_p2_application_bot_menu_v6(self, f: Callable[
        [P2ApplicationBotMenuV6], None]) -> "EventDispatcherHandlerBuilder":
        if "p2.application.bot.menu_v6" in self._processorMap:
            raise EventException("processor already registered, type: p2.application.bot.menu_v6")
        self._processorMap["p2.application.bot.menu_v6"] = P2ApplicationBotMenuV6Processor(f)
        return self

    def build(self) -> EventDispatcherHandler:
        event_dispatcher_handler = EventDispatcherHandler()
        event_dispatcher_handler._encrypt_key = self._encrypt_key
        event_dispatcher_handler._verification_token = self._verification_token
        event_dispatcher_handler._processorMap = self._processorMap
        event_dispatcher_handler._callback_processor_map = self._callback_processor_map
        return event_dispatcher_handler