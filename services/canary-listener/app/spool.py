"""Tiny durable queue (JSON lines on disk) for hits the API couldn't accept.
Single-process, guarded by an asyncio lock; survives container restarts when the
directory is a volume."""
import asyncio
import json
import os
from pathlib import Path


class Spool:
    def __init__(self, directory: str, max_entries: int = 10_000):
        self.path = Path(directory) / "pending.jsonl"
        self.max_entries = max_entries
        self._lock = asyncio.Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _read(self) -> list[str]:
        try:
            return [l for l in self.path.read_text().splitlines() if l.strip()]
        except FileNotFoundError:
            return []

    def _write(self, lines: list[str]) -> None:
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text("".join(l + "\n" for l in lines))
        os.replace(tmp, self.path)

    async def add(self, payload: dict) -> bool:
        """Returns False if the spool is full (hit is dropped)."""
        async with self._lock:
            lines = self._read()
            if len(lines) >= self.max_entries:
                return False
            lines.append(json.dumps(payload, separators=(",", ":")))
            self._write(lines)
            return True

    async def drain(self, send) -> int:
        """Try to deliver every spooled hit; keep those that fail. Returns remaining count."""
        async with self._lock:
            lines = self._read()
            keep: list[str] = []
            for i, line in enumerate(lines):
                try:
                    ok = await send(json.loads(line))
                except Exception:
                    ok = False
                if not ok:
                    keep = lines[i:]  # API still down: stop, preserve order
                    break
            self._write(keep)
            return len(keep)

    def size(self) -> int:
        return len(self._read())
