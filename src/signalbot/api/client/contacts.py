from __future__ import annotations

from typing import TYPE_CHECKING

from signalbot.api.client.base import BaseClient, SectionURIs

if TYPE_CHECKING:
    import aiohttp

    from signalbot.api.outgoing import UpdateContact


class ContactsURIs(SectionURIs):
    def contacts_uri(self) -> str:
        return self._base.http_uri(f"/v1/contacts/{self._base.phone_number}")


class ContactsClient(BaseClient[ContactsURIs]):
    async def update_contact(
        self,
        update_contact: UpdateContact,
    ) -> aiohttp.ClientResponse:
        uri = self._uris.contacts_uri()
        payload = update_contact.model_dump_json(exclude_none=True, by_alias=True)
        return await self._request(
            "put", uri, error_cls=UpdateContactError, payload=payload
        )


class UpdateContactError(Exception):
    pass
