from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.appointment import Appointment
from ...models.appointment_update import AppointmentUpdate
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    appointment_id: int,
    *,
    body: AppointmentUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/appointments/{appointment_id}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Appointment, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = Appointment.from_dict(response.json())

        return response_200
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Appointment, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    appointment_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: AppointmentUpdate,
) -> Response[Union[Appointment, HTTPValidationError]]:
    """Update Appointment

    Args:
        appointment_id (int):
        body (AppointmentUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Appointment, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        appointment_id=appointment_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    appointment_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: AppointmentUpdate,
) -> Optional[Union[Appointment, HTTPValidationError]]:
    """Update Appointment

    Args:
        appointment_id (int):
        body (AppointmentUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Appointment, HTTPValidationError]
    """

    return sync_detailed(
        appointment_id=appointment_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    appointment_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: AppointmentUpdate,
) -> Response[Union[Appointment, HTTPValidationError]]:
    """Update Appointment

    Args:
        appointment_id (int):
        body (AppointmentUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Appointment, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        appointment_id=appointment_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    appointment_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: AppointmentUpdate,
) -> Optional[Union[Appointment, HTTPValidationError]]:
    """Update Appointment

    Args:
        appointment_id (int):
        body (AppointmentUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Appointment, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            appointment_id=appointment_id,
            client=client,
            body=body,
        )
    ).parsed
