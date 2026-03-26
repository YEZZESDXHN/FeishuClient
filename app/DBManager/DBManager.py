import logging
import sqlite3
from typing import Optional, Union, List, Any

from app.user_data import CodeBeamerDefect

logger = logging.getLogger('FeishuClient.' + __name__)

DEFECTS_TABLE_NAME = 'cb_defects'
INFO_TABLE_NAME = 'info'


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
            logger.info(f"DDL语句执行成功：{sql[:50]}...")
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
                feishu_bitable_url TEXT DEFAULT ''
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
                modified_at INTEGER DEFAULT 0,
                modified_by TEXT DEFAULT '',
                fixed_in_release TEXT DEFAULT '',
                reported_in_release TEXT DEFAULT '',
                team TEXT DEFAULT '',
                owner TEXT DEFAULT '',
                submitted_by TEXT DEFAULT '',
                submitted_at INTEGER DEFAULT 0,
                frequency TEXT DEFAULT '',
                severity TEXT DEFAULT ''
            )
        """
        return self.execute_ddl(create_sql)

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
            logger.exception(f"精准批量 Upsert 失败: {e}")
            return {'inserted': 0, 'updated': 0, 'no_change': 0}

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


class DBManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.defects_db: DefectsDB = DefectsDB(self.db_path)
        self.info_db: InfoDB = InfoDB(self.db_path)

