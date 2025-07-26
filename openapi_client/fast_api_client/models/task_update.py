import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="TaskUpdate")


@_attrs_define
class TaskUpdate:
    """
    Attributes:
        title (str):
        due_date (datetime.date):
        description (Union[None, Unset, str]):
        start_date (Union[None, Unset, datetime.date]):
        end_date (Union[None, Unset, datetime.date]):
        start_time (Union[None, Unset, str]):
        end_time (Union[None, Unset, str]):
        category_id (Union[None, Unset, int]):
        perceived_difficulty (Union[None, Unset, int]):
        estimated_difficulty (Union[None, Unset, int]):
        estimated_duration_minutes (Union[None, Unset, int]):
        priority (Union[Unset, int]):  Default: 3.
        worked_on (Union[Unset, bool]):  Default: False.
        paused (Union[Unset, bool]):  Default: False.
    """

    title: str
    due_date: datetime.date
    description: Union[None, Unset, str] = UNSET
    start_date: Union[None, Unset, datetime.date] = UNSET
    end_date: Union[None, Unset, datetime.date] = UNSET
    start_time: Union[None, Unset, str] = UNSET
    end_time: Union[None, Unset, str] = UNSET
    category_id: Union[None, Unset, int] = UNSET
    perceived_difficulty: Union[None, Unset, int] = UNSET
    estimated_difficulty: Union[None, Unset, int] = UNSET
    estimated_duration_minutes: Union[None, Unset, int] = UNSET
    priority: Union[Unset, int] = 3
    worked_on: Union[Unset, bool] = False
    paused: Union[Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        due_date = self.due_date.isoformat()

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        start_date: Union[None, Unset, str]
        if isinstance(self.start_date, Unset):
            start_date = UNSET
        elif isinstance(self.start_date, datetime.date):
            start_date = self.start_date.isoformat()
        else:
            start_date = self.start_date

        end_date: Union[None, Unset, str]
        if isinstance(self.end_date, Unset):
            end_date = UNSET
        elif isinstance(self.end_date, datetime.date):
            end_date = self.end_date.isoformat()
        else:
            end_date = self.end_date

        start_time: Union[None, Unset, str]
        if isinstance(self.start_time, Unset):
            start_time = UNSET
        else:
            start_time = self.start_time

        end_time: Union[None, Unset, str]
        if isinstance(self.end_time, Unset):
            end_time = UNSET
        else:
            end_time = self.end_time

        category_id: Union[None, Unset, int]
        if isinstance(self.category_id, Unset):
            category_id = UNSET
        else:
            category_id = self.category_id

        perceived_difficulty: Union[None, Unset, int]
        if isinstance(self.perceived_difficulty, Unset):
            perceived_difficulty = UNSET
        else:
            perceived_difficulty = self.perceived_difficulty

        estimated_difficulty: Union[None, Unset, int]
        if isinstance(self.estimated_difficulty, Unset):
            estimated_difficulty = UNSET
        else:
            estimated_difficulty = self.estimated_difficulty

        estimated_duration_minutes: Union[None, Unset, int]
        if isinstance(self.estimated_duration_minutes, Unset):
            estimated_duration_minutes = UNSET
        else:
            estimated_duration_minutes = self.estimated_duration_minutes

        priority = self.priority

        worked_on = self.worked_on

        paused = self.paused

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "title": title,
                "due_date": due_date,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if start_date is not UNSET:
            field_dict["start_date"] = start_date
        if end_date is not UNSET:
            field_dict["end_date"] = end_date
        if start_time is not UNSET:
            field_dict["start_time"] = start_time
        if end_time is not UNSET:
            field_dict["end_time"] = end_time
        if category_id is not UNSET:
            field_dict["category_id"] = category_id
        if perceived_difficulty is not UNSET:
            field_dict["perceived_difficulty"] = perceived_difficulty
        if estimated_difficulty is not UNSET:
            field_dict["estimated_difficulty"] = estimated_difficulty
        if estimated_duration_minutes is not UNSET:
            field_dict["estimated_duration_minutes"] = estimated_duration_minutes
        if priority is not UNSET:
            field_dict["priority"] = priority
        if worked_on is not UNSET:
            field_dict["worked_on"] = worked_on
        if paused is not UNSET:
            field_dict["paused"] = paused

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        title = d.pop("title")

        due_date = isoparse(d.pop("due_date")).date()

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_start_date(data: object) -> Union[None, Unset, datetime.date]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                start_date_type_0 = isoparse(data).date()

                return start_date_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.date], data)

        start_date = _parse_start_date(d.pop("start_date", UNSET))

        def _parse_end_date(data: object) -> Union[None, Unset, datetime.date]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                end_date_type_0 = isoparse(data).date()

                return end_date_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.date], data)

        end_date = _parse_end_date(d.pop("end_date", UNSET))

        def _parse_start_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        start_time = _parse_start_time(d.pop("start_time", UNSET))

        def _parse_end_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        end_time = _parse_end_time(d.pop("end_time", UNSET))

        def _parse_category_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        category_id = _parse_category_id(d.pop("category_id", UNSET))

        def _parse_perceived_difficulty(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        perceived_difficulty = _parse_perceived_difficulty(d.pop("perceived_difficulty", UNSET))

        def _parse_estimated_difficulty(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        estimated_difficulty = _parse_estimated_difficulty(d.pop("estimated_difficulty", UNSET))

        def _parse_estimated_duration_minutes(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        estimated_duration_minutes = _parse_estimated_duration_minutes(d.pop("estimated_duration_minutes", UNSET))

        priority = d.pop("priority", UNSET)

        worked_on = d.pop("worked_on", UNSET)

        paused = d.pop("paused", UNSET)

        task_update = cls(
            title=title,
            due_date=due_date,
            description=description,
            start_date=start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time,
            category_id=category_id,
            perceived_difficulty=perceived_difficulty,
            estimated_difficulty=estimated_difficulty,
            estimated_duration_minutes=estimated_duration_minutes,
            priority=priority,
            worked_on=worked_on,
            paused=paused,
        )

        task_update.additional_properties = d
        return task_update

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
