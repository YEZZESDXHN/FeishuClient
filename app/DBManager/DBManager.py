import logging
import sqlite3
from datetime import date, timedelta, datetime
from typing import Optional, Union, List, Any

from app.user_data import CodeBeamerDefect

logger = logging.getLogger('FeishuClient.' + __name__)

DEFECTS_TABLE_NAME = 'cb_defects'
INFO_TABLE_NAME = 'info'
SCHEDULER_TABLE_NAME = 'scheduler'
EMAIL_CONTACTS_TABLE_NAME = 'email_contacts'
SYS_MEMBERS_TABLE_NAME = 'sys_members'
SW_MEMBERS_TABLE_NAME = 'sw_members'
TEST_MEMBERS_TABLE_NAME = 'test_members'
ADMIN_MEMBERS_TABLE_NAME = 'admin_members'
UPDATE_TIME_TABLE_NAME = 'update_time'


class DBBase:
    """数据库操作通用基类：封装通用逻辑，所有表操作子类继承"""
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_conn(self) -> sqlite3.Connection:
        """获取数据库连接：统一配置，便于后续全局修改（如开启连接池）"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")  # 全局开启外键，所有子类继承
        conn.row_factory = sqlite3.Row  # 让查询结果支持「列名取值」，更友好
        return conn

    def _safe_table_name(self, table_name: str) -> str:
        """安全拼接表名：双引号包裹，避免关键字/空格问题（延续之前的规范）"""
        return f'"{table_name}"'

    def execute_ddl(self, sql: str) -> bool:
        """执行DDL语句（建表/删表等），统一异常处理"""
        try:
            with self._get_conn() as conn:
                conn.execute(sql)
            logger.debug(f"DDL语句执行成功：{sql[:50]}...")
            return True
        except sqlite3.Error as e:
            logger.exception(f"DDL语句执行失败：{str(e)}")
            return False

    def execute_dml(self, sql: str, params: tuple = (), is_get_increment_id: bool = False) -> \
            Optional[Union[tuple[int, int], int]]:
        """
        执行DML语句（增/删/改），统一异常处理
        :return: 受影响行数或者tuple[受影响行数, 自增id]，失败返回None
        """
        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                if is_get_increment_id:
                    return cursor.rowcount, cursor.lastrowid
                else:
                    return cursor.rowcount
        except sqlite3.Error as e:
            logger.exception(f"DML语句执行失败：sql={sql[:100]}..., params={params}, error={str(e)}")
            return None

    def execute_dql(self, sql: str, params: tuple = ()) -> list[dict]:
        """
        通用DQL执行方法：执行SELECT查询，返回字典列表（列名→值）
        :param sql: SELECT查询语句（带?占位符）
        :param params: 查询参数元组
        :return: 结果字典列表，无数据/异常返回空列表
        """
        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                # 将查询结果转换为字典列表（列名作为key，适配所有表）
                columns = [col[0] for col in cursor.description]  # 获取查询列名
                result = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return result
        except sqlite3.Error as e:
            logger.exception(f"DQL查询失败：sql={sql[:100]}..., params={params}, error={str(e)}")
            return []


class SchedulerDB(DBBase):
    def __init__(self, db_path: str):
        super().__init__(db_path)
        self.table_name = SCHEDULER_TABLE_NAME
        self.safe_table = self._safe_table_name(self.table_name)
        self.init_database()

    def init_database(self) -> bool:
        """初始化表结构：增加 job_name 以便 UI 显示"""
        create_sql = f"""
            CREATE TABLE IF NOT EXISTS {self.safe_table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT UNIQUE NOT NULL,  -- APScheduler 用的字符串 ID
                job_name TEXT,                 -- 友好名称
                job_type TEXT NOT NULL,       -- interval, cron, date
                job_param TEXT NOT NULL,      -- 具体的间隔秒数或 cron 表达式
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        return self.execute_ddl(create_sql)

    def add_job_record(self, job_id: str, job_name: str, job_type: str, job_param: str) -> bool:
        """
        向数据库添加一条任务记录
        """
        sql = f"""
            INSERT INTO {self.safe_table} (job_id, job_name, job_type, job_param)
            VALUES (?, ?, ?, ?)
        """
        params = (job_id, job_name, job_type, job_param)
        # execute_dml 返回受影响行数，1 表示成功插入
        result = self.execute_dml(sql, params)
        return result is not None and result > 0

    def get_all_jobs(self) -> list[dict]:
        """
        获取所有任务，用于程序启动时重新加载到 APScheduler
        """
        sql = f"SELECT * FROM {self.safe_table} ORDER BY id DESC"
        return self.execute_dql(sql)

    def get_job_by_id(self, job_id: str) -> Optional[dict]:
        """
        根据 APScheduler 的字符串 ID 查询
        """
        sql = f"SELECT * FROM {self.safe_table} WHERE job_id = ?"
        results = self.execute_dql(sql, (job_id,))
        return results[0] if results else None

    def delete_job_by_job_id(self, job_id: str) -> bool:
        """
        根据 APScheduler 的任务 ID 删除记录
        """
        if not job_id:
            return False

        sql = f"DELETE FROM {self.safe_table} WHERE job_id = ?"
        rowcount = self.execute_dml(sql, (job_id,))

        if rowcount and rowcount >= 1:
            logger.info(f"数据库记录删除成功: job_id={job_id}")
            return True
        return False

    def update_job_param(self, job_id: str, new_param: str) -> bool:
        """
        更新现有任务的参数（比如修改了执行频率）
        """
        sql = f"UPDATE {self.safe_table} SET job_param = ? WHERE job_id = ?"
        rowcount = self.execute_dml(sql, (new_param, job_id))
        return rowcount is not None and rowcount > 0


class InfoDB(DBBase):
    def __init__(self, db_path: str):
        super().__init__(db_path)
        self.table_name = INFO_TABLE_NAME  # 建议明确表名
        self.safe_table = self._safe_table_name(self.table_name)

        # 定义唯一的固定主键值
        self.SINGLE_ROW_KEY = "GLOBAL_CONFIG"
        self.init_database()

    def init_database(self) -> bool:
        create_sql = f"""
            CREATE TABLE IF NOT EXISTS {self.safe_table} (
                key TEXT PRIMARY KEY,
                cb_username TEXT DEFAULT '',
                cb_password TEXT DEFAULT '',
                feishu_app_id TEXT DEFAULT '',
                feishu_secret TEXT DEFAULT '',
                feishu_bitable_url TEXT DEFAULT '',
                feishu_group_chat_id TEXT DEFAULT ''
            )
        """
        success = self.execute_ddl(create_sql)
        if success:
            # 核心逻辑：使用 INSERT OR IGNORE 确保表里至少有一行基础数据
            init_sql = f"INSERT OR IGNORE INTO {self.safe_table} (key) VALUES (?)"
            self.execute_dml(init_sql, (self.SINGLE_ROW_KEY,))
        return success

    def save_config(self, config_dict: dict) -> bool:
        """
        保存或更新那唯一的一条配置
        :param config_dict: 包含配置字段的字典
        """
        # 强制设置主键为固定值，确保永远只有一行
        config_dict['key'] = self.SINGLE_ROW_KEY

        fields = list(config_dict.keys())
        columns = ", ".join(fields)
        placeholders = ", ".join(["?"] * len(fields))

        # 使用 REPLACE INTO：如果 key 已存在则覆盖，不存在则插入
        sql = f"REPLACE INTO {self.safe_table} ({columns}) VALUES ({placeholders})"

        res = self.execute_dml(sql, tuple(config_dict.values()))
        return res is not None and res > 0

    def get_config(self) -> Optional[dict]:
        """获取那唯一的一条配置"""
        sql = f"SELECT * FROM {self.safe_table} WHERE key = ?"
        rows = self.execute_dql(sql, (self.SINGLE_ROW_KEY,))
        if rows:
            # 返回字典格式，方便直接使用
            return dict(rows[0])
        return None

    def update_single_field(self, field_name: str, value: Any) -> bool:
        """快捷方法：只更新某一个字段的值"""
        sql = f"UPDATE {self.safe_table} SET {field_name} = ? WHERE key = ?"
        res = self.execute_dml(sql, (value, self.SINGLE_ROW_KEY))
        return res is not None and res > 0


class UpdateTimeDB(DBBase):
    def __init__(self, db_path: str):
        super().__init__(db_path)
        self.table_name = UPDATE_TIME_TABLE_NAME
        self.safe_table = self._safe_table_name(self.table_name)

        # 定义唯一的固定主键值
        self.SINGLE_ROW_KEY = "GLOBAL_UPDATE_TIME"
        self.init_database()

    def init_database(self) -> bool:
        """初始化表，使用 TEXT 存储时间"""
        create_sql = f"""
            CREATE TABLE IF NOT EXISTS {self.safe_table} (
                key TEXT PRIMARY KEY,
                UpdateTime TEXT DEFAULT ''
            )
        """
        success = self.execute_ddl(create_sql)
        if success:
            # 确保初始化一行数据。如果不存在，初始时间设为空字符串或一个极早的时间
            init_sql = f"INSERT OR IGNORE INTO {self.safe_table} (key, UpdateTime) VALUES (?, ?)"
            self.execute_dml(init_sql, (self.SINGLE_ROW_KEY, "1970-01-01 00:00:00"))
        return success

    def get_update_time(self) -> str:
        """获取存储的时间字符串"""
        sql = f"SELECT UpdateTime FROM {self.safe_table} WHERE key = ?"
        rows = self.execute_dql(sql, (self.SINGLE_ROW_KEY,))
        if rows and rows[0]['UpdateTime']:
            return rows[0]['UpdateTime']
        return ""

    def set_update_time(self, time_str: str) -> bool:
        """手动设置更新时间字符串"""
        sql = f"UPDATE {self.safe_table} SET UpdateTime = ? WHERE key = ?"
        rowcount = self.execute_dml(sql, (time_str, self.SINGLE_ROW_KEY))
        return rowcount is not None and rowcount > 0

    def set_now(self) -> bool:
        """自动将当前系统时间存入数据库 (格式: YYYY-MM-DD HH:MM:SS)"""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.set_update_time(now_str)


class DefectsDB(DBBase):
    def __init__(self, db_path: str):
        super().__init__(db_path)
        self.table_name = DEFECTS_TABLE_NAME
        self.safe_table = self._safe_table_name(self.table_name)
        self.init_defects_database()

    def init_defects_database(self):
        """初始化表结构：字段与 CodeBeamerDefect 属性一一对应"""
        create_sql = f"""
            CREATE TABLE IF NOT EXISTS {self.safe_table} (
                defect_id INTEGER PRIMARY KEY,
                status TEXT DEFAULT '',
                summary TEXT NOT NULL,
                assigned_to TEXT DEFAULT '',
                assigned_to_email TEXT DEFAULT '',
                modified_at INTEGER DEFAULT 0,
                modified_by TEXT DEFAULT '',
                modified_by_email TEXT DEFAULT '',
                fixed_in_release TEXT DEFAULT '',
                reported_in_release TEXT DEFAULT '',
                team TEXT DEFAULT '',
                owner TEXT DEFAULT '',
                owner_email TEXT DEFAULT '',
                submitted_by TEXT DEFAULT '',
                submitted_by_email TEXT DEFAULT '',
                submitted_at INTEGER DEFAULT 0,
                frequency TEXT DEFAULT '',
                severity TEXT DEFAULT ''
            )
        """
        return self.execute_ddl(create_sql)

    def _get_timestamp_ms(self, days_offset: int = 0) -> int:
        """
        私有辅助方法：获取指定日期 00:00:00 的 13 位毫秒时间戳
        days_offset: 0 代表今天, -1 代表昨天
        """
        target_date = date.today() + timedelta(days=days_offset)
        dt = datetime.combine(target_date, datetime.min.time())
        return int(dt.timestamp() * 1000)

    def get_today_defects(self) -> list[CodeBeamerDefect]:
        """获取今天 00:00 之后新增的缺陷"""
        today_start = self._get_timestamp_ms(0)

        sql = f"SELECT * FROM {self.safe_table} WHERE submitted_at >= ? ORDER BY submitted_at DESC"
        rows = self.execute_dql(sql, (today_start,))
        return [CodeBeamerDefect.model_validate(dict(row)) for row in rows]

    def get_yesterday_defects(self) -> list[CodeBeamerDefect]:
        """获取昨天 00:00 到 23:59 之间新增的缺陷"""
        yesterday_start = self._get_timestamp_ms(-1)
        today_start = self._get_timestamp_ms(0)

        # 范围查询：大于等于昨天零点，且小于今天零点
        sql = f"""
            SELECT * FROM {self.safe_table} 
            WHERE submitted_at >= ? AND submitted_at < ? 
            ORDER BY submitted_at DESC
        """
        rows = self.execute_dql(sql, (yesterday_start, today_start))
        return [CodeBeamerDefect.model_validate(dict(row)) for row in rows]

    def get_active_defects_by_assignee(self, assignee_email: str) -> list[CodeBeamerDefect]:
        """
        获取指定负责人的进行中缺陷
        逻辑：assigned_to 包含 assignee_name
             且 status 不在 ('Cancel', 'Closed', 'Resolved') 中
        """
        # 使用 LIKE 实现“包含”
        # 使用 NOT IN 排除已结束的状态
        # 注意：这里的状态字符串建议与你 CodeBeamer 中的实际值保持一致（大小写敏感）
        sql = f"""
            SELECT * FROM {self.safe_table} 
            WHERE assigned_to LIKE ? 
            AND status NOT IN ('Cancelled', 'Closed')
            ORDER BY modified_at DESC
        """

        # 构造模糊查询参数：%某人%
        params = (f"%{assignee_email}%",)

        rows = self.execute_dql(sql, params)

        if not rows:
            return []

        # 转换为 Pydantic 模型列表
        return [CodeBeamerDefect.model_validate(dict(row)) for row in rows]

    def _get_model_fields(self) -> list[str]:
        """获取模型的所有字段名，用于动态生成 SQL"""
        return list(CodeBeamerDefect.model_fields.keys())

    def upsert_defect(self, defect: CodeBeamerDefect) -> bool:
        """单条保存或更新"""
        fields = self._get_model_fields()
        placeholders = ", ".join(["?"] * len(fields))
        columns = ", ".join(fields)

        # 使用 REPLACE INTO 简化逻辑：存在则更新，不存在则插入
        sql = f"REPLACE INTO {self.safe_table} ({columns}) VALUES ({placeholders})"

        # 将模型转换为元组，注意顺序要与 fields 一致
        data = tuple(getattr(defect, field) for field in fields)
        rowcount = self.execute_dml(sql, data)
        return rowcount is not None and rowcount > 0

    def batch_upsert_defects(self, defects: list[CodeBeamerDefect]) -> dict[str, int]:
        """
        批量处理并返回真正【新增】和【内容发生变化】的数量
        """
        if not defects:
            return {'inserted': 0, 'updated': 0, 'ignored': 0}

        fields = self._get_model_fields()
        # 排除主键，用于对比和设置值
        data_fields = [f for f in fields if f != 'defect_id']

        # 1. 尝试批量插入（忽略已存在的 ID）
        insert_sql = f"""
            INSERT OR IGNORE INTO {self.safe_table} 
            ({", ".join(fields)}) VALUES ({", ".join(['?'] * len(fields))})
        """

        # 2. 尝试更新（仅当内容有变化时）
        # 逻辑：WHERE defect_id = ? AND (status != ? OR summary != ? ...)
        # 注意：SQLite 处理 NULL 比较时需要用 IS NOT 或手动转为空字符串（你的模型已处理为空字符串，所以直接用 !=）
        where_conditions = " OR ".join([f"{f} != ?" for f in data_fields])
        update_sql = f"""
            UPDATE {self.safe_table} 
            SET {", ".join([f"{f} = ?" for f in data_fields])}
            WHERE defect_id = ? AND ({where_conditions})
        """

        inserted_total = 0
        updated_total = 0

        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()

                # 执行插入
                insert_params = [tuple(getattr(d, f) for f in fields) for d in defects]
                cursor.executemany(insert_sql, insert_params)
                inserted_total = cursor.rowcount

                # 执行更新（对比内容）
                update_params = []
                for d in defects:
                    vals = tuple(getattr(d, f) for f in data_fields)  # SET 的值
                    current_id = (d.defect_id,)  # WHERE 的 ID
                    compare_vals = tuple(getattr(d, f) for f in data_fields)  # 用于对比的值
                    update_params.append(vals + current_id + compare_vals)

                cursor.executemany(update_sql, update_params)
                updated_total = cursor.rowcount

            return {
                'inserted': inserted_total,
                'updated': updated_total,
                'no_change': len(defects) - inserted_total - updated_total
            }
        except sqlite3.Error as e:
            raise f"批量 Upsert 失败: {e}"

    def get_all_defects(self) -> list[CodeBeamerDefect]:
        """获取所有缺陷，并自动转换为模型对象列表"""
        sql = f"SELECT * FROM {self.safe_table}"
        rows = self.execute_dql(sql)
        # 利用 Pydantic 的 model_validate 快速转换
        return [CodeBeamerDefect.model_validate(dict(row)) for row in rows]

    def get_defect_by_id(self, defect_id: int) -> Optional[CodeBeamerDefect]:
        """按 ID 查询单个缺陷"""
        sql = f"SELECT * FROM {self.safe_table} WHERE defect_id = ?"
        rows = self.execute_dql(sql, (defect_id,))
        if rows:
            return CodeBeamerDefect.model_validate(dict(rows[0]))
        return None

    def delete_defect(self, defect_id: int) -> bool:
        """删除单个缺陷"""
        sql = f"DELETE FROM {self.safe_table} WHERE defect_id = ?"
        res = self.execute_dml(sql, (defect_id,))
        return res is not None and res > 0

    def batch_delete_defects(self, defect_ids: list[int]) -> int:
        """批量删除"""
        if not defect_ids:
            return 0
        placeholders = ", ".join(["?"] * len(defect_ids))
        sql = f"DELETE FROM {self.safe_table} WHERE defect_id IN ({placeholders})"
        res = self.execute_dml(sql, tuple(defect_ids))
        return res if res is not None else 0

    def delete_all_defects(self) -> bool:
        """删除所有数据（清空表）"""
        sql = f"DELETE FROM {self.safe_table}"
        return self.execute_ddl(sql)


class EmailDB(DBBase):
    def __init__(self, db_path: str):
        super().__init__(db_path)
        self.table_name = EMAIL_CONTACTS_TABLE_NAME
        self.safe_table = self._safe_table_name(self.table_name)
        self.init_database()

    def init_database(self) -> bool:
        """
        初始化表：short_name 作为主键，email 为联系方式
        """
        create_sql = f"""
            CREATE TABLE IF NOT EXISTS {self.safe_table} (
                short_name TEXT PRIMARY KEY, 
                email TEXT NOT NULL,
                feishu_userid
            )
        """
        return self.execute_ddl(create_sql)

    def add_or_update_email(self, short_name: str, email: str, feishu_userid: str = '') -> bool:
        """
        添加或更新邮件记录（使用 REPLACE 语法：如果主键冲突则覆盖）
        """
        sql = f"REPLACE INTO {self.safe_table} (short_name, email, feishu_userid) VALUES (?, ?, ?)"
        rowcount = self.execute_dml(sql, (short_name, email, feishu_userid))
        return rowcount is not None and rowcount > 0

    def get_email_by_name(self, short_name: str) -> Optional[str]:
        """
        根据简称获取邮箱地址
        """
        sql = f"SELECT email FROM {self.safe_table} WHERE short_name = ?"
        results = self.execute_dql(sql, (short_name,))
        return results[0]['email'] if results else None

    def get_all_emails(self) -> list[dict]:
        """
        获取所有联系人清单
        """
        sql = f"SELECT * FROM {self.safe_table} ORDER BY short_name ASC"
        return self.execute_dql(sql)

    def delete_email_by_name(self, short_name: str) -> bool:
        """
        根据简称删除记录
        """
        sql = f"DELETE FROM {self.safe_table} WHERE short_name = ?"
        rowcount = self.execute_dml(sql, (short_name,))
        return rowcount is not None and rowcount > 0


class TestMemberDB(DBBase):
    def __init__(self, db_path: str):
        super().__init__(db_path)
        self.table_name = TEST_MEMBERS_TABLE_NAME
        self.safe_table = self._safe_table_name(self.table_name)
        self.init_database()

    def init_database(self) -> bool:
        """
        初始化表：email 设置为 UNIQUE，确保不会重复存储相同的邮箱
        """
        create_sql = f"""
            CREATE TABLE IF NOT EXISTS {self.safe_table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                email TEXT NOT NULL UNIQUE
            )
        """
        return self.execute_ddl(create_sql)

    # --- 增加 / 更新 ---
    def add_email(self, email: str) -> bool:
        """
        添加新邮箱。如果邮箱已存在，由于 UNIQUE 约束，此操作会被忽略。
        """
        sql = f"INSERT OR IGNORE INTO {self.safe_table} (email) VALUES (?)"
        rowcount = self.execute_dml(sql, (email,))
        # 执行成功且没有报错（即使因为重复被 ignore 也会返回 rowcount）
        return rowcount is not None

    # --- 删除 ---
    def delete_email(self, email: str) -> bool:
        """
        根据邮箱地址删除记录
        """
        sql = f"DELETE FROM {self.safe_table} WHERE email = ?"
        rowcount = self.execute_dml(sql, (email,))
        return rowcount is not None and rowcount > 0

    # --- 查询 ---
    def get_all_emails(self) -> List[str]:
        """
        获取所有邮箱列表，返回纯字符串列表，方便 PySide6 UI 组件使用
        """
        sql = f"SELECT email FROM {self.safe_table} ORDER BY email ASC"
        results = self.execute_dql(sql)
        if not results:
            return []
        # 将结果从 [{'email': 'a@b.com'}, ...] 转换为 ['a@b.com', ...]
        return [row['email'] for row in results]

    def is_email_exists(self, email: str) -> bool:
        """
        检查某个邮箱是否已经在数据库中
        """
        sql = f"SELECT 1 FROM {self.safe_table} WHERE email = ? LIMIT 1"
        results = self.execute_dql(sql, (email,))
        return len(results) > 0

    def clear_all(self) -> bool:
        """
        清空所有成员记录
        """
        sql = f"DELETE FROM {self.safe_table}"
        return self.execute_dml(sql) is not None


class AdminMemberDB(DBBase):
    def __init__(self, db_path: str):
        super().__init__(db_path)
        self.table_name = ADMIN_MEMBERS_TABLE_NAME
        self.safe_table = self._safe_table_name(self.table_name)
        self.init_database()

    def init_database(self) -> bool:
        """
        初始化表：email 设置为 UNIQUE，确保不会重复存储相同的邮箱
        """
        create_sql = f"""
            CREATE TABLE IF NOT EXISTS {self.safe_table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                email TEXT NOT NULL UNIQUE
            )
        """
        return self.execute_ddl(create_sql)

    # --- 增加 / 更新 ---
    def add_email(self, email: str) -> bool:
        """
        添加新邮箱。如果邮箱已存在，由于 UNIQUE 约束，此操作会被忽略。
        """
        sql = f"INSERT OR IGNORE INTO {self.safe_table} (email) VALUES (?)"
        rowcount = self.execute_dml(sql, (email,))
        # 执行成功且没有报错（即使因为重复被 ignore 也会返回 rowcount）
        return rowcount is not None

    # --- 删除 ---
    def delete_email(self, email: str) -> bool:
        """
        根据邮箱地址删除记录
        """
        sql = f"DELETE FROM {self.safe_table} WHERE email = ?"
        rowcount = self.execute_dml(sql, (email,))
        return rowcount is not None and rowcount > 0

    # --- 查询 ---
    def get_all_emails(self) -> List[str]:
        """
        获取所有邮箱列表，返回纯字符串列表，方便 PySide6 UI 组件使用
        """
        sql = f"SELECT email FROM {self.safe_table} ORDER BY email ASC"
        results = self.execute_dql(sql)
        if not results:
            return []
        # 将结果从 [{'email': 'a@b.com'}, ...] 转换为 ['a@b.com', ...]
        return [row['email'] for row in results]

    def is_email_exists(self, email: str) -> bool:
        """
        检查某个邮箱是否已经在数据库中
        """
        sql = f"SELECT 1 FROM {self.safe_table} WHERE email = ? LIMIT 1"
        results = self.execute_dql(sql, (email,))
        return len(results) > 0

    def clear_all(self) -> bool:
        """
        清空所有成员记录
        """
        sql = f"DELETE FROM {self.safe_table}"
        return self.execute_dml(sql) is not None


class SysMemberDB(DBBase):
    def __init__(self, db_path: str):
        super().__init__(db_path)
        self.table_name = SYS_MEMBERS_TABLE_NAME
        self.safe_table = self._safe_table_name(self.table_name)
        self.init_database()

    def init_database(self) -> bool:
        """
        初始化表：email 设置为 UNIQUE，确保不会重复存储相同的邮箱
        """
        create_sql = f"""
            CREATE TABLE IF NOT EXISTS {self.safe_table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                email TEXT NOT NULL UNIQUE
            )
        """
        return self.execute_ddl(create_sql)

    # --- 增加 / 更新 ---
    def add_email(self, email: str) -> bool:
        """
        添加新邮箱。如果邮箱已存在，由于 UNIQUE 约束，此操作会被忽略。
        """
        sql = f"INSERT OR IGNORE INTO {self.safe_table} (email) VALUES (?)"
        rowcount = self.execute_dml(sql, (email,))
        # 执行成功且没有报错（即使因为重复被 ignore 也会返回 rowcount）
        return rowcount is not None

    # --- 删除 ---
    def delete_email(self, email: str) -> bool:
        """
        根据邮箱地址删除记录
        """
        sql = f"DELETE FROM {self.safe_table} WHERE email = ?"
        rowcount = self.execute_dml(sql, (email,))
        return rowcount is not None and rowcount > 0

    # --- 查询 ---
    def get_all_emails(self) -> List[str]:
        """
        获取所有邮箱列表，返回纯字符串列表，方便 PySide6 UI 组件使用
        """
        sql = f"SELECT email FROM {self.safe_table} ORDER BY email ASC"
        results = self.execute_dql(sql)
        if not results:
            return []
        # 将结果从 [{'email': 'a@b.com'}, ...] 转换为 ['a@b.com', ...]
        return [row['email'] for row in results]

    def is_email_exists(self, email: str) -> bool:
        """
        检查某个邮箱是否已经在数据库中
        """
        sql = f"SELECT 1 FROM {self.safe_table} WHERE email = ? LIMIT 1"
        results = self.execute_dql(sql, (email,))
        return len(results) > 0

    def clear_all(self) -> bool:
        """
        清空所有成员记录
        """
        sql = f"DELETE FROM {self.safe_table}"
        return self.execute_dml(sql) is not None


class SwMemberDB(DBBase):
    def __init__(self, db_path: str):
        super().__init__(db_path)
        self.table_name = SW_MEMBERS_TABLE_NAME
        self.safe_table = self._safe_table_name(self.table_name)
        self.init_database()

    def init_database(self) -> bool:
        """
        初始化表：email 设置为 UNIQUE，确保不会重复存储相同的邮箱
        """
        create_sql = f"""
            CREATE TABLE IF NOT EXISTS {self.safe_table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                email TEXT NOT NULL UNIQUE
            )
        """
        return self.execute_ddl(create_sql)

    # --- 增加 / 更新 ---
    def add_email(self, email: str) -> bool:
        """
        添加新邮箱。如果邮箱已存在，由于 UNIQUE 约束，此操作会被忽略。
        """
        sql = f"INSERT OR IGNORE INTO {self.safe_table} (email) VALUES (?)"
        rowcount = self.execute_dml(sql, (email,))
        # 执行成功且没有报错（即使因为重复被 ignore 也会返回 rowcount）
        return rowcount is not None

    # --- 删除 ---
    def delete_email(self, email: str) -> bool:
        """
        根据邮箱地址删除记录
        """
        sql = f"DELETE FROM {self.safe_table} WHERE email = ?"
        rowcount = self.execute_dml(sql, (email,))
        return rowcount is not None and rowcount > 0

    # --- 查询 ---
    def get_all_emails(self) -> List[str]:
        """
        获取所有邮箱列表，返回纯字符串列表，方便 PySide6 UI 组件使用
        """
        sql = f"SELECT email FROM {self.safe_table} ORDER BY email ASC"
        results = self.execute_dql(sql)
        if not results:
            return []
        # 将结果从 [{'email': 'a@b.com'}, ...] 转换为 ['a@b.com', ...]
        return [row['email'] for row in results]

    def is_email_exists(self, email: str) -> bool:
        """
        检查某个邮箱是否已经在数据库中
        """
        sql = f"SELECT 1 FROM {self.safe_table} WHERE email = ? LIMIT 1"
        results = self.execute_dql(sql, (email,))
        return len(results) > 0

    def clear_all(self) -> bool:
        """
        清空所有成员记录
        """
        sql = f"DELETE FROM {self.safe_table}"
        return self.execute_dml(sql) is not None


class DBManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.defects_db: DefectsDB = DefectsDB(self.db_path)
        self.info_db: InfoDB = InfoDB(self.db_path)
        self.scheduler_db: SchedulerDB = SchedulerDB(self.db_path)
        self.update_time_db: UpdateTimeDB = UpdateTimeDB(self.db_path)
        # self.email_db: EmailDB = EmailDB(self.db_path)
        # self.sys_member_db: SysMemberDB = SysMemberDB(self.db_path)
        # self.sw_member_db: SwMemberDB = SwMemberDB(self.db_path)
        # self.test_member_db: TestMemberDB = TestMemberDB(self.db_path)
        # self.admin_member_db: AdminMemberDB = AdminMemberDB(self.db_path)

