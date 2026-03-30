from enum import IntEnum, Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DefectFieldType(IntEnum):
    text = 0
    int = 1
    people = 2
    Choice = 3
    date = 4


class DefectStatus(str, Enum):
    assigned = 'Assigned'
    submitted = 'Submitted'
    closed = 'Closed'
    planned = 'Planned'
    Analyzed = 'Analyzed'
    Cancelled = 'Cancelled'
    Implemented = 'Implemented'
    Request_Cancellation = 'Request Cancellation'
    Verified = 'Verified'


class CodeBeamerDefect(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    defect_id: int = 0
    status: Optional[str] = ''
    summary: str = ''
    assigned_to: Optional[str] = ''
    assigned_to_email: Optional[str] = ''
    modified_at: Optional[int] = 0
    modified_by: Optional[str] = ''
    modified_by_email: Optional[str] = ''
    fixed_in_release: Optional[str] = ''
    reported_in_release: Optional[str] = ''
    team: Optional[str] = ''
    owner: Optional[str] = ''
    owner_email: Optional[str] = ''
    submitted_by: Optional[str] = ''
    submitted_by_email: Optional[str] = ''
    submitted_at: Optional[int] = 0
    frequency: Optional[str] = ''
    severity: Optional[str] = ''

    def to_json(self) -> str:
        return self.model_dump_json(by_alias=True, exclude_none=True)

    def to_dict(self) -> dict:
        return self.model_dump(by_alias=True, exclude_none=True)

    @field_validator('status', 'summary', 'assigned_to', 'modified_by',
                     'fixed_in_release', 'reported_in_release', 'team',
                     'owner', 'submitted_by', 'frequency', mode='before')
    @classmethod  # <--- 必须加上这个，且放在 field_validator 下面
    def set_null_to_empty(cls, v):
        # 这里的 v 是原始输入值
        return v if v is not None else ''

    @classmethod
    def from_json(cls, json_str: str):
        return cls.model_validate_json(json_str)

    @classmethod
    def from_dict(cls, dict_input: dict):
        return cls.model_validate(dict_input)