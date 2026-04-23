import logging
import re

from PySide6.QtCore import QObject, Signal

from app.CodebeamerClient.CodebeamerClient import CodebeamerClient
from app.user_data import CodeBeamerDefect

logger = logging.getLogger('FeishuClient.' + __name__)


class QCodebeamerDefectClient(QObject, CodebeamerClient):
    signal_projects = Signal(object)
    def __init__(self, username, password):
        super().__init__(username=username, password=password)

    def clean_wiki_text(self, raw_text):
        # 1. 移除样式标签 %%(...)，支持嵌套括号
        cleaned = re.sub(r'%%\((?:[^)(]+|\([^)(]*\))*\)', '', raw_text)

        # 2. 移除闭合标签 %!
        cleaned = cleaned.replace('%!', '')

        # 3. 彻底移除反斜杠（处理 Wiki 的 \\ 换行标记）
        # 使用正则 r'\\+' 匹配任何连续的 1 个或多个反斜杠，直接删掉
        # 这能彻底解决 Python 转义带来的 \ 或 \\ 残留问题
        cleaned = re.sub(r'\\+', '', cleaned)

        # 4. 移除加粗用的双下划线 __
        cleaned = cleaned.replace('__', '')

        # 5. 排版优化：清理清洗后产生的“多余空行”
        # 将只包含空格/制表符的行变成彻底的空行
        cleaned = re.sub(r'^[ \t]+$', '', cleaned, flags=re.MULTILINE)
        # 将 3 个以上的连续换行压缩为 2 个换行（保留正常的段落间距）
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

        # 6。替换特殊的波浪号横杠 ~- 为普通的 - (新增规则)
        cleaned = cleaned.replace('~-', '-')

        lines = [line.strip() for line in cleaned.splitlines() if line.strip()]

        # 最后把保留下来的有效行，用单个换行符重新拼接
        return '\n'.join(lines)

    def convert_defect_items(self, items) -> list[CodeBeamerDefect]:
        defect_list = []
        for item in items:
            defect = CodeBeamerDefect()
            defect.defect_id = item['id']
            defect.status = item['status']['name']
            defect.summary = item['name']
            defect.assigned_to_email = ",".join(self.get_email(_item['name'])[1] for _item in item['assignedTo'] if self.get_email(_item['name']))
            defect.assigned_to = ",".join(self.get_email(_item['name'])[0] for _item in item['assignedTo'] if self.get_email(_item['name']))
            defect.modified_at = self.convert_iso_to_unix(item['modifiedAt']) + 28800000 * 2
            # print(f"modifiedAt:{item['modifiedAt']},unix:{self.convert_iso_to_unix(item['modifiedAt'])}")
            defect.modified_by_email = self.get_email(item['modifiedBy']['name'])[1]
            defect.modified_by = self.get_email(item['modifiedBy']['name'])[0]
            try:
                defect.severity = item['severities'][0]['name']
            except:
                defect.severity = ''
            try:
                defect.planned_release = item['versions'][0]['name']
            except:
                defect.planned_release = ''
            defect.fixed_in_release = ''
            defect.reported_in_release = ''
            for field in item['customFields']:
                if field['name'] == 'Origin':
                    defect.origin = field['values'][0]['name']
                if field['name'] == 'Reported in Release':
                    defect.reported_in_release = field['values'][0]['name']
                if field['name'] == 'Frequency':
                    defect.frequency = field['values'][0]['name']
                if field['name'] == 'Fixed in Release':
                    defect.fixed_in_release = field['values'][0]['name']
                if field['name'] == 'Analysis Comments':
                    try:
                        defect.analysis_comments = self.clean_wiki_text(field['value'])
                    except:
                        defect.analysis_comments = ''
                if field['name'] == 'Validation Comments':
                    try:
                        defect.validation_comments = self.clean_wiki_text(field['value'])
                    except:
                        defect.validation_comments = ''

            try:
                defect.team = item['teams'][0]['name']
            except Exception as e:
                defect.team = ''
            try:
                defect.priority = item['priority']['name']
            except Exception as e:
                defect.priority = ''
            defect.owner_email = ",".join(self.get_email(_item['name'])[1] for _item in item['owners'] if self.get_email(_item['name']))
            defect.owner = ",".join(self.get_email(_item['name'])[0] for _item in item['owners'] if self.get_email(_item['name']))
            defect.submitted_by_email = self.get_email(item['createdBy']['name'])[1]
            defect.submitted_by = self.get_email(item['createdBy']['name'])[0]
            defect.submitted_at = self.convert_iso_to_unix(item['createdAt']) + 28800000 * 2
            defect_list.append(defect)
        return defect_list

    def get_projects(self):
        if self.client.is_authenticated() or self.client.authenticate():
            try:
                project_lists = self.client.get_json("projects")
                self.signal_projects.emit(project_lists)
            except Exception as e:
                logger.error(f"获取项目失败，{e}")