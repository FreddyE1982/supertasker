import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="PlanTaskCreate")


@_attrs_define
class PlanTaskCreate:
    """
    Attributes:
        title (str):
        estimated_difficulty (int):
        estimated_duration_minutes (int):
        due_date (datetime.date):
        description (Union[None, Unset, str]):
        priority (Union[Unset, int]):  Default: 3.
        category_id (Union[None, Unset, int]):
        high_energy_start_hour (Union[None, Unset, int]):
        high_energy_end_hour (Union[None, Unset, int]):
        fatigue_break_factor (Union[None, Unset, float]):
        energy_curve (Union[None, Unset, list[int]]):
        energy_day_order_weight (Union[None, Unset, float]):
        category_day_weight (Union[None, Unset, float]):
        transition_buffer_minutes (Union[None, Unset, int]):
        intelligent_transition_buffer (Union[None, Unset, bool]):
        productivity_history_weight (Union[None, Unset, float]):
        productivity_half_life_days (Union[None, Unset, int]):
        category_productivity_weight (Union[None, Unset, float]):
        spaced_repetition_factor (Union[None, Unset, float]):
        session_count_weight (Union[None, Unset, float]):
        difficulty_load_weight (Union[None, Unset, float]):
        energy_load_weight (Union[None, Unset, float]):
    """

    title: str
    estimated_difficulty: int
    estimated_duration_minutes: int
    due_date: datetime.date
    description: Union[None, Unset, str] = UNSET
    priority: Union[Unset, int] = 3
    category_id: Union[None, Unset, int] = UNSET
    high_energy_start_hour: Union[None, Unset, int] = UNSET
    high_energy_end_hour: Union[None, Unset, int] = UNSET
    fatigue_break_factor: Union[None, Unset, float] = UNSET
    energy_curve: Union[None, Unset, list[int]] = UNSET
    energy_day_order_weight: Union[None, Unset, float] = UNSET
    category_day_weight: Union[None, Unset, float] = UNSET
    transition_buffer_minutes: Union[None, Unset, int] = UNSET
    intelligent_transition_buffer: Union[None, Unset, bool] = UNSET
    productivity_history_weight: Union[None, Unset, float] = UNSET
    productivity_half_life_days: Union[None, Unset, int] = UNSET
    category_productivity_weight: Union[None, Unset, float] = UNSET
    spaced_repetition_factor: Union[None, Unset, float] = UNSET
    session_count_weight: Union[None, Unset, float] = UNSET
    difficulty_load_weight: Union[None, Unset, float] = UNSET
    energy_load_weight: Union[None, Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        estimated_difficulty = self.estimated_difficulty

        estimated_duration_minutes = self.estimated_duration_minutes

        due_date = self.due_date.isoformat()

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        priority = self.priority

        category_id: Union[None, Unset, int]
        if isinstance(self.category_id, Unset):
            category_id = UNSET
        else:
            category_id = self.category_id

        high_energy_start_hour: Union[None, Unset, int]
        if isinstance(self.high_energy_start_hour, Unset):
            high_energy_start_hour = UNSET
        else:
            high_energy_start_hour = self.high_energy_start_hour

        high_energy_end_hour: Union[None, Unset, int]
        if isinstance(self.high_energy_end_hour, Unset):
            high_energy_end_hour = UNSET
        else:
            high_energy_end_hour = self.high_energy_end_hour

        fatigue_break_factor: Union[None, Unset, float]
        if isinstance(self.fatigue_break_factor, Unset):
            fatigue_break_factor = UNSET
        else:
            fatigue_break_factor = self.fatigue_break_factor

        energy_curve: Union[None, Unset, list[int]]
        if isinstance(self.energy_curve, Unset):
            energy_curve = UNSET
        elif isinstance(self.energy_curve, list):
            energy_curve = self.energy_curve

        else:
            energy_curve = self.energy_curve

        energy_day_order_weight: Union[None, Unset, float]
        if isinstance(self.energy_day_order_weight, Unset):
            energy_day_order_weight = UNSET
        else:
            energy_day_order_weight = self.energy_day_order_weight

        category_day_weight: Union[None, Unset, float]
        if isinstance(self.category_day_weight, Unset):
            category_day_weight = UNSET
        else:
            category_day_weight = self.category_day_weight

        transition_buffer_minutes: Union[None, Unset, int]
        if isinstance(self.transition_buffer_minutes, Unset):
            transition_buffer_minutes = UNSET
        else:
            transition_buffer_minutes = self.transition_buffer_minutes

        intelligent_transition_buffer: Union[None, Unset, bool]
        if isinstance(self.intelligent_transition_buffer, Unset):
            intelligent_transition_buffer = UNSET
        else:
            intelligent_transition_buffer = self.intelligent_transition_buffer

        productivity_history_weight: Union[None, Unset, float]
        if isinstance(self.productivity_history_weight, Unset):
            productivity_history_weight = UNSET
        else:
            productivity_history_weight = self.productivity_history_weight

        productivity_half_life_days: Union[None, Unset, int]
        if isinstance(self.productivity_half_life_days, Unset):
            productivity_half_life_days = UNSET
        else:
            productivity_half_life_days = self.productivity_half_life_days

        category_productivity_weight: Union[None, Unset, float]
        if isinstance(self.category_productivity_weight, Unset):
            category_productivity_weight = UNSET
        else:
            category_productivity_weight = self.category_productivity_weight

        spaced_repetition_factor: Union[None, Unset, float]
        if isinstance(self.spaced_repetition_factor, Unset):
            spaced_repetition_factor = UNSET
        else:
            spaced_repetition_factor = self.spaced_repetition_factor

        session_count_weight: Union[None, Unset, float]
        if isinstance(self.session_count_weight, Unset):
            session_count_weight = UNSET
        else:
            session_count_weight = self.session_count_weight

        difficulty_load_weight: Union[None, Unset, float]
        if isinstance(self.difficulty_load_weight, Unset):
            difficulty_load_weight = UNSET
        else:
            difficulty_load_weight = self.difficulty_load_weight

        energy_load_weight: Union[None, Unset, float]
        if isinstance(self.energy_load_weight, Unset):
            energy_load_weight = UNSET
        else:
            energy_load_weight = self.energy_load_weight

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "title": title,
                "estimated_difficulty": estimated_difficulty,
                "estimated_duration_minutes": estimated_duration_minutes,
                "due_date": due_date,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if priority is not UNSET:
            field_dict["priority"] = priority
        if category_id is not UNSET:
            field_dict["category_id"] = category_id
        if high_energy_start_hour is not UNSET:
            field_dict["high_energy_start_hour"] = high_energy_start_hour
        if high_energy_end_hour is not UNSET:
            field_dict["high_energy_end_hour"] = high_energy_end_hour
        if fatigue_break_factor is not UNSET:
            field_dict["fatigue_break_factor"] = fatigue_break_factor
        if energy_curve is not UNSET:
            field_dict["energy_curve"] = energy_curve
        if energy_day_order_weight is not UNSET:
            field_dict["energy_day_order_weight"] = energy_day_order_weight
        if category_day_weight is not UNSET:
            field_dict["category_day_weight"] = category_day_weight
        if transition_buffer_minutes is not UNSET:
            field_dict["transition_buffer_minutes"] = transition_buffer_minutes
        if intelligent_transition_buffer is not UNSET:
            field_dict["intelligent_transition_buffer"] = intelligent_transition_buffer
        if productivity_history_weight is not UNSET:
            field_dict["productivity_history_weight"] = productivity_history_weight
        if productivity_half_life_days is not UNSET:
            field_dict["productivity_half_life_days"] = productivity_half_life_days
        if category_productivity_weight is not UNSET:
            field_dict["category_productivity_weight"] = category_productivity_weight
        if spaced_repetition_factor is not UNSET:
            field_dict["spaced_repetition_factor"] = spaced_repetition_factor
        if session_count_weight is not UNSET:
            field_dict["session_count_weight"] = session_count_weight
        if difficulty_load_weight is not UNSET:
            field_dict["difficulty_load_weight"] = difficulty_load_weight
        if energy_load_weight is not UNSET:
            field_dict["energy_load_weight"] = energy_load_weight

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        title = d.pop("title")

        estimated_difficulty = d.pop("estimated_difficulty")

        estimated_duration_minutes = d.pop("estimated_duration_minutes")

        due_date = isoparse(d.pop("due_date")).date()

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        priority = d.pop("priority", UNSET)

        def _parse_category_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        category_id = _parse_category_id(d.pop("category_id", UNSET))

        def _parse_high_energy_start_hour(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        high_energy_start_hour = _parse_high_energy_start_hour(d.pop("high_energy_start_hour", UNSET))

        def _parse_high_energy_end_hour(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        high_energy_end_hour = _parse_high_energy_end_hour(d.pop("high_energy_end_hour", UNSET))

        def _parse_fatigue_break_factor(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        fatigue_break_factor = _parse_fatigue_break_factor(d.pop("fatigue_break_factor", UNSET))

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

        def _parse_energy_day_order_weight(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        energy_day_order_weight = _parse_energy_day_order_weight(d.pop("energy_day_order_weight", UNSET))

        def _parse_category_day_weight(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        category_day_weight = _parse_category_day_weight(d.pop("category_day_weight", UNSET))

        def _parse_transition_buffer_minutes(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        transition_buffer_minutes = _parse_transition_buffer_minutes(d.pop("transition_buffer_minutes", UNSET))

        def _parse_intelligent_transition_buffer(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        intelligent_transition_buffer = _parse_intelligent_transition_buffer(
            d.pop("intelligent_transition_buffer", UNSET)
        )

        def _parse_productivity_history_weight(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        productivity_history_weight = _parse_productivity_history_weight(d.pop("productivity_history_weight", UNSET))

        def _parse_productivity_half_life_days(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        productivity_half_life_days = _parse_productivity_half_life_days(d.pop("productivity_half_life_days", UNSET))

        def _parse_category_productivity_weight(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        category_productivity_weight = _parse_category_productivity_weight(d.pop("category_productivity_weight", UNSET))

        def _parse_spaced_repetition_factor(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        spaced_repetition_factor = _parse_spaced_repetition_factor(d.pop("spaced_repetition_factor", UNSET))

        def _parse_session_count_weight(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        session_count_weight = _parse_session_count_weight(d.pop("session_count_weight", UNSET))

        def _parse_difficulty_load_weight(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        difficulty_load_weight = _parse_difficulty_load_weight(d.pop("difficulty_load_weight", UNSET))

        def _parse_energy_load_weight(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        energy_load_weight = _parse_energy_load_weight(d.pop("energy_load_weight", UNSET))

        plan_task_create = cls(
            title=title,
            estimated_difficulty=estimated_difficulty,
            estimated_duration_minutes=estimated_duration_minutes,
            due_date=due_date,
            description=description,
            priority=priority,
            category_id=category_id,
            high_energy_start_hour=high_energy_start_hour,
            high_energy_end_hour=high_energy_end_hour,
            fatigue_break_factor=fatigue_break_factor,
            energy_curve=energy_curve,
            energy_day_order_weight=energy_day_order_weight,
            category_day_weight=category_day_weight,
            transition_buffer_minutes=transition_buffer_minutes,
            intelligent_transition_buffer=intelligent_transition_buffer,
            productivity_history_weight=productivity_history_weight,
            productivity_half_life_days=productivity_half_life_days,
            category_productivity_weight=category_productivity_weight,
            spaced_repetition_factor=spaced_repetition_factor,
            session_count_weight=session_count_weight,
            difficulty_load_weight=difficulty_load_weight,
            energy_load_weight=energy_load_weight,
        )

        plan_task_create.additional_properties = d
        return plan_task_create

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
