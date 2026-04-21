import json
import logging
import os
import uuid
from datetime import datetime
from typing import Optional
from pathlib import Path

import gspread
import requests
import urllib3
from PySide6.QtCore import QObject, QThread, Signal, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QSystemTrayIcon, QMenu, QMessageBox
from apscheduler.schedulers.qt import QtScheduler
from apscheduler.triggers.cron import CronTrigger
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from app.CodebeamerClient.CodebeamerDefectClient import QCodebeamerDefectClient
from app.DBManager.DBManager import DBManager
from app.resources.resources import IconEngine
from app.windows.SchedulerJobsTable import SchedulerJobsTable

from app.FeishuApi.FeishuApiClient import FeishuApiClient
from app.FeishuApi.FeishuWsClient import WsClient
from app.ui.MainWindow import Ui_MainWindow
from app.user_data import CodeBeamerDefect
import lark_oapi.core.http.transport as feishu_transport

from lark_oapi.api.im.v1 import P2ImMessageReceiveV1
from lark_oapi.api.application.v6 import P2ApplicationBotMenuV6
# from app.FeishuApi.CustomEventDispatcherHandler import EventDispatcherHandler
from lark_oapi import EventDispatcherHandler
from lark_oapi.api.contact.v3 import GetUserRequest, GetUserResponse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger('FeishuClient.' + __name__)

feishu_session = requests.Session()

# 2. 配置重试策略 (针对底层的连接失败、握手超时自动重试)
# backoff_factor=1 表示重试间隔为 1s, 2s, 4s...
retry_strategy = Retry(
    total=3,  # 最多重试 3 次
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504], # 遇到飞书网关报错也重试
    allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"] # 允许重试的方法
)

# 3. 配置连接池大小 (20 个连接足够应付高频的批量操作)
adapter = HTTPAdapter(
    pool_connections=20,
    pool_maxsize=20,
    max_retries=retry_strategy
)
feishu_session.mount('https://', adapter)
feishu_session.mount('http://', adapter)

feishu_transport.requests = feishu_session


class QtSignaler(QObject):
    """用于发出信号的辅助类，确保线程安全"""
    log_signal = Signal(str)


class QtLoggingHandler(logging.Handler):
    def __init__(self, slot_func):
        super().__init__()
        self.signaler = QtSignaler()
        # 将信号连接到传入的 UI 更新函数（比如 textEdit.append）
        self.signaler.log_signal.connect(slot_func)

    def emit(self, record):
        # 格式化日志内容
        msg = self.format(record)
        # 通过信号发射出去，Qt 会自动处理跨线程 UI 更新
        self.signaler.log_signal.emit(msg)


class QWsClient(QObject, WsClient):
    signal_event_key = Signal(str, str)
    def __init__(self, app_id, app_secret, parent: "MainWindow"):
        super().__init__(app_id=app_id, app_secret=app_secret, feishu_client=parent.feishu_client)
        self.parent = parent

    def ws_client_event_handler_init(self):
        self.ws_client_event_handler = (
            EventDispatcherHandler.builder("", "")
            .register_p2_application_bot_menu_v6(self.do_p2_application_bot_menu_v6)
            .register_p2_im_message_receive_v1(self.do_p2_im_message_receive_v1)
            .build()
        )

    def do_p2_application_bot_menu_v6(self, data: P2ApplicationBotMenuV6) -> None:
        event_key = data.event.event_key
        open_id = data.event.operator.operator_id.open_id
        self.signal_event_key.emit(event_key, open_id)

    def do_p2_im_message_receive_v1(self, data: P2ImMessageReceiveV1):
        pass
        # if data.event.message.message_type == "text":
        #     res_content = json.loads(data.event.message.content)["text"]
        # else:
        #     res_content = "解析消息失败，请发送文本消息\nparse message failed, please send text message"
        #
        # content = json.dumps(
        #     {
        #         "text": "收到你发送的消息："
        #                 + res_content
        #     }
        # )
        #
        # if data.event.message.chat_type == "p2p":
        #     request: CreateMessageRequest = (
        #         CreateMessageRequest.builder()
        #         .receive_id_type("chat_id")
        #         .request_body(
        #             CreateMessageRequestBody.builder()
        #             .receive_id(data.event.message.chat_id)
        #             .msg_type("text")
        #             .content(content)
        #             .build()
        #         )
        #         .build()
        #     )
        #     # 使用OpenAPI发送消息
        #     # Use send OpenAPI to send messages
        #     # https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/create
        #     response: CreateMessageResponse = self.feishu_client.client.im.v1.message.create(request)
        #     print('self.client.im.v1.message.create(request)')
        #
        #     if not response.success():
        #         raise Exception(
        #             f"client.im.v1.message.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
        #         )
        # else:
        #     request: ReplyMessageRequest = (
        #         ReplyMessageRequest.builder()
        #         .message_id(data.event.message.message_id)
        #         .request_body(
        #             ReplyMessageRequestBody.builder()
        #             .content(content)
        #             .msg_type("text")
        #             .build()
        #         )
        #         .build()
        #     )
        #     # 使用OpenAPI回复消息
        #     # Reply to messages using send OpenAPI
        #     # https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/reply
        #     response: ReplyMessageResponse = self.feishu_client.client.im.v1.message.reply(request)
        #     if not response.success():
        #         raise Exception(
        #             f"client.im.v1.message.reply failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
        #         )


class QFeishuApiClient(QObject, FeishuApiClient):
    signal_data_tables = Signal(object)
    signal_init_finish = Signal()
    def __init__(self, app_id, app_secret):
        super().__init__(app_id=app_id, app_secret=app_secret)

    def get_data_tables(self, app_token):
        data_tables = self.bitable_api.get_data_tables(app_token)
        self.signal_data_tables.emit(data_tables)

    def client_init(self):
        super().client_init()
        self.signal_init_finish.emit()


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
            'Severity': 'severity',
            'Planned Release': 'planned_release'
        }
        self._gc = None  # 初始设为 None

    @property
    def gc(self):
        """只有在第一次调用 self.gc 时才进行 OAuth 认证"""
        if self._gc is None:
            self._gc = gspread.oauth(
                credentials_filename='./google_oauth/client_secret.json',
                authorized_user_filename='./google_oauth/authorized_user.json'
            )
        return self._gc

    def get_email_by_open_id(self, open_id):
        try:
            client = self.parent.feishu_client.client
            request: GetUserRequest = GetUserRequest.builder() \
                .user_id(open_id) \
                .user_id_type("open_id") \
                .build()

            # 发起请求
            response: GetUserResponse = client.contact.v3.user.get(request)

            # 处理失败返回
            if not response.success():
                logger.error(
                    f"client.contact.v3.user.get failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
                return
            else:
                return response.data.user.email
        except Exception as e:
            logger.error(f"client.contact.v3.user.get failed, {e}")
            return

    def code_beamer_defects_conversion_feishu_items(self, defects: list[CodeBeamerDefect],
                                                    feishu_records: Optional[list] = None,
                                                    is_add: bool = True):
        feishu_items = []

        def transform_defect(defect):
            item = {}
            for key, value in self.code_beamer_defect_field_map.items():
                if key == 'ID':
                    _id = getattr(defect, value, '')
                    item[key] = {
                        "text": str(_id),
                        "link": f"https://cb.alm.vnet.valeo.com/cb/issue/{_id}"
                    }
                else:
                    item[key] = getattr(defect, value, '')
            return item
        if is_add:
            for _defect in defects:
                feishu_items.append(transform_defect(_defect))
        else:
            if not feishu_records:
                logger.error('feishu_records 不能为空')
                return []

            if len(defects) != len(feishu_records):
                logger.error('defects 与 feishu_records 长度不一致')
                return []

                # 使用 zip 同时迭代，并将 record 作为外层字典的键
            for record, _defect in zip(feishu_records, defects):
                # 根据你的描述，返回“键是 feishu_records 成员”的字典
                feishu_items.append({
                    "record": record,  # 这里的 record 可以是 Feishu 的 record_id 或对象
                    "data": transform_defect(_defect)
                })
        return feishu_items

    def send_assigned_notify(self, members, title):
        feishu_client = self.parent.feishu_client
        if not members:
            logger.warning(f"团队成员为空")
            return
        defect_db = self.parent.db_manager.defects_db
        update_time = self.parent.db_manager.update_time_db.get_update_time()
        for test_member in members:
            defects = defect_db.get_active_defects_by_assignee(test_member)
            if defects:
                logger.debug(f"即将给{test_member}发送assigned推送，数量：{len(defects)}")
                content = {
                    'zh_cn': {
                        'title': f'{title} 数量:{len(defects)}',
                        "content": []
                    }
                }
                defect_content = content['zh_cn']['content']
                defect_content.append([{
                    "tag": "text",
                    "text": f"数据同步时间：{update_time}"
                }])
                for defect in defects:
                    defect_content.append([{"tag": "hr"}])
                    defect_content.append([
                        {
                            "tag": "a",
                            "href": f"https://cb.alm.vnet.valeo.com/cb/issue/{defect.defect_id}",
                            "text": f"{defect.defect_id}  ",
                            "style": ["bold", "italic"]
                        },
                        {
                            "tag": "text",
                            "text": f"{defect.summary}"
                        },
                    ])
                    ext_info = []
                    if defect.submitted_by:
                        ext_info.append({
                                "tag": "text",
                                "text": f"提交人：{defect.submitted_by}   "
                            })

                    if defect.status:
                        ext_info.append({
                            "tag": "text",
                            "text": f"状态：{defect.status}   "
                        })

                    if defect.fixed_in_release:
                        ext_info.append({
                                "tag": "text",
                                "text": f"修复版本：{defect.fixed_in_release}   "
                            })
                    if defect.severity:
                        ext_info.append({
                                "tag": "text",
                                "text": f"问题等级：{defect.severity}   "
                            })
                    defect_content.append(ext_info)

                feishu_client.send_message(
                    receive_id_type='email',
                    receive_id=test_member,
                    msg_type='post',
                    content=content
                )
            else:
                logger.debug(f"无指派给{test_member}的bug，跳过")

    def send_assigned_to_test_notify(self):
        logger.info(f"开始执行job,给测试团队发送assigned通知...")
        members = self.parent.test_members
        self.send_assigned_notify(members, '以下为Assigned给你的Bug，请及时验证并流转状态！')
        logger.info(f"测试团队发送assigned通知执行完毕")

    def send_assigned_to_sys_notify(self):
        logger.info(f"开始执行job,给系统团队发送assigned通知...")
        members = self.parent.sys_members
        self.send_assigned_notify(members, '以下为Assigned给你的Bug，请及时分析并流转状态！')
        logger.info(f"系统团队发送assigned通知执行完毕")

    def send_assigned_to_sw_notify(self):
        logger.info(f"开始执行job,给软件团队发送assigned通知...")
        members = self.parent.sw_members
        self.send_assigned_notify(members, '以下为Assigned给你的Bug，请及时分析并修复，修复完成将状态改为Implemented后转给测试！')
        logger.info(f"软件团队发送assigned通知执行完毕")

    def send_added_today_notify(self):
        chat_id = self.parent.group_chat_id
        logger.info(f"开始执行job,群发今日新增defects,chat_id:{chat_id}...")
        if not chat_id:
            logger.warning(f"未定义group chat id")
            return
        feishu_client = self.parent.feishu_client
        update_time = self.parent.db_manager.update_time_db.get_update_time()
        try:
            defects = self.parent.db_manager.defects_db.get_today_defects()

            content = {
                'zh_cn': {
                    'title': f'今日新增Defects数量:{len(defects)}',
                    "content": []
                }
            }
            defect_content = content['zh_cn']['content']
            defect_content.append([{
                "tag": "text",
                "text": f"数据同步时间：{update_time}"
            }])
            if defects:
                for defect in defects:
                    defect_content.append([{"tag": "hr"}])
                    defect_content.append([
                        {
                            "tag": "a",
                            "href": f"https://cb.alm.vnet.valeo.com/cb/issue/{defect.defect_id}",
                            "text": f"{defect.defect_id}  ",
                            "style": ["bold", "italic"]
                        },
                        {
                            "tag": "text",
                            "text": f"{defect.summary}"
                        },
                    ])
                    ext_info = []
                    if defect.submitted_by:
                        ext_info.append({
                            "tag": "text",
                            "text": f"提交人：{defect.submitted_by}   "
                        })
                    if defect.status:
                        ext_info.append({
                            "tag": "text",
                            "text": f"状态：{defect.status}   "
                        })
                    if defect.assigned_to:
                        ext_info.append({
                            "tag": "text",
                            "text": f"指派人：{defect.assigned_to}   "
                        })
                    if defect.severity:
                        ext_info.append({
                            "tag": "text",
                            "text": f"问题等级：{defect.severity}   "
                        })
                    defect_content.append(ext_info)

            feishu_client.send_message(
                receive_id_type='chat_id',
                receive_id=chat_id,
                msg_type='post',
                content=content
            )
            logger.info(f"发送今日新增defects执行完毕")

        except Exception as e:
            logger.error(f"send_added_today_notify执行失败，{e}")

    def send_added_yesterday_notify(self):
        chat_id = self.parent.group_chat_id
        logger.info(f"开始执行job,群发昨日新增defects,chat_id:{chat_id}...")
        if not chat_id:
            logger.warning(f"未定义group chat id")
            return
        feishu_client = self.parent.feishu_client
        update_time = self.parent.db_manager.update_time_db.get_update_time()
        try:
            defects = self.parent.db_manager.defects_db.get_yesterday_defects()

            content = {
                'zh_cn': {
                    'title': f'昨日新增Defects数量:{len(defects)}',
                    "content": []
                }
            }
            defect_content = content['zh_cn']['content']
            defect_content.append([{
                "tag": "text",
                "text": f"数据同步时间：{update_time}"
            }])
            if defects:
                for defect in defects:
                    defect_content.append([{"tag": "hr"}])
                    defect_content.append([
                        {
                            "tag": "a",
                            "href": f"https://cb.alm.vnet.valeo.com/cb/issue/{defect.defect_id}",
                            "text": f"{defect.defect_id}  ",
                            "style": ["bold", "italic"]
                        },
                        {
                            "tag": "text",
                            "text": f"{defect.summary}"
                        },
                    ])
                    ext_info = []
                    if defect.submitted_by:
                        ext_info.append({
                            "tag": "text",
                            "text": f"提交人：{defect.submitted_by}   "
                        })
                    if defect.status:
                        ext_info.append({
                            "tag": "text",
                            "text": f"状态：{defect.status}   "
                        })
                    if defect.assigned_to:
                        ext_info.append({
                            "tag": "text",
                            "text": f"指派人：{defect.assigned_to}   "
                        })
                    if defect.severity:
                        ext_info.append({
                            "tag": "text",
                            "text": f"问题等级：{defect.severity}   "
                        })
                    defect_content.append(ext_info)

            feishu_client.send_message(
                receive_id_type='chat_id',
                receive_id=chat_id,
                msg_type='post',
                content=content
            )
            logger.info(f"发送昨日新增defects执行完毕")

        except Exception as e:
            logger.error(f"send_added_yesterday_notify执行失败，{e}")

    def sync_code_beamer_defect_to_database(self):
        logger.info(f"开始执行Defects同步到数据库...")
        code_beamer_client = self.parent.cb_client
        if code_beamer_client.client.is_authenticated() or code_beamer_client.client.authenticate():
            try:

                project_id = self.parent.cb_projects[self.parent.comboBox_CBProject.currentIndex()]['id']

                tracker_id = code_beamer_client.get_tracker_id_by_name('Defect', project_id)
                items = code_beamer_client.get_all_items_by_query(tracker_id=tracker_id, filter_active=False)
                defs = code_beamer_client.convert_defect_items(items)
                result = self.parent.db_manager.defects_db.batch_upsert_defects(defs)
                self.parent.db_manager.update_time_db.set_now()
                logger.info(f"Defect同步成功，{result}")
            except Exception as e:
                logger.error(f'获取CB Defect失败，{e}')

    def load_google_spec_config(self) -> dict:
        """读取 config 文件到全局变量"""
        config_path = "./config/google_spec_config.json"
        if not os.path.exists(config_path):
            return {}

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def update_google_spec_test_report_arp(self):
        logger.info(f"开始更新google spec apr report")
        defects_db = self.parent.db_manager.defects_db
        config_dict = self.load_google_spec_config()
        reported_defects = defects_db.get_active_defects_by_reported_in_release(config_dict["sw_version"])

        open_defects = defects_db.get_active_open_defects()
        sh = self.gc.open_by_url(config_dict["google_spec_url"])

        worksheet = sh.worksheet(config_dict['sheet_name'])
        reported_defects_matrix = []
        open_defects_matrix = []
        for defect in reported_defects:
            reported_defects_matrix.append(
                [f'=HYPERLINK("https://cb.alm.vnet.valeo.com/cb/issue/{defect.defect_id}", {defect.defect_id})',
                 'Open',
                 defect.summary,
                 defect.status,
                 defect.severity,
                 self.unix_ms_to_date(defect.submitted_at, -28800000)
                 ])

        for defect in open_defects:
            open_defects_matrix.append(
                [f'=HYPERLINK("https://cb.alm.vnet.valeo.com/cb/issue/{defect.defect_id}", {defect.defect_id})',
                 'Open',
                 defect.summary,
                 defect.status,
                 defect.severity,
                 self.unix_ms_to_date(defect.submitted_at, -28800000)
                 ])

        worksheet.batch_clear(config_dict["del_range"])
        worksheet.update(range_name=config_dict["new_defects_range_name"], values=open_defects_matrix, value_input_option='USER_ENTERED')
        worksheet.update(range_name=config_dict["open_defects_range_name"], values=reported_defects_matrix, value_input_option='USER_ENTERED')
        logger.info(f"更新google spec apr report完成")

    def unix_ms_to_date(self, unix_ms, offset=0):
        """
        将 13 位毫秒级 Unix 时间戳转换为日期字符串
        格式: YYYY-MM-DD HH:MM:SS
        """
        # 1. 将毫秒转为秒 (13位 -> 10位)
        dt_object = datetime.fromtimestamp((unix_ms + offset) / 1000.0)

        # 2. 格式化输出
        return dt_object.strftime('%Y-%m-%d %H:%M:%S')

    def sync_code_beamer_defect_to_feishu(self):
        logger.info(f"开始执行Defects同步到飞书...")
        code_beamer_client = self.parent.cb_client
        feishu_client = self.parent.feishu_client
        admin_email = None
        if self.parent.admin_members:
            admin_email = self.parent.admin_members[0]
        if not feishu_client.client:
            feishu_client.client_init()
        if code_beamer_client.client.is_authenticated() or code_beamer_client.client.authenticate():
            try:

                project_id = self.parent.cb_projects[self.parent.comboBox_CBProject.currentIndex()]['id']

                tracker_id = code_beamer_client.get_tracker_id_by_name('Defect', project_id)
                items = code_beamer_client.get_all_items_by_query(tracker_id=tracker_id, filter_active=False)
                defs = code_beamer_client.convert_defect_items(items)
                result = self.parent.db_manager.defects_db.batch_upsert_defects(defs)
                self.parent.db_manager.update_time_db.set_now()
                logger.info(f"获取defect情况，{result}")
                if result['inserted'] == 0 and result['updated'] == 0:
                    if admin_email:
                        feishu_client.message_api.send_message(
                            receive_id_type='email',
                            receive_id=admin_email,
                            msg_type='text',
                            content={'text': f"Defect同步成功，{result}"}
                        )
                    logger.info(f'Defect同步成功(无变化，跳过)')
                    return
            except Exception as e:
                logger.error(f'获取CB Defect失败，{e}')
                if admin_email:
                    feishu_client.message_api.send_message(
                        receive_id_type='email',
                        receive_id=admin_email,
                        msg_type='text',
                        content={'text': f"Defect同步失败"}
                    )
                return
            try:
                table_index = self.parent.comboBox_BitableDateTable.currentIndex()
                table_id = self.parent.feishu_bitable_tables[table_index]['table_id']
                app_token = self.parent.feishu_bitable_app_token
                feishu_items = feishu_client.bitable_api.get_records(
                    app_token=app_token,
                    table_id=table_id,
                    field_names=['ID']
                )
                if not feishu_items:
                    logger.warning(f'未获取到飞书记录')
            except Exception as e:
                table_index = self.parent.comboBox_BitableDateTable.currentIndex()
                logger.error(f"获取多维表格数据表{self.parent.feishu_bitable_tables[table_index]['name']}记录失败，{e}")
                if admin_email:
                    feishu_client.message_api.send_message(
                        receive_id_type='email',
                        receive_id=admin_email,
                        msg_type='text',
                        content={'text': f"Defect同步失败"}
                    )
                return
            # record_ids = []
            defect_id_and_record_map = {}
            try:

                for feishu_item in feishu_items:

                    try:
                        defect_id = feishu_item.fields["ID"]['text']
                        # record_ids.append(feishu_item.record_id)
                        defect_id_and_record_map[defect_id] = feishu_item.record_id
                    except Exception as e:
                        logger.error(f"获取defect_id失败,删除该记录：{feishu_item.record_id}，{feishu_item.fields}，{e}")
                        feishu_client.bitable_api.delete_records(
                            app_token=app_token,
                            table_id=table_id,
                            records=[feishu_item.record_id]
                        )

                # feishu_client.bitable_api.delete_records(
                #     app_token=app_token,
                #     table_id=table_id,
                #     records=record_ids
                # )
            except Exception as e:
                logger.error(f"获取多维表格defect数据失败，{e}")
                if admin_email:
                    feishu_client.message_api.send_message(
                        receive_id_type='email',
                        receive_id=admin_email,
                        msg_type='text',
                        content={'text': f"Defect同步失败,删除多维表格数据失败"}
                    )
                return
            try:
                add_defs = []
                update_defs = []
                update_feishu_records = []
                for _def in defs:
                    if str(_def.defect_id) in defect_id_and_record_map:
                        update_defs.append(_def)
                        update_feishu_records.append(defect_id_and_record_map[str(_def.defect_id)])
                    else:
                        add_defs.append(_def)

                add_records = self.code_beamer_defects_conversion_feishu_items(add_defs)
                update_records = self.code_beamer_defects_conversion_feishu_items(update_defs, update_feishu_records, False)

                feishu_client.bitable_api.add_records(
                    app_token=app_token,
                    table_id=table_id,
                    records=add_records)
                feishu_client.bitable_api.update_records(
                    app_token=app_token,
                    table_id=table_id,
                    records=update_records)
                logger.info(f'更新飞书表格：{len(update_records)}，新增：{len(add_records)}')
            except Exception as e:
                logger.error(f"同步多维表格数据失败，{e}")
                if admin_email:
                    feishu_client.message_api.send_message(
                        receive_id_type='email',
                        receive_id=admin_email,
                        msg_type='text',
                        content={'text': f"Defect同步失败"}
                    )
                return

            logger.info(f"Defects同步已完成")
            if admin_email:
                feishu_client.message_api.send_message(
                    receive_id_type='email',
                    receive_id=admin_email,
                    msg_type='text',
                    content={'text': f"Defect同步成功，{result}"}
                )

    def test_job(self):
        logger.info("test_job")

    def resp_today_submit(self, open_id):
        logger.info(f"开始执行resp_today_submit...")
        feishu_client = self.parent.feishu_client
        email = self.get_email_by_open_id(open_id)
        if not email:
            logger.error(f"获取email失败")
            return
        update_time = self.parent.db_manager.update_time_db.get_update_time()
        try:
            defects = self.parent.db_manager.defects_db.get_today_defects()

            content = {
                'zh_cn': {
                    'title': f'今日新增Defects数量:{len(defects)}',
                    "content": []
                }
            }
            defect_content = content['zh_cn']['content']
            defect_content.append([{
                "tag": "text",
                "text": f"数据同步时间：{update_time}"
            }])
            if defects:
                for defect in defects:
                    defect_content.append([{"tag": "hr"}])
                    defect_content.append([
                        {
                            "tag": "a",
                            "href": f"https://cb.alm.vnet.valeo.com/cb/issue/{defect.defect_id}",
                            "text": f"{defect.defect_id}  ",
                            "style": ["bold", "italic"]
                        },
                        {
                            "tag": "text",
                            "text": f"{defect.summary}"
                        },
                    ])
                    ext_info = []
                    if defect.submitted_by:
                        ext_info.append({
                            "tag": "text",
                            "text": f"提交人：{defect.submitted_by}   "
                        })
                    if defect.status:
                        ext_info.append({
                            "tag": "text",
                            "text": f"状态：{defect.status}   "
                        })
                    if defect.assigned_to:
                        ext_info.append({
                            "tag": "text",
                            "text": f"指派人：{defect.assigned_to}   "
                        })
                    if defect.severity:
                        ext_info.append({
                            "tag": "text",
                            "text": f"问题等级：{defect.severity}   "
                        })
                    defect_content.append(ext_info)

            feishu_client.send_message(
                receive_id_type='email',
                receive_id=email,
                msg_type='post',
                content=content
            )
            logger.info(f"发送今日新增defects执行完毕")

        except Exception as e:
            logger.error(f"resp_today_submit执行失败，{e}")

    def resp_yesterday_submit(self, open_id):
        logger.info(f"开始执行resp_yesterday_submit...")
        feishu_client = self.parent.feishu_client
        email = self.get_email_by_open_id(open_id)
        if not email:
            logger.error(f"获取email失败")
            return
        update_time = self.parent.db_manager.update_time_db.get_update_time()
        try:
            defects = self.parent.db_manager.defects_db.get_yesterday_defects()

            content = {
                'zh_cn': {
                    'title': f'昨日新增Defects数量:{len(defects)}',
                    "content": []
                }
            }
            defect_content = content['zh_cn']['content']
            defect_content.append([{
                "tag": "text",
                "text": f"数据同步时间：{update_time}"
            }])
            if defects:
                for defect in defects:
                    defect_content.append([{"tag": "hr"}])
                    defect_content.append([
                        {
                            "tag": "a",
                            "href": f"https://cb.alm.vnet.valeo.com/cb/issue/{defect.defect_id}",
                            "text": f"{defect.defect_id}  ",
                            "style": ["bold", "italic"]
                        },
                        {
                            "tag": "text",
                            "text": f"{defect.summary}"
                        },
                    ])
                    ext_info = []
                    if defect.submitted_by:
                        ext_info.append({
                            "tag": "text",
                            "text": f"提交人：{defect.submitted_by}   "
                        })
                    if defect.status:
                        ext_info.append({
                            "tag": "text",
                            "text": f"状态：{defect.status}   "
                        })
                    if defect.assigned_to:
                        ext_info.append({
                            "tag": "text",
                            "text": f"指派人：{defect.assigned_to}   "
                        })
                    if defect.severity:
                        ext_info.append({
                            "tag": "text",
                            "text": f"问题等级：{defect.severity}   "
                        })
                    defect_content.append(ext_info)

            feishu_client.send_message(
                receive_id_type='email',
                receive_id=email,
                msg_type='post',
                content=content
            )
            logger.info(f"发送今日新增defects执行完毕")

        except Exception as e:
            logger.error(f"resp_today_submit执行失败，{e}")

    def resp_assigned_to_me(self, open_id):
        feishu_client = self.parent.feishu_client
        email = self.get_email_by_open_id(open_id)
        if not email:
            logger.error(f"获取email失败")
            return
        defect_db = self.parent.db_manager.defects_db
        update_time = self.parent.db_manager.update_time_db.get_update_time()
        defects = defect_db.get_active_defects_by_assignee(email)

        content = {
            'zh_cn': {
                'title': f'指派给你的票数量:{len(defects)}',
                "content": []
            }
        }
        defect_content = content['zh_cn']['content']
        defect_content.append([{
            "tag": "text",
            "text": f"数据同步时间：{update_time}"
        }])
        if defects:
            for defect in defects:
                defect_content.append([{"tag": "hr"}])
                defect_content.append([
                    {
                        "tag": "a",
                        "href": f"https://cb.alm.vnet.valeo.com/cb/issue/{defect.defect_id}",
                        "text": f"{defect.defect_id}  ",
                        "style": ["bold", "italic"]
                    },
                    {
                        "tag": "text",
                        "text": f"{defect.summary}"
                    },
                ])
                ext_info = []
                if defect.submitted_by:
                    ext_info.append({
                        "tag": "text",
                        "text": f"提交人：{defect.submitted_by}   "
                    })
                if defect.status:
                    ext_info.append({
                        "tag": "text",
                        "text": f"状态：{defect.status}   "
                    })

                if defect.fixed_in_release:
                    ext_info.append({
                        "tag": "text",
                        "text": f"修复版本：{defect.fixed_in_release}"
                    })
                if defect.severity:
                    ext_info.append({
                        "tag": "text",
                        "text": f"问题等级：{defect.severity}   "
                    })
                defect_content.append(ext_info)

        feishu_client.send_message(
            receive_id_type='email',
            receive_id=email,
            msg_type='post',
            content=content
        )

    def resp_submitted_by_me(self, open_id):
        feishu_client = self.parent.feishu_client
        email = self.get_email_by_open_id(open_id)
        if not email:
            logger.error(f"获取email失败")
            return
        defect_db = self.parent.db_manager.defects_db
        update_time = self.parent.db_manager.update_time_db.get_update_time()
        defects = defect_db.get_active_defects_by_submitted(email)

        content = {
            'zh_cn': {
                'title': f'你提交的票数量:{len(defects)}',
                "content": []
            }
        }
        defect_content = content['zh_cn']['content']
        defect_content.append([{
            "tag": "text",
            "text": f"数据同步时间：{update_time}"
        }])
        if defects:
            for defect in defects:
                defect_content.append([{"tag": "hr"}])
                defect_content.append([
                    {
                        "tag": "a",
                        "href": f"https://cb.alm.vnet.valeo.com/cb/issue/{defect.defect_id}",
                        "text": f"{defect.defect_id}  ",
                        "style": ["bold", "italic"]
                    },
                    {
                        "tag": "text",
                        "text": f"{defect.summary}"
                    },
                ])
                ext_info = []
                if defect.status:
                    ext_info.append({
                        "tag": "text",
                        "text": f"状态：{defect.status}   "
                    })
                if defect.assigned_to:
                    ext_info.append({
                        "tag": "text",
                        "text": f"指派人：{defect.assigned_to}   "
                    })
                if defect.planned_release:
                    ext_info.append({
                        "tag": "text",
                        "text": f"Planned Release：{defect.planned_release}   "
                    })
                if defect.severity:
                    ext_info.append({
                        "tag": "text",
                        "text": f"问题等级：{defect.severity}   "
                    })
                defect_content.append(ext_info)

        feishu_client.send_message(
            receive_id_type='email',
            receive_id=email,
            msg_type='post',
            content=content
        )


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    自定义的主窗口类，继承了 QMainWindow（Qt主窗口行为）
    """
    signal_update_data_tables = Signal(str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.logo_icon = QIcon("logo.ico")
        self.setWindowIcon(self.logo_icon)

        self.qt_logging_handler = QtLoggingHandler(self.textEdit.append)
        self.qt_logging_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
        self.qt_logging_handler.setFormatter(formatter)
        feishu_logger = logging.getLogger('FeishuClient')
        lark_logger = logging.getLogger('Lark')
        apscheduler_logger = logging.getLogger('apscheduler')
        feishu_logger.addHandler(self.qt_logging_handler)
        lark_logger.addHandler(self.qt_logging_handler)
        apscheduler_logger.addHandler(self.qt_logging_handler)

        self.test_members = []
        self.sw_members = []
        self.sys_members = []
        self.admin_members = []

        self.scheduler = QtScheduler()
        self.scheduler.start()
        self.check_ws_client_state_timer = QTimer()
        self.check_ws_client_state_timer.setInterval(500)
        self.check_ws_client_state_timer.timeout.connect(self.check_feishu_ws_client_state)
        self.check_ws_client_state_timer.start()
        self.feishu_client_state: bool = False  #
        self.feishu_ws_client_state: bool = False  #
        self.db_path = 'Database/database.db'
        self.db_manager: Optional[DBManager] = None
        self.init_database(self.db_path)
        self.init_scheduler_jobs()
        self.cb_projects: list[dict] = []
        self.cb_username: str = ''
        self.cb_password: str = '.'

        self.feishu_app_id: str = ''
        self.feishu_secret: str = ''
        self.feishu_bitable_url: str = ''
        self.feishu_bitable_tables: list[dict] = []  # [{table_id: table_name}]
        self.feishu_bitable_app_token: str = ''
        self.group_chat_id:  str = ''
        self._runner_init()
        self.feishu_client: Optional[QFeishuApiClient] = None
        self._feishu_client_init()

        self.feishu_ws_client: Optional[QWsClient] = None
        self._feishu_ws_client_init()

        self.cb_client: Optional[QCodebeamerDefectClient] = None
        self._codebeamer_init()
        self.job_name_map = {
            "同步Defects到飞书": self.runner.sync_code_beamer_defect_to_feishu,
            '给测试团队发送assigned票通知': self.runner.send_assigned_to_test_notify,
            "给系统团队发送assigned票通知": self.runner.send_assigned_to_sys_notify,
            "给开发团队发送assigned票通知": self.runner.send_assigned_to_sw_notify,
            "今日新增票通知": self.runner.send_added_today_notify,
            "昨日新增票通知": self.runner.send_added_yesterday_notify,
            "更新google spec APR report": self.runner.update_google_spec_test_report_arp,
            "同步Defects到数据库": self.runner.sync_code_beamer_defect_to_database,
            "test": self.runner.test_job,
        }
        self.event_key_map = {
            "指派给我的Bug": self.runner.resp_assigned_to_me,
            "我提交的Bug": self.runner.resp_submitted_by_me,
            "昨日新增Bug": self.runner.resp_yesterday_submit,
            "今天新增Bug": self.runner.resp_today_submit,
        }
        self.signal_connect()
        self.load_members()
        self.init_ui()
        self.init_tray()

    def init_tray(self):
        """初始化系统托盘"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.logo_icon)  # 同样使用这个 ico
        self.tray_icon.setToolTip("CodeBeamer-飞书同步工具")
        self.tray_icon.show()

        # 托盘图标被激活（比如点击）时的行为
        self.tray_icon.activated.connect(self.on_tray_activated)

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:  # 单击托盘
            self.showNormal()
            self.activateWindow()  # 确保窗口提到最前

    def load_members(self):
        """读取 config 文件到全局变量"""
        member_config_path = './config/team_members.json'
        if not os.path.exists(member_config_path):
            self.test_members = []
            self.sw_members = []
            self.sys_members = []
            self.admin_members = []

        try:
            with open(member_config_path, 'r', encoding='utf-8') as f:
                members = json.load(f)
                self.test_members = members['test_members']
                self.sw_members = members['sw_members']
                self.sys_members = members['sys_members']
                self.admin_members = members['admin_members']
        except (json.JSONDecodeError, IOError):
            self.test_members = []
            self.sw_members = []
            self.sys_members = []
            self.admin_members = []

    def setup_scheduler_jobs_table(self):
        layout = self.tab_scheduler.layout()
        if not layout:
            layout = QVBoxLayout(self.tab_scheduler)

        self.scheduler_jobs_table = SchedulerJobsTable(parent=self)
        layout.addWidget(self.scheduler_jobs_table)

    def execute_task_logic(self, job_name):
        """
        所有定时任务的统一执行逻辑
        """
        func = self.job_name_map.get(job_name)
        if func:
            func()
        else:
            logger.error(f"找不到任务: {job_name}")

    def execute_task_logic_ws_client(self, event_key, open_id):
        """
        所有定时任务的统一执行逻辑
        """
        func = self.event_key_map.get(event_key)
        if func:
            func(open_id)
        else:
            logger.error(f"找不到任务: {event_key}")

    def init_scheduler_jobs(self):
        """
        从数据库加载所有任务并注入到调度器中
        通常在程序启动（__init__ 或 show 后）调用一次
        """
        # 1. 从数据库获取所有任务记录（返回的是字典列表）
        jobs = self.db_manager.scheduler_db.get_all_jobs()
        if not jobs:
            logger.info("数据库中无定时任务记录")
            return

        count = 0
        for job_info in jobs:
            job_id = job_info['job_id']
            job_type = job_info['job_type']
            job_param = job_info['job_param']
            job_name = job_info.get('job_name', '未命名任务')

            try:
                self.add_job(job_id, job_name, job_type, job_param)

                count += 1
                logger.info(f"成功恢复任务: {job_name} (ID: {job_id})")

            except Exception as e:
                logger.error(f"恢复任务 {job_id} 失败: {str(e)}")

        logger.info(f"定时任务初始化完成，共加载 {count} 个任务")

    def reschedule_job(self, job_id, job_type, job_param):
        try:
            # 1. 如果是 cron 类型，且你传入的是 "5 * * * *" 这种字符串
            if job_type == 'cron':
                trigger = CronTrigger.from_crontab(job_param)
                return self.scheduler.reschedule_job(job_id, trigger=trigger)
            # 2. 如果是 interval 类型 (假设 job_param 是秒数，或者是 "seconds=10" 这种格式)
            elif job_type == 'interval':
                # 如果你的 job_param 是数字，这里可以直接用 seconds=int(job_param)
                # 或者更通用的做法是解析参数，这里演示最常用的秒数：
                return self.scheduler.reschedule_job(job_id, trigger='interval', seconds=int(job_param))

            else:
                raise ValueError(f"不支持的触发类型: {job_type}")

        except Exception as e:
            print(f"重设任务失败: {e}")
            return None

    def remove_job(self, job_id):
        self.scheduler.remove_job(job_id)

    def add_job(self, job_id, job_name, job_type, job_param):
        if job_type == 'interval':
            # 转换参数为整数（秒）
            self.scheduler.add_job(
                self.execute_task_logic,  # 统一的任务执行入口
                'interval',
                seconds=int(job_param),
                id=job_id,
                name=job_name,
                args=[job_name]  # 传递 ID 和名称给执行函数
            )

        elif job_type == 'cron':
            # 如果是 Cron 表达式，直接传入字符串
            # 假设 UI 存入的是简单的秒数偏移或标准 5/6 位表达式
            self.scheduler.add_job(
                self.execute_task_logic,
                trigger=CronTrigger.from_crontab(job_param),
                id=job_id,
                name=job_name,
                args=[job_name]
            )

        elif job_type == 'date':
            self.scheduler.add_job(
                self.execute_task_logic,
                'date',
                run_date=job_param,  # 需符合 ISO 8601 格式
                id=job_id,
                name=job_name,
                args=[job_name]
            )

    def init_ui(self):
        self.setup_scheduler_jobs_table()
        self.pushButton_FeishuClient.setIcon(IconEngine.get_icon('unlink', 'red'))
        self.pushButton_FeishuWsClient.setIcon(IconEngine.get_icon('unlink', 'red'))

        config = self.db_manager.info_db.get_config()
        self.pushButton_RefreshDataTable.setDisabled(True)
        self.comboBox_BitableDateTable.setDisabled(True)
        self.comboBox_ManualTrigger.addItems(self.job_name_map.keys())
        if config:
            try:
                self.cb_username = config['cb_username']
                self.cb_password = config['cb_password']
                self.feishu_app_id = config['feishu_app_id']
                self.feishu_secret = config['feishu_secret']
                self.feishu_bitable_url = config['feishu_bitable_url']
                self.group_chat_id = config['feishu_group_chat_id']
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
                self.lineEdit_GroupChatID.setText(self.group_chat_id)
            except Exception as e:
                logger.error(f"初始化ui info失败， {e}")

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

    def check_feishu_ws_client_state(self):
        if self.feishu_ws_client.ws_client and self.feishu_ws_client.ws_client._conn:
            self.feishu_ws_client_state = True
            self.pushButton_FeishuWsClient.setIcon(IconEngine.get_icon('link', 'green'))
        else:
            self.feishu_ws_client_state = False
            self.pushButton_FeishuWsClient.setIcon(IconEngine.get_icon('unlink', 'red'))

    def check_feishu_client_state(self):
        if self.feishu_client.client:
            self.feishu_client_state = True
            self.pushButton_RefreshDataTable.setDisabled(False)
            self.comboBox_BitableDateTable.setDisabled(False)
            self.pushButton_ManualTrigger.setDisabled(False)
            self.pushButton_FeishuClient.setIcon(IconEngine.get_icon('link', 'green'))
            # self.pushButton_RefreshDataTable.clicked.emit()

    def _runner_init(self):
        self.runner_thread = QThread()
        self.runner = QRunner(self)
        self.runner.moveToThread(self.runner_thread)
        self.runner_thread.start()

    def _codebeamer_init(self):
        self.cb_client_thread = QThread()
        self.cb_client = QCodebeamerDefectClient(self.cb_username, self.cb_password)
        self.cb_client.moveToThread(self.cb_client_thread)
        self.cb_client_thread.start()

    def _feishu_client_init(self):
        self.feishu_client_thread = QThread()
        self.feishu_client = QFeishuApiClient(self.feishu_app_id, self.feishu_secret)
        self.feishu_client.moveToThread(self.feishu_client_thread)
        self.feishu_client_thread.start()

    def _feishu_ws_client_init(self):
        self.feishu_ws_client_thread = QThread()
        self.feishu_ws_client = QWsClient(self.feishu_app_id, self.feishu_secret, self)
        self.feishu_ws_client.moveToThread(self.feishu_ws_client_thread)
        self.feishu_ws_client_thread.start()
        self.feishu_ws_client.signal_event_key.connect(self.ws_client_trigger_job)

    def manual_trigger_job(self):
        job_name = self.comboBox_ManualTrigger.currentText()
        if job_name in self.job_name_map:
            # 添加一个单次执行的任务
            self.scheduler.add_job(
                func=self.execute_task_logic,
                trigger='date',  # 立即执行一次
                args=[job_name],
                id=str(uuid.uuid4())[:8],
                name=f"手动触发-{job_name}",
                misfire_grace_time=60
            )
            logger.debug(f"已提交手动任务: {job_name}")

    def ws_client_trigger_job(self, event_key, open_id):
        if event_key in self.event_key_map:
            # 添加一个单次执行的任务
            self.scheduler.add_job(
                func=self.execute_task_logic_ws_client,
                trigger='date',  # 立即执行一次
                args=[event_key, open_id],
                id=str(uuid.uuid4())[:8],
                name=f"回调触发-{event_key}",
                misfire_grace_time=60
            )
            logger.debug(f"已提交回调任务: {event_key}")


    def signal_connect(self):
        self.lineEdit_Username.editingFinished.connect(self.update_cb_username)
        self.lineEdit_Password.editingFinished.connect(self.update_cb_password)
        self.lineEdit_AppID.editingFinished.connect(self.update_feishu_app_id)
        self.lineEdit_AppSecret.editingFinished.connect(self.update_feishu_secret)
        self.lineEdit_BitableUrl.editingFinished.connect(self.update_feishu_bitable_url)
        self.lineEdit_GroupChatID.editingFinished.connect(self.update_group_chat_id)
        self.pushButton_FeishuClient.clicked.connect(self.feishu_client.client_init)
        self.pushButton_FeishuWsClient.clicked.connect(self.feishu_ws_client.ws_client_start)
        self.feishu_client.signal_data_tables.connect(self.update_feishu_bitable_tables)
        self.signal_update_data_tables.connect(self.feishu_client.get_data_tables)
        self.pushButton_RefreshDataTable.clicked.connect(self.update_feishu_bitable_url)
        self.feishu_client.signal_init_finish.connect(self.check_feishu_client_state)
        self.pushButton_ManualTrigger.clicked.connect(self.manual_trigger_job)
        self.pushButton_GetProject.clicked.connect(self.cb_client.get_projects)
        self.cb_client.signal_projects.connect(self.update_cb_project)

    def update_cb_project(self, projects):
        self.cb_projects = projects
        projects_name_list = [project['name'] for project in self.cb_projects]
        self.comboBox_CBProject.clear()
        self.comboBox_CBProject.addItems(projects_name_list)

    def update_group_chat_id(self):
        self.group_chat_id = self.lineEdit_GroupChatID.text()
        self.cb_client.update_username(self.group_chat_id)
        self.db_manager.info_db.update_single_field(field_name='feishu_group_chat_id', value=self.group_chat_id)

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
        if not self.feishu_bitable_url:
            return
        self.db_manager.info_db.update_single_field(field_name='feishu_bitable_url', value=self.feishu_bitable_url)
        self.feishu_bitable_app_token = self.feishu_client.bitable_api.get_feishu_app_token(self.feishu_bitable_url)
        if not self.feishu_bitable_app_token:
            return
        if self.feishu_client_state:
            self.signal_update_data_tables.emit(self.feishu_bitable_app_token)
        else:
            return

    def update_feishu_bitable_tables(self, tables: list):
        self.feishu_bitable_tables.clear()
        name_list = []
        for table in tables:
            self.feishu_bitable_tables.append({'table_id': table.table_id, "name": table.name})
            name_list.append(table.name)
        self.comboBox_BitableDateTable.clear()
        self.comboBox_BitableDateTable.addItems(name_list)

    from PySide6.QtWidgets import QMessageBox, QSystemTrayIcon

    def closeEvent(self, event) -> None:
        """重写关闭事件，弹出选择对话框"""

        # 弹出提示框
        reply = QMessageBox.question(
            self,
            '退出确认',
            "您想彻底退出程序，还是隐藏到后台运行？\n\n[Yes]: 彻底退出\n[No]: 隐藏到后台",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # --- 情况 1: 彻底退出，执行原有的线程清理逻辑 ---
            logger.info("用户选择彻底退出，正在清理线程...")

            # 停止所有线程
            threads = [
                (self.runner_thread, "runner_thread"),
                (self.cb_client_thread, "cb_client_thread"),
                (self.feishu_client_thread, "feishu_client_thread"),
                (self.feishu_ws_client_thread, "feishu_ws_client_thread")
            ]
            for thread, name in threads:
                if thread and thread.isRunning():
                    thread.quit()
                    if not thread.wait(1000):
                        logger.warning(f"{name} 线程强制退出")

            event.accept()  # 接受关闭事件，程序退出

        elif reply == QMessageBox.No:
            # --- 情况 2: 隐藏到后台 ---
            event.ignore()  # 忽略关闭请求
            self.hide()  # 隐藏窗口
            if hasattr(self, 'tray_icon'):
                self.tray_icon.showMessage(
                    "同步工具",
                    "程序已转入后台运行",
                    QSystemTrayIcon.Information,
                    2000
                )
        else:
            # --- 情况 3: 用户点击了取消 (Cancel) ---
            event.ignore()
