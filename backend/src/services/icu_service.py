"""
Intervals.icu API service.

Auth: HTTP Basic with username "API_KEY" and password = athlete API key.
Docs: https://forum.intervals.icu/t/api-access-to-intervals-icu/609
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx


ICU_BASE_URL = "https://intervals.icu/api/v1"


class IcuService:
    """Thin client for Intervals.icu REST API."""

    def __init__(self, base_url: str = ICU_BASE_URL, timeout: float = 60.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _auth(self, api_key: str) -> httpx.BasicAuth:
        return httpx.BasicAuth("API_KEY", api_key)

    def _athlete_path(self, athlete_id: Optional[str]) -> str:
        # "0" means the athlete owning the API key
        aid = athlete_id if athlete_id not in (None, "") else "0"
        return f"{self.base_url}/athlete/{aid}"

    async def test_connection(self, api_key: str, athlete_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate API key by fetching the athlete profile.

        Returns:
            Athlete dict from ICU (includes id, name, etc.)

        Raises:
            ValueError on auth / API errors
        """
        url = self._athlete_path(athlete_id)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, auth=self._auth(api_key))

        if response.status_code in (401, 403):
            raise ValueError("Intervals.icu API key is invalid or missing CALENDAR scope.")
        if response.status_code >= 400:
            raise ValueError(f"Intervals.icu error ({response.status_code}): {response.text[:300]}")

        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("Unexpected athlete response from Intervals.icu")
        return data

    async def upsert_events_bulk(
        self,
        api_key: str,
        events: List[Dict[str, Any]],
        athlete_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Create/update calendar events via bulk upsert.

        Uses external_id for matching when upsert=true.
        Note: ICU documents upsert matching for OAuth clients; API key may
        still create/update by external_id depending on ICU version — we
        always send upsert=true and external_id.
        """
        if not events:
            return []

        url = f"{self._athlete_path(athlete_id)}/events/bulk"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url,
                params={"upsert": "true"},
                json=events,
                auth=self._auth(api_key),
                headers={"Content-Type": "application/json"},
            )

        if response.status_code in (401, 403):
            raise ValueError("Intervals.icu rejected the request (auth). Check API key and scopes.")
        if response.status_code >= 400:
            raise ValueError(f"Intervals.icu bulk upsert failed ({response.status_code}): {response.text[:500]}")

        data = response.json()
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "events" in data:
            return data["events"]
        return [data] if data else []

    async def list_events(
        self,
        api_key: str,
        oldest: str,
        newest: str,
        athlete_id: Optional[str] = None,
        category: str = "WORKOUT",
    ) -> List[Dict[str, Any]]:
        """
        List calendar events in a local-date range (inclusive).

        Args:
            oldest / newest: yyyy-MM-dd local dates
            category: ICU category filter (default WORKOUT)
        """
        url = f"{self._athlete_path(athlete_id)}/events"
        params: Dict[str, Any] = {"oldest": oldest, "newest": newest}
        if category:
            params["category"] = category

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params, auth=self._auth(api_key))

        if response.status_code in (401, 403):
            raise ValueError("Intervals.icu rejected the request (auth). Check API key and scopes.")
        if response.status_code >= 400:
            raise ValueError(f"Intervals.icu list events failed ({response.status_code}): {response.text[:500]}")

        data = response.json()
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "events" in data:
            return data["events"] or []
        return []

    async def delete_events_bulk(
        self,
        api_key: str,
        events: List[Dict[str, Any]],
        athlete_id: Optional[str] = None,
    ) -> int:
        """
        Delete calendar events by id and/or external_id.

        Body items: {"id": ...} and/or {"external_id": "..."}.
        Missing events are ignored. Returns count actually deleted.
        """
        if not events:
            return 0

        url = f"{self._athlete_path(athlete_id)}/events/bulk-delete"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.put(
                url,
                json=events,
                auth=self._auth(api_key),
                headers={"Content-Type": "application/json"},
            )

        if response.status_code in (401, 403):
            raise ValueError("Intervals.icu rejected the request (auth). Check API key and scopes.")
        if response.status_code >= 400:
            raise ValueError(f"Intervals.icu bulk delete failed ({response.status_code}): {response.text[:500]}")

        data = response.json()
        if isinstance(data, int):
            return data
        if isinstance(data, dict):
            deleted = data.get("deleted")
            if isinstance(deleted, int):
                return deleted
            return int(deleted) if deleted is not None else 0
        return 0


icu_service = IcuService()
