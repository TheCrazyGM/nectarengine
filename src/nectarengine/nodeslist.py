"""Utilities for working with the Hive Engine node benchmark metadata."""

import json
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence

import requests
from nectar import Hive
from nectar.account import Account

_DEFAULT_ACCOUNT = "flowerengine"
_DEFAULT_HIVE_NODES: Sequence[str] = ("https://api.hive.blog",)
_BEACON_HE_NODES_URL = "https://beacon.peakd.com/api/he/nodes"
_BEACON_HE_HISTORY_NODES_URL = "https://beacon.peakd.com/api/heh/nodes"

NodeUrlList = List[str]


@dataclass(order=True)
class Node:
    """Represents a Hive Engine node sourced from FlowerEngine metadata."""

    rank: float
    url: str = field(compare=False)
    data: Dict[str, Any] = field(default_factory=dict, compare=False)
    failing_cause: Optional[str] = field(default=None, compare=False)

    def __post_init__(self) -> None:
        cleaned_url = self.url.strip()
        if not cleaned_url:
            raise ValueError("Node url cannot be empty")
        self.url = self._ensure_trailing_slash(cleaned_url)

    def as_url(self) -> str:
        """Return the node endpoint as a normalized URL."""

        return self.url

    def __str__(self) -> str:
        return self.url

    @staticmethod
    def _ensure_trailing_slash(url: str) -> str:
        normalized = url.rstrip("/")
        return f"{normalized}/"


class Nodes(Sequence[Node]):
    """Convenience accessor for FlowerEngine node benchmarks."""

    def __init__(
        self,
        username: str = _DEFAULT_ACCOUNT,
        hive_nodes: Optional[Iterable[str]] = None,
        auto_refresh: bool = True,
    ) -> None:
        self.username = username
        self.hive_nodes: Sequence[str] = tuple(hive_nodes) if hive_nodes else _DEFAULT_HIVE_NODES
        self._nodes: List[Node] = []
        self._raw_metadata: Dict[str, Any] = {}
        if auto_refresh:
            self.refresh()

    def refresh(self) -> List[Node]:
        """Reload the node list from the FlowerEngine account metadata."""

        metadata = self._load_metadata()
        self._nodes = self._build_nodes(metadata)
        self._raw_metadata = metadata
        return list(self._nodes)

    def beacon(
        self,
        limit: Optional[int] = None,
        url: str = _BEACON_HE_NODES_URL,
        timeout: int = 15,
    ) -> List[Node]:
        """Fetch Hive Engine nodes from the PeakD Beacon API."""

        return self._fetch_beacon_nodes(url=url, limit=limit, timeout=timeout)

    def beacon_history(
        self,
        limit: Optional[int] = None,
        url: str = _BEACON_HE_HISTORY_NODES_URL,
        timeout: int = 15,
    ) -> List[Node]:
        """Fetch Hive Engine history nodes from the PeakD Beacon API."""

        return self._fetch_beacon_nodes(url=url, limit=limit, timeout=timeout)

    def node_list(self) -> List[Node]:
        """Return the currently cached node list, refreshing if empty."""

        if not self._nodes:
            self.refresh()
        return list(self._nodes)

    def fastest(self, limit: int = 1) -> List[Node]:
        """Return the fastest nodes according to the benchmark ranking."""

        nodes = self.node_list()
        if limit <= 0:
            return []
        return nodes[:limit] if limit < len(nodes) else nodes

    def as_urls(self, limit: Optional[int] = None) -> NodeUrlList:
        """Provide the node URLs, optionally truncated to *limit* entries."""

        nodes = self.node_list()
        if limit is not None:
            nodes = nodes[:limit]
        return [node.as_url() for node in nodes]

    def primary_url(self) -> Optional[str]:
        """Return the highest-ranked node URL or ``None`` if unavailable."""

        nodes = self.node_list()
        return nodes[0].as_url() if nodes else None

    @property
    def raw_metadata(self) -> Dict[str, Any]:
        """Expose the latest raw metadata payload."""

        return dict(self._raw_metadata)

    def __len__(self) -> int:
        return len(self.node_list())

    def __getitem__(self, index: int) -> Node:
        return self.node_list()[index]

    def __iter__(self) -> Iterator[Node]:
        return iter(self.node_list())

    def _load_metadata(self) -> Dict[str, Any]:
        hv = Hive(node=self.hive_nodes)
        account = Account(self.username, blockchain_instance=hv)
        metadata = account.json_metadata
        if not metadata:
            return {}
        if isinstance(metadata, str):
            try:
                return json.loads(metadata)
            except json.JSONDecodeError:
                return {}
        if isinstance(metadata, dict):
            return metadata
        return {}

    @staticmethod
    def _build_nodes(metadata: Dict[str, Any]) -> List[Node]:
        report_entries = metadata.get("report", []) if isinstance(metadata, dict) else []
        failing_nodes = metadata.get("failing_nodes", {}) if isinstance(metadata, dict) else {}

        nodes: List[Node] = []
        for entry in report_entries:
            if not isinstance(entry, dict):
                continue
            node_url = entry.get("node")
            if not node_url or not isinstance(node_url, str):
                continue
            rank = _calculate_overall_rank(entry)
            nodes.append(
                Node(
                    rank=rank,
                    url=node_url,
                    data=entry,
                    failing_cause=failing_nodes.get(node_url),
                )
            )
        nodes.sort()
        return nodes

    def _fetch_beacon_nodes(self, url: str, limit: Optional[int], timeout: int) -> List[Node]:
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise RuntimeError(f"Unable to reach beacon service: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise RuntimeError("Beacon API returned invalid JSON payload") from exc

        if not isinstance(payload, list):
            raise RuntimeError("Beacon API returned unexpected structure; expected list")

        beacon_nodes: List[Node] = []
        for entry in payload:
            if not isinstance(entry, dict):
                continue
            endpoint = entry.get("endpoint")
            if not isinstance(endpoint, str) or not endpoint.strip():
                continue

            score = entry.get("score")
            rank = 100.0
            if isinstance(score, (int, float)):
                rank = max(0.0, 100.0 - float(score))

            fail_count = entry.get("fail")
            failing_cause = None
            if isinstance(fail_count, (int, float)) and fail_count > 0:
                failing_cause = f"{int(fail_count)} failed health checks"

            beacon_nodes.append(
                Node(
                    rank=rank,
                    url=endpoint,
                    data=entry,
                    failing_cause=failing_cause,
                )
            )

        beacon_nodes.sort()
        if limit is not None:
            if limit <= 0:
                return []
            return beacon_nodes[:limit]
        return beacon_nodes


def _calculate_overall_rank(node_data: Dict[str, Any]) -> float:
    """Replicate engine_bench ranking logic for consistent ordering."""

    if not node_data.get("engine", False) or node_data.get("SSCnodeVersion", "") == "unknown":
        return 999.0

    failed_ops = 0
    ranks: List[float] = []
    for component in ["token", "contract", "account_history", "config", "latency"]:
        section = node_data.get(component, {})
        if not isinstance(section, dict):
            continue
        if not section.get("ok", False):
            failed_ops += 1
        rank_value = section.get("rank")
        if isinstance(rank_value, (int, float)) and rank_value > 0:
            ranks.append(float(rank_value))

    if failed_ops > 2:
        return 900.0

    if ranks:
        avg_rank = sum(ranks) / len(ranks)
        return avg_rank + (failed_ops * 10.0)

    return 950.0
