from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.focus_session import FocusSession
from ...models.focus_session_create import FocusSessionCreate
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    task_id: int,
    *,
    body: FocusSessionCreate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/tasks/{task_id}/focus_sessions",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[FocusSession, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = FocusSession.from_dict(response.json())

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
) -> Response[Union[FocusSession, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    task_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: FocusSessionCreate,
) -> Response[Union[FocusSession, HTTPValidationError]]:
    """Create Focus Session

    Args:
        task_id (int):
        body (FocusSessionCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[FocusSession, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        task_id=task_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    task_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: FocusSessionCreate,
) -> Optional[Union[FocusSession, HTTPValidationError]]:
    """Create Focus Session

    Args:
        task_id (int):
        body (FocusSessionCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[FocusSession, HTTPValidationError]
    """

    return sync_detailed(
        task_id=task_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    task_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: FocusSessionCreate,
) -> Response[Union[FocusSession, HTTPValidationError]]:
    """Create Focus Session

    Args:
        task_id (int):
        body (FocusSessionCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[FocusSession, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        task_id=task_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    task_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: FocusSessionCreate,
) -> Optional[Union[FocusSession, HTTPValidationError]]:
    """Create Focus Session

    Args:
        task_id (int):
        body (FocusSessionCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[FocusSession, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            task_id=task_id,
            client=client,
            body=body,
        )
    ).parsed
