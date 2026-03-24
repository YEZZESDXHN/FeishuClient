import json
from enum import Enum, IntEnum
from typing import List
from urllib.parse import urlparse

from lark_oapi import logger
from lark_oapi.api.bitable.v1 import CreateAppRequest, ReqApp, CreateAppResponse, AppTable, ListAppTableRequest, \
    ListAppTableResponse, SearchAppTableRecordRequest, SearchAppTableRecordRequestBody, SearchAppTableRecordResponse, \
    BatchDeleteAppTableRecordRequest, BatchDeleteAppTableRecordRequestBody, BatchDeleteAppTableRecordResponse, \
    AppTableRecord, BatchCreateAppTableRecordRequest, BatchCreateAppTableRecordRequestBody, \
    BatchCreateAppTableRecordResponse


class UiType(str, Enum):
    # 基础文本与通讯
    TEXT = "Text"
    EMAIL = "Email"
    PHONE = "Phone"
    URL = "Url"

    # 数值与度量
    NUMBER = "Number"
    PROGRESS = "Progress"
    CURRENCY = "Currency"
    RATING = "Rating"

    # 选择与日期
    SINGLE_SELECT = "SingleSelect"
    MULTI_SELECT = "MultiSelect"
    DATETIME = "DateTime"
    CHECKBOX = "Checkbox"

    # 组织与协作
    USER = "User"
    GROUP_CHAT = "GroupChat"
    STAGE = "Stage"
    ATTACHMENT = "Attachment"

    # 关联与逻辑
    SINGLE_LINK = "SingleLink"
    DUPLEX_LINK = "DuplexLink"
    FORMULA = "Formula"
    LOOKUP = "Lookup"
    BARCODE = "Barcode"
    LOCATION = "Location"
    BUTTON = "Button"

    # 系统字段
    AUTO_NUMBER = "AutoNumber"
    CREATED_TIME = "CreatedTime"
    MODIFIED_TIME = "ModifiedTime"
    CREATED_USER = "CreatedUser"
    MODIFIED_USER = "ModifiedUser"

    def __str__(self):
        return self.value


class FieldType(IntEnum):
    # 基础类型
    TEXT = 1
    NUMBER = 2
    SINGLE_SELECT = 3
    MULTI_SELECT = 4
    DATE_TIME = 5
    CHECKBOX = 7
    USER = 11
    PHONE = 13
    URL = 15
    ATTACHMENT = 17
    SINGLE_LINK = 18
    LOOKUP = 19
    FORMULA = 20
    DUPLEX_LINK = 21
    LOCATION = 22
    GROUP_CHAT = 23
    STAGE = 24

    # 系统类型
    CREATED_TIME = 1001
    MODIFIED_TIME = 1002
    CREATED_USER = 1003
    MODIFIED_USER = 1004
    AUTO_NUMBER = 1005

    # 特殊扩展
    BUTTON = 3001


FIELD_TO_UI_MAP = {
    FieldType.TEXT: [UiType.TEXT, UiType.BARCODE, UiType.EMAIL],
    FieldType.NUMBER: [UiType.NUMBER, UiType.PROGRESS, UiType.CURRENCY, UiType.RATING],
    FieldType.SINGLE_SELECT: [UiType.SINGLE_SELECT],
    FieldType.MULTI_SELECT: [UiType.MULTI_SELECT],
    FieldType.DATE_TIME: [UiType.DATETIME],
    FieldType.CHECKBOX: [UiType.CHECKBOX],
    FieldType.USER: [UiType.USER],
    FieldType.PHONE: [UiType.PHONE],
    FieldType.URL: [UiType.URL],
    FieldType.ATTACHMENT: [UiType.ATTACHMENT],
    FieldType.SINGLE_LINK: [UiType.SINGLE_LINK],
    FieldType.LOOKUP: [UiType.LOOKUP],
    FieldType.FORMULA: [UiType.FORMULA],
    FieldType.DUPLEX_LINK: [UiType.DUPLEX_LINK],
    FieldType.LOCATION: [UiType.LOCATION],
    FieldType.GROUP_CHAT: [UiType.GROUP_CHAT],
    FieldType.STAGE: [UiType.STAGE],
    FieldType.CREATED_TIME: [UiType.CREATED_TIME],
    FieldType.MODIFIED_TIME: [UiType.MODIFIED_TIME],
    FieldType.CREATED_USER: [UiType.CREATED_USER],
    FieldType.MODIFIED_USER: [UiType.MODIFIED_USER],
    FieldType.AUTO_NUMBER: [UiType.AUTO_NUMBER],
    FieldType.BUTTON: [UiType.BUTTON],
}


class FeishuBitableApi:
    def __init__(self, feishu_api_client):
        self._feishu_api_client = feishu_api_client

    @staticmethod
    def _get_field_payload(field_name: str, ui_type: UiType):
        """
        根据 UI 类型自动推导出对应的 FieldType(数字) 并生成请求体
        """
        # 查找该 UiType 属于哪个 FieldType
        target_field_type = None
        for f_type, ui_list in FIELD_TO_UI_MAP.items():
            if ui_type in ui_list:
                target_field_type = f_type
                break

        payload = {
            "field_name": field_name,
            "type": int(target_field_type),
            "ui_type": ui_type
        }

        return payload

    def create_bitable_table(self, name: str, folder_token: str):
        """
        创建多维表格
        :return:
        """
        if not self._feishu_api_client.client:
            logger.error(f"Client未初始化")
            return
        request: CreateAppRequest = CreateAppRequest.builder() \
            .request_body(ReqApp.builder()
                          .name(name)
                          .folder_token(folder_token)
                          .build()) \
            .build()

        # 发起请求
        response: CreateAppResponse = self._feishu_api_client.client.bitable.v1.app.create(request)

        # 处理失败返回
        if not response.success():
            logger.error(
                f"client.bitable.v1.app.create failed, code: {response.code}, "
                f"msg: {response.msg}, log_id: {response.get_log_id()}, "
                f"resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return

    def create_data_table(self, name: str, default_view_name: str):
        """
        新增一个数据表
        :return:
        """
        pass

    def create_data_tables(self):
        """
        新增多个数据表
        :return:
        """
        pass

    @staticmethod
    def get_feishu_app_token(table_url: str) -> str:
        """
        解析飞书多维表格 URL，提取 app_token (base/ 之后，参数之前的部分)
        """
        try:
            # 1. 解析 URL 结构
            parsed_url = urlparse(table_url)

            # 2. 获取路径部分，例如: /base/UsxxbFSO4a0Q1tszVF9c2JpHnxg
            path = parsed_url.path

            # 3. 按照 '/' 分割并过滤掉空字符串
            # 结果类似于 ['base', 'UsxxbFSO4a0Q1tszVF9c2JpHnxg']
            parts = [p for p in path.split('/') if p]

            # 4. 逻辑判断：app_token 通常在 'base' 关键字之后
            if 'base' in parts:
                idx = parts.index('base')
                if idx + 1 < len(parts):
                    return parts[idx + 1]

            return ""
        except Exception:
            return ""

    def get_data_tables(self, app_token: str, page_size: int = 10, page_token: str = '') -> List[AppTable]:
        """
        获取数据表
        :param app_token:
        :param page_size:
        :param page_token:
        :return:
        """
        request: ListAppTableRequest = ListAppTableRequest.builder() \
            .app_token(app_token) \
            .page_size(page_size) \
            .build()
        response: ListAppTableResponse = self._feishu_api_client.client.bitable.v1.app_table.list(request)

        # 处理失败返回
        if not response.success():
            logger.error(
                f"client.bitable.v1.app_table.list failed, "
                f"code: {response.code}, "
                f"msg: {response.msg}, "
                f"log_id: {response.get_log_id()}, "
                f"resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return []
        else:
            return response.data.items

    def get_records(self, app_token: str, table_id: str, user_id_type: str, field_names: list, page_size: int = 10, page_token: str = ''):
        request: SearchAppTableRecordRequest = SearchAppTableRecordRequest.builder() \
            .app_token(app_token) \
            .table_id(table_id) \
            .user_id_type(user_id_type) \
            .page_token(page_token) \
            .page_size(page_size) \
            .request_body(SearchAppTableRecordRequestBody.builder()
                          .field_names(field_names)
                          .build()) \
            .build()

        # 发起请求
        response: SearchAppTableRecordResponse = self._feishu_api_client.client.bitable.v1.app_table_record.search(request)

        # 处理失败返回
        if not response.success():
            logger.error(
                f"client.bitable.v1.app_table_record.search failed, "
                f"code: {response.code}, "
                f"msg: {response.msg}, "
                f"log_id: {response.get_log_id()}, "
                f"resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return
        else:
            return response.data.items

    def delete_records(self, app_token: str, table_id: str, records: list, ignore_consistency_check: bool = True):
        request: BatchDeleteAppTableRecordRequest = BatchDeleteAppTableRecordRequest.builder() \
            .app_token(app_token) \
            .table_id(table_id) \
            .ignore_consistency_check(ignore_consistency_check) \
            .request_body(BatchDeleteAppTableRecordRequestBody.builder()
                          .records(records)
                          .build()) \
            .build()

        # 发起请求
        response: BatchDeleteAppTableRecordResponse = self._feishu_api_client.client.bitable.v1.app_table_record.batch_delete(request)

        # 处理失败返回
        if not response.success():
            logger.error(
                f"client.bitable.v1.app_table_record.batch_delete failed, "
                f"code: {response.code}, "
                f"msg: {response.msg}, "
                f"log_id: {response.get_log_id()}, "
                f"resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return False
        else:
            return True

    def add_records(self, app_token: str, table_id: str, records: list[dict], user_id_type: str = "open_id",
                    client_token: str = "", ignore_consistency_check: bool = True):
        app_table_records = []
        for record in records:
            _app_table_record = AppTableRecord.builder().fields(record).build()
            app_table_records.append(_app_table_record)
        request: BatchCreateAppTableRecordRequest = BatchCreateAppTableRecordRequest.builder() \
            .app_token(app_token) \
            .table_id(table_id) \
            .user_id_type(user_id_type) \
            .client_token(client_token) \
            .ignore_consistency_check(ignore_consistency_check) \
            .request_body(BatchCreateAppTableRecordRequestBody.builder()
                          .records(app_table_records)
                          .build()) \
            .build()

        # 发起请求
        response: BatchCreateAppTableRecordResponse = self._feishu_api_client.client.bitable.v1.app_table_record.batch_create(request)

        # 处理失败返回
        if not response.success():
            logger.error(
                f"client.bitable.v1.app_table_record.batch_create failed, "
                f"code: {response.code}, "
                f"msg: {response.msg}, "
                f"log_id: {response.get_log_id()}, "
                f"resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return False
        else:
            return True
