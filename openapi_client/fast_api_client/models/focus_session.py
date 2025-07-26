import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="FocusSession")


@_attrs_define
class FocusSession:
    """
    Attributes:
        start_time (datetime.datetime):
        end_time (datetime.datetime):
        id (int):
        task_id (int):
        completed (Union[Unset, bool]):  Default: False.
    """

    start_time: datetime.datetime
    end_time: datetime.datetime
    id: int
    task_id: int
    completed: Union[Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        start_time = self.start_time.isoformat()

        end_time = self.end_time.isoformat()

        id = self.id

        task_id = self.task_id

        completed = self.completed

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "start_time": start_time,
                "end_time": end_time,
                "id": id,
                "task_id": task_id,
            }
        )
        if completed is not UNSET:
            field_dict["completed"] = completed

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        start_time = isoparse(d.pop("start_time"))

        end_time = isoparse(d.pop("end_time"))

        id = d.pop("id")

        task_id = d.pop("task_id")

        completed = d.pop("completed", UNSET)

        focus_session = cls(
            start_time=start_time,
            end_time=end_time,
            id=id,
            task_id=task_id,
            completed=completed,
        )

        focus_session.additional_properties = d
        return focus_session

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
