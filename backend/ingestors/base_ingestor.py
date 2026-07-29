"""Template that every feed ingestor follows: `fetch()` pulls raw data
from the upstream API, `normalize()` converts it to Threat-shaped dicts,
and `run()` wires the two together so a single ingestor failure can
never take down the whole scheduled job.
"""
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class BaseIngestor(ABC):
    source_name: str = "unknown"

    @abstractmethod
    def fetch(self) -> Any:
        """Retrieve raw data from the upstream feed. Raise on failure --
        `run()` is responsible for catching it, not this method.
        """
        raise NotImplementedError

    @abstractmethod
    def normalize(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Convert raw upstream data into a list of Threat-shaped dicts
        (see services.normalization_service.build_threat_dict).
        """
        raise NotImplementedError

    def run(self) -> List[Dict[str, Any]]:
        """Fetch + normalize, isolating failures at each step so one bad
        feed (timeout, malformed response, missing API key) can't crash
        the other two scheduled jobs.
        """
        try:
            raw_data = self.fetch()
        except Exception:
            logger.exception("[%s] fetch failed", self.source_name)
            return []

        try:
            threats = self.normalize(raw_data)
        except Exception:
            logger.exception("[%s] normalization failed", self.source_name)
            return []

        logger.info("[%s] produced %d normalized indicators", self.source_name, len(threats))
        return threats
