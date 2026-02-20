from typing import TypedDict, Optional
from api.models.departments import Department
from datetime import datetime


class DepartmentData(TypedDict):
    name: str
    parent: Optional[Department]
    created_at: datetime
