"""
Context Loader
Load bank-defined context cards and expose them as structured objects for PAM.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _parse_date(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            logger.warning(f"Unable to parse date value '{value}'")
            return None


@dataclass
class ContextCard:
    id: str
    name: str
    focus_area: str
    priority: int
    time_frame: Dict[str, Any] = field(default_factory=dict)
    incentive: Optional[str] = None
    description: str = ""
    eligibility: Dict[str, Any] = field(default_factory=dict)
    status: str = "active"
    tags: List[str] = field(default_factory=list)

    def is_active(self, reference_time: Optional[datetime] = None) -> bool:
        now = reference_time or datetime.utcnow()
        status_lower = (self.status or "").lower()

        if status_lower not in {"active", "scheduled"}:
            return False

        start = _parse_date(self.time_frame.get("start_date"))
        end = _parse_date(self.time_frame.get("end_date"))
        open_ended = self.time_frame.get("open_ended", False)

        if start and now < start:
            return False

        if end and now > end:
            return False

        if open_ended:
            return status_lower == "active"

        # Scheduled contexts become active when timeframe permits
        return True

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "ContextCard":
        context_id = raw.get("id") or raw.get("name", "untitled").strip().lower().replace(" ", "_")
        priority = raw.get("priority", 100)
        try:
            priority = int(priority)
        except (TypeError, ValueError):
            priority = 100

        return cls(
            id=context_id,
            name=raw.get("name", context_id),
            focus_area=raw.get("focus_area", ""),
            priority=priority,
            time_frame=raw.get("time_frame", {}),
            incentive=raw.get("incentive"),
            description=raw.get("description", ""),
            eligibility=raw.get("eligibility", {}),
            status=raw.get("status", "active"),
            tags=raw.get("tags", [])
        )


class ContextLoader:
    """
    Loads context card definitions from a JSON file and exposes them as structured objects.
    """

    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.contexts = self._load_contexts()

    def _load_contexts(self) -> List[ContextCard]:
        if not self.config_path.exists():
            logger.warning(f"Context file not found: {self.config_path}")
            return []

        try:
            with self.config_path.open("r", encoding="utf-8") as f:
                raw_contexts = json.load(f)
        except Exception as exc:
            logger.error(f"Failed to load contexts: {exc}")
            return []

        return self._parse(raw_contexts)

    def _parse(self, raw_contexts: List[Dict[str, Any]]) -> List[ContextCard]:
        contexts = []
        for entry in raw_contexts:
            try:
                contexts.append(ContextCard.from_dict(entry))
            except Exception as exc:
                logger.warning(f"Skipping invalid context entry: {exc}")

        return sorted(contexts, key=lambda ctx: ctx.priority)

    def reload(self) -> None:
        """Reload contexts from disk."""
        self.contexts = self._load_contexts()

    def get_contexts(self) -> List[ContextCard]:
        return self.contexts

    @staticmethod
    def parse_context_dicts(raw_contexts: List[Dict[str, Any]]) -> List[ContextCard]:
        return sorted(
            [ContextCard.from_dict(entry) for entry in raw_contexts],
            key=lambda ctx: ctx.priority
        )

