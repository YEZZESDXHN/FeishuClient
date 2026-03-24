from datetime import datetime
import json
import os
import re
import time
from typing import Optional, Dict, List, Any

import requests

from app.user_data import CodeBeamerDefect


class CodebeamerLoginer:
    """
    CodebeamerLoginer API 客户端
    - 自动化认证（无需CSRF令牌）
    - 请求处理/解析
    """

    def __init__(self, username, password, base_url: str = "https://cb.alm.vnet.valeo.com"):
        """
        初始化Codebeamer客户端
        """
        self.base_url = base_url
        self.cb_base = f"{base_url}/cb"
        self.api_base = f"{self.cb_base}/api/v3"
        self.session = requests.Session()
        self.session.verify = False
        self._authenticated = False
        self.username = username
        self.password = password
        # self.authenticate(self.username, self.password)


    def is_authenticated(self) -> bool:
        """通过访问一个需要认证的端点来检查当前会话是否仍然有效"""
        if not self._authenticated:
            return False
        try:
            # /users/me 是一个轻量级的、需要认证的端点
            response = self.session.get(f"{self.api_base}/projects", timeout=10)
            self._authenticated = (response.status_code == 200)
            return self._authenticated
        except requests.RequestException:
            self._authenticated = False
            return False

    def authenticate(self) -> bool:
        """
        执行登录认证
        """
        print("=" * 60)
        print("Codebeamer 自动化认证")
        print("=" * 60)

        if not all([self.username, self.password]):
            print("❌ 认证失败：未提供用户名或密码。")
            return False

        login_url = f"{self.cb_base}/login.spr"
        login_data = {
            'user': self.username,
            'password': self.password,
            'targetURL': '/user'
        }

        print(f"正在登录用户: {self.username}...")

        try:
            response = self.session.post(
                login_url,
                data=login_data,
                allow_redirects=False,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )

            print(f"登录响应状态码: {response.status_code}")

            if response.status_code == 302:
                redirect_to = response.headers.get('Location', '')
                print(f"✅ 登录成功！重定向至: {redirect_to}")

                if response.cookies:
                    self.session.cookies.update(response.cookies)

                if redirect_to:
                    full_redirect_url = f"{self.cb_base}{redirect_to}"
                    self.session.get(full_redirect_url)

                self._prepare_api_headers()
                self._authenticated = True
                return True
            else:
                print(f"❌ 登录失败，状态码: {response.status_code}")
                self._authenticated = False
                return False

        except Exception as e:
            print(f"❌ 认证过程出错: {e}")
            return False

    def _prepare_api_headers(self):
        """
        准备API调用所需的请求头
        """
        api_headers = {
            'accept': 'application/json',
            'x-requested-with': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session.headers.update(api_headers)
        print("✅ API请求头已准备就绪")

    def get_json(self, url: str, params: Optional[Dict] = None) -> Dict:
        """
        发送GET请求并返回JSON数据
        """
        time.sleep(2)
        full_url = f"{self.api_base}/{url}" if not url.startswith('http') else url

        try:
            response = self.session.get(full_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            if hasattr(e.response, 'text'):
                print(f"错误响应: {e.response.text[:200]}")
            raise

    def post(self, endpoint: str, data: dict = None):
        """
        修正版 POST：自动处理 URL 拼接并增加路径调试
        """
        # 1. 极其严格的 URL 拼接逻辑
        base = self.api_base.rstrip('/')
        path = endpoint.lstrip('/')
        full_url = f"{base}/{path}"

        try:
            response = self.session.post(
                full_url,
                json=data,
                verify=False,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"  ❌ POST 请求失败 [{response.status_code}]")
                # 如果是 404，打印出请求头辅助排查
                if response.status_code == 404:
                    print(f"     请检查 base_url 是否包含 '/api/v3'。当前: {self.base_url}")
                return {"items": [], "total": 0}

        except Exception as e:
            print(f"  ❌ POST 请求异常: {e}")
            return {"items": [], "total": 0}


class CodebeamerClient:
    """
    项目特定的功能扩展
    """

    def __init__(self, username, password, base_url: str = "https://cb.alm.vnet.valeo.com"):
        """
        初始化项目实例
        """
        self.email_cache = {}
        self.email_cache_path = 'email_cache.json'
        self.load_emails()
        self.username = username
        self.password = password
        self.client = CodebeamerLoginer(self.username, self.password, base_url)
        # self.project_lists = self.client.get_json("projects")
        # self.project_id = None
        # self.project_info = None
        self.trackers = {}
        self.defect_tracker_id = None
        # 用于缓存用户名到全名的映射，避免重复请求API
        # self.user_cache = {}

    def update_username(self, username):
        self.username = username
        self.client.username = username

    def update_password(self, password):
        self.password = password
        self.client.password = password


    def get_project_info(self, project_id) -> Dict:
        """获取项目详细信息"""
        project_info = self.client.get_json(f"projects/{project_id}")
        print(f"✅ 项目信息: {project_info.get('name')}")
        return project_info

    def get_all_trackers_by_project(self, project_id: int = None) -> List[Dict]:
        """获取指定项目下所有的 Tracker"""
        pid = project_id
        if not pid:
            print("  ❌ 错误：未指定 Project ID，请先调用 get_project_id_by_name 或手动设置。")
            return []

        try:
            print(f"--> 正在获取项目 (ID: {pid}) 的 Tracker 列表...")
            trackers = self.client.get_json(f"projects/{pid}/trackers")
            if not trackers:
                print(f"  ⚠️ 警告：该项目 (ID: {pid}) 下没有可用的 Tracker。")
                return []
            print(f"  ✅ 成功获取 {len(trackers)} 个 Tracker。")
            return trackers
        except Exception as e:
            print(f"  ❌ 获取 Tracker 列表失败: {e}")
            return []

    def get_tracker_id_by_name(self, tracker_name: str, project_id: int = None) -> int:
        """根据 Tracker 名称获取 Tracker ID"""
        pid = project_id
        print(f"--> 正在查找 Tracker: '{tracker_name}' (项目ID: {pid})")

        trackers = self.get_all_trackers_by_project(pid)
        for t in trackers:
            if t.get('name') == tracker_name:
                t_id = t.get('id')
                print(f"  ✅ 匹配成功：'{tracker_name}' (ID: {t_id})")
                return t_id

        # 错误处理：打印该项目下可用的 Tracker 供排查
        available = [t.get('name') for t in trackers if t.get('name')]
        print(f"  ❌ 错误：在项目 {pid} 中未找到 Tracker '{tracker_name}'。")
        print(f"  📌 可用 Tracker 包括: {available}")
        raise ValueError(f"无法定位 Tracker: {tracker_name}")

    def get_all_items_by_query(self, tracker_id: int = None, page_size: int = 500, filter_active: bool = True):
        """
        全量获取函数：调用修正后的 post 方法
        """
        target_tracker_id = tracker_id

        all_items = []
        page = 1
        cbql_str = f"tracker.id IN ({target_tracker_id})"

        print(f"  🚀 开始批量分页抓取 (Tracker ID: {target_tracker_id})...")

        while True:
            payload = {
                "queryString": cbql_str,
                "page": page,
                "pageSize": page_size
            }

            # 注意：这里只传相对路径 'items/query'
            result = self.client.post("items/query", data=payload)

            items = result.get('items', [])
            if not items:
                break

            all_items.extend(items)
            print(f"    ✅ 已获取第 {page} 页，累计 {len(all_items)} 条...")

            if len(items) < page_size:
                break

            page += 1
            time.sleep(0.5)

        if not all_items:
            return []

        # 根据标志位判断是否过滤
        if filter_active:
            print("正在根据配置过滤 Closed 和 Cancelled 的Item...")
            filtered_items = self._filter_items(all_items)
        else:
            print("根据配置，保留所有状态的单子 (跳过过滤)...")
            filtered_items = all_items

        return filtered_items

    def get_user_full_name(self, username: str) -> str:
        """
        根据用户名字符串查找并拼接全名。
        """
        if not username:
            return ""


        try:
            url = f"users/findByName"
            # 发送请求，注意此处只传单个 username
            user_data = self.client.get_json(url, params={'name': username})

            if user_data:
                first_name = user_data.get('firstName', '')
                last_name = user_data.get('lastName', '')
                full_name = f"{first_name} {last_name}".strip()
                return full_name
            else:
                return ''
        except Exception as e:
            # 如果单个用户查找失败，保留原始 ID
            print(f"查找单个用户 {username} 详情失败: {e}")
            return ''

    def get_tracker_field_config(self, tracker_id: int, whitelist: list = None) -> Dict[str, Dict]:
        """
        根据传入的白名单动态获取字段配置。
        如果 whitelist 为空，则自适应导出所有字段。
        """
        fields_summary = self.client.get_json(f"trackers/{tracker_id}/fields")  #
        field_config = {}

        for f in fields_summary:
            f_id = f['id']
            f_name = f['name']
            # 清理字段名中的 HTML 标签
            clean_name = re.sub(r'<[^>]+>', '', f_name).strip()

            # 核心逻辑：如果启用了白名单，且字段不在白名单中，则跳过
            if whitelist and clean_name not in whitelist:
                continue

            try:
                # 获取 trackerItemField 用于路径自适应
                detail = self.client.get_json(f"trackers/{tracker_id}/fields/{f_id}")
                field_config[clean_name] = {
                    'id': f_id,
                    'path': detail.get('trackerItemField'),
                    'type': detail.get('type')
                }
            except:
                field_config[clean_name] = {'id': f_id, 'path': None}

        return field_config

    def convert_items_fully_adaptively(self, items: List[Dict], field_config: Dict[str, Dict]):
        """
        完全自适应转换：将 items 转换为 DataFrame，并转换用户全名
        """
        records = []
        for item in items:
            record = {}
            for f_name, config in field_config.items():
                f_path = config.get('path')
                f_id = config.get('id')

                # 策略 A：从顶层路径取值
                if f_path and f_path in item:
                    record[f_name] = self._parse_complex_value(item.get(f_path))

                # 策略 B：从 customFields 数组取值
                if f_name not in record or record[f_name] == "":
                    for cf in item.get('customFields', []):
                        if cf.get('fieldId') == f_id:
                            val_data = cf.get('values') if 'values' in cf else cf.get('value')
                            record[f_name] = self._parse_complex_value(val_data)

            # 后处理：转换用户全名、清洗 Wiki 和 日期
            for k, v in record.items():
                if isinstance(v, str):
                    # 如果字段名包含 'by' 或 'to'，尝试转换为全名
                    if any(user_key in k.lower() for user_key in ['by', 'to']):
                        v = self.get_user_full_name(v)

                    # 清洗 Wiki 标签，保留业务标记 [ANS]
                    if '%%' in v:
                        v = re.sub(r'%%\(.*?\)', '', v).replace('%!', '').strip()

                    # 仅处理日期字段的截断
                    if any(d_key in k.lower() for d_key in ['at', 'date', 'on/at']):
                        if 'T' in v and len(v) > 10: v = v[:10]

                    record[k] = v
            records.append(record)

        return records

    def _parse_complex_value(self, value: Any) -> str:
        """
        通用解析：将 Reference 对象解析为名称字符串
        """
        if value is None: return ""
        if isinstance(value, list):
            return ", ".join([str(self._parse_complex_value(i)) for i in value if i])
        if isinstance(value, dict):
            return value.get('name', str(value))
        return str(value)

    def _filter_items(self, items: List[Dict]) -> List[Dict]:
        """
        过滤item：删除状态为"Cancelled"或"Closed"的item
        """
        if not items:
            return []

        filtered_items = []
        cancelled_count = 0
        closed_count = 0
        active_count = 0

        for item in items:
            # 检查状态是否为"Cancelled"或"Closed"
            status = item.get('status', {}).get('name', '')

            if status == 'Cancelled':
                cancelled_count += 1
                continue

            if status == 'Closed':
                closed_count += 1
                continue

            # 保留其他状态的缺陷
            filtered_items.append(item)
            active_count += 1

        # 打印过滤统计
        print("\n" + "=" * 50)
        print("Item过滤统计")
        print("=" * 50)
        print(f"原始Item总数: {len(items)}")
        print(f"状态为 Cancelled 的Item: {cancelled_count}")
        print(f"状态为 Closed 的Item: {closed_count}")
        print(f"过滤后保留的Item: {active_count}")
        print("=" * 50)

        return filtered_items

    def load_emails(self):
        """读取 config 文件到全局变量"""
        if not os.path.exists(self.email_cache_path):
            self.email_cache = {}

        try:
            with open(self.email_cache_path, 'r', encoding='utf-8') as f:
                self.email_cache = json.load(f)
        except (json.JSONDecodeError, IOError):
            self.email_cache = {}

    def generate_email_by_username(self, username):
        # 1. 获取原始全名，例如 "Zhichen Wang" 或 "Prosper-Fei PAN"
        full_name = self.get_user_full_name(username)

        if not full_name:
            return None

        # 2. 处理逻辑：
        #    - lower(): 全部转为小写
        #    - strip(): 去除首尾多余空格
        #    - replace(" ", "."): 将中间的空格替换为点
        email_prefix = full_name.lower().strip().replace(" ", ".")

        # 3. 拼接后缀
        email = f"{email_prefix}@valeo.com"

        return email



    def get_email(self, username):
        """获取 Email，不存在则生成并持久化"""
        # 1. 尝试从内存/缓存中获取
        email = self.email_cache.get(username)

        if not email:
            # 2. 如果不存在，调用生成函数
            email = self.generate_email_by_username(username)

            # 3. 更新内存变量
            # if not email:
            #     return None
            self.email_cache[username] = email

            # 4. 同步写入 config 文件（持久化）
            try:
                with open(self.email_cache_path, 'w', encoding='utf-8') as f:
                    json.dump(self.email_cache, f, ensure_ascii=False, indent=4)
            except IOError as e:
                print(f"Error saving config: {e}")

        return email

    def convert_iso_to_unix(self, iso_str):
        """
        将 '2026-03-12T07:31:05.068' 转换为 Unix 时间戳
        """
        try:
            # 1. 自动解析 ISO 格式字符串
            dt = datetime.fromisoformat(iso_str)

            # 2. 返回毫秒秒级时间戳 (int)；如果需要毫秒，可以不乘以 1000
            return int(dt.timestamp() * 1000)
        except ValueError as e:
            print(f"Invalid format: {e}")
            return None

    def convert_defect_items(self, items) -> list[CodeBeamerDefect]:
        defect_list = []
        for item in items:
            defect = CodeBeamerDefect()
            defect.defect_id = item['id']
            defect.url = f"https://cb.alm.vnet.valeo.com/cb/issue/{defect.defect_id}"
            defect.status = item['status']['name']
            defect.summary = item['name']
            defect.assigned_to = ",".join(self.get_email(_item['name']) for _item in item['assignedTo'] if self.get_email(_item['name']))
            defect.modified_at = self.convert_iso_to_unix(item['modifiedAt']) + 28800000
            # print(f"modifiedAt:{item['modifiedAt']},unix:{self.convert_iso_to_unix(item['modifiedAt'])}")
            defect.modified_by = self.get_email(item['modifiedBy']['name'])
            try:
                defect.severity = item['severities'][0]['name']
            except:
                defect.severity = ''
            defect.fixed_in_release = ''
            defect.reported_in_release = ''
            for field in item['customFields']:
                if field['name'] == 'Reported in Release':
                    defect.reported_in_release = field['values'][0]['name']
                if field['name'] == 'Frequency':
                    defect.frequency = field['values'][0]['name']
                if field['name'] == 'Fixed in Release':
                    defect.fixed_in_release = field['values'][0]['name']

            try:
                defect.team = item['teams'][0]['name']
            except Exception as e:
                defect.team = ''
            defect.owner = ",".join(self.get_email(_item['name']) for _item in item['owners'] if self.get_email(_item['name']))
            defect.submitted_by = self.get_email(item['createdBy']['name'])
            defect.submitted_at = self.convert_iso_to_unix(item['createdAt']) + 28800000
            defect_list.append(defect)
        return defect_list

