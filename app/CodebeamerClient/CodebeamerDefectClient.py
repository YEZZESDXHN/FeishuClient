import logging

from PySide6.QtCore import QObject, Signal

from app.CodebeamerClient.CodebeamerClient import CodebeamerClient
from app.user_data import CodeBeamerDefect

logger = logging.getLogger('FeishuClient.' + __name__)


class QCodebeamerDefectClient(QObject, CodebeamerClient):
    signal_projects = Signal(object)
    def __init__(self, username, password):
        super().__init__(username=username, password=password)

    def convert_defect_items(self, items) -> list[CodeBeamerDefect]:
        defect_list = []
        for item in items:
            defect = CodeBeamerDefect()
            defect.defect_id = item['id']
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

    def get_projects(self):
        if self.client._authenticated or self.client.authenticate():
            try:
                project_lists = self.client.get_json("projects")
                self.signal_projects.emit(project_lists)
            except Exception as e:
                logger.error(f"获取项目失败，{e}")