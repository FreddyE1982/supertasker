import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="Appointment")


@_attrs_define
class Appointment:
    """
    Attributes:
        title (str):
        start_time (datetime.datetime):
        end_time (datetime.datetime):
        id (int):
        description (Union[None, Unset, str]):
        category_id (Union[None, Unset, int]):
    """

    title: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    id: int
    description: Union[None, Unset, str] = UNSET
    category_id: Union[None, Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        start_time = self.start_time.isoformat()

        end_time = self.end_time.isoformat()

        id = self.id

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        category_id: Union[None, Unset, int]
        if isinstance(self.category_id, Unset):
            category_id = UNSET
        else:
            category_id = self.category_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "title": title,
                "start_time": start_time,
                "end_time": end_time,
                "id": id,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if category_id is not UNSET:
            field_dict["category_id"] = category_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        title = d.pop("title")

        start_time = isoparse(d.pop("start_time"))

        end_time = isoparse(d.pop("end_time"))

        id = d.pop("id")

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_category_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        category_id = _parse_category_id(d.pop("category_id", UNSET))

        appointment = cls(
            title=title,
            start_time=start_time,
            end_time=end_time,
            id=id,
            description=description,
            category_id=category_id,
        )

        appointment.additional_properties = d
        return appointment

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
