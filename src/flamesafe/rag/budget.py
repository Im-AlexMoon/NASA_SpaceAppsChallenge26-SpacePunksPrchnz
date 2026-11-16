"""Atomic, durable, single-instance admission ledger. Failures consume reservations."""

import sqlite3
from datetime import UTC, datetime


class Budget:
    def __init__(self, settings):
        self.settings = settings

    def _reserve_shared(self, now):
        from google.cloud import firestore

        s = self.settings
        db = firestore.Client(project=s.firestore_project)
        collection = db.collection("flamesafe_generation_budget")
        windows = (
            (collection.document("day-" + now[:10]), s.daily_calls, s.daily_budget_usd),
            (collection.document("month-" + now[:7]), s.monthly_calls, s.monthly_budget_usd),
        )
        reserve = s.reservation_usd if s.billing_mode == "paid" else 0

        @firestore.transactional
        def admit(transaction):
            snapshots = [ref.get(transaction=transaction, retry=None, timeout=5) for ref, _, _ in windows]
            for snap, (ref, cap, money) in zip(snapshots, windows, strict=True):
                row = snap.to_dict() or {}
                calls = row.get("calls", 0)
                spent = row.get("reserved", 0)
                if calls >= cap or (s.billing_mode == "paid" and spent + reserve > money + 1e-10):
                    raise ValueError("Generation quota exhausted; evidence-only mode remains available.")
                transaction.set(ref, {"calls": calls + 1, "reserved": spent + reserve})

        try:
            admit(db.transaction(max_attempts=2))
        finally:
            db.close()

    def reserve(self):
        s = self.settings
        if not s.generation_enabled or s.billing_mode not in {"free", "paid"}:
            raise ValueError("Generation is disabled; use evidence-only mode.")
        if s.daily_calls <= 0 or s.monthly_calls <= 0:
            raise ValueError("Positive daily and monthly call quotas are required.")
        if (
            s.billing_mode == "paid"
            and min(s.reservation_usd, s.daily_budget_usd, s.monthly_budget_usd) <= 0
        ):
            raise ValueError("Paid mode requires per-call reservation and both budget caps.")
        now = datetime.now(UTC).isoformat()
        if s.firestore_project:
            self._reserve_shared(now)
            return
        if s.cloud_runtime:
            raise ValueError("The shared generation ledger is unavailable; use evidence mode.")
        s.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(s.ledger_path, timeout=10) as con:
            con.execute(
                "CREATE TABLE IF NOT EXISTS calls (at TEXT NOT NULL, reserved REAL NOT NULL)"
            )
            con.execute("BEGIN IMMEDIATE")
            for prefix, cap, money in (
                (now[:10], s.daily_calls, s.daily_budget_usd),
                (now[:7], s.monthly_calls, s.monthly_budget_usd),
            ):
                count, spent = con.execute(
                    "SELECT count(*), coalesce(sum(reserved),0) FROM calls WHERE at LIKE ?",
                    (prefix + "%",),
                ).fetchone()
                if count >= cap or (
                    s.billing_mode == "paid" and spent + s.reservation_usd > money + 1e-10
                ):
                    raise ValueError(
                        "Generation quota exhausted; evidence-only mode remains available."
                    )
            con.execute(
                "INSERT INTO calls VALUES (?, ?)",
                (now, s.reservation_usd if s.billing_mode == "paid" else 0),
            )
