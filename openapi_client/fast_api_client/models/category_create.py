from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CategoryCreate")


@_attrs_define
class CategoryCreate:
    """
    Attributes:
        name (str):
        color (str):
        preferred_start_hour (Union[None, Unset, int]):
        preferred_end_hour (Union[None, Unset, int]):
        energy_curve (Union[None, Unset, list[int]]):
    """

    name: str
    color: str
    preferred_start_hour: Union[None, Unset, int] = UNSET
    preferred_end_hour: Union[None, Unset, int] = UNSET
    energy_curve: Union[None, Unset, list[int]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        color = self.color

        preferred_start_hour: Union[None, Unset, int]
        if isinstance(self.preferred_start_hour, Unset):
            preferred_start_hour = UNSET
        else:
            preferred_start_hour = self.preferred_start_hour

        preferred_end_hour: Union[None, Unset, int]
        if isinstance(self.preferred_end_hour, Unset):
            preferred_end_hour = UNSET
        else:
            preferred_end_hour = self.preferred_end_hour

        energy_curve: Union[None, Unset, list[int]]
        if isinstance(self.energy_curve, Unset):
            energy_curve = UNSET
        elif isinstance(self.energy_curve, list):
            energy_curve = self.energy_curve

        else:
            energy_curve = self.energy_curve

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "color": color,
            }
        )
        if preferred_start_hour is not UNSET:
            field_dict["preferred_start_hour"] = preferred_start_hour
        if preferred_end_hour is not UNSET:
            field_dict["preferred_end_hour"] = preferred_end_hour
        if energy_curve is not UNSET:
            field_dict["energy_curve"] = energy_curve

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        color = d.pop("color")

        def _parse_preferred_start_hour(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        preferred_start_hour = _parse_preferred_start_hour(d.pop("preferred_start_hour", UNSET))

        def _parse_preferred_end_hour(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        preferred_end_hour = _parse_preferred_end_hour(d.pop("preferred_end_hour", UNSET))

        def _parse_energy_curve(data: object) -> Union[None, Unset, list[int]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                energy_curve_type_0 = cast(list[int], data)

                return energy_curve_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[int]], data)

        energy_curve = _parse_energy_curve(d.pop("energy_curve", UNSET))

        category_create = cls(
            name=name,
            color=color,
            preferred_start_hour=preferred_start_hour,
            preferred_end_hour=preferred_end_hour,
            energy_curve=energy_curve,
        )

        category_create.additional_properties = d
        return category_create

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
