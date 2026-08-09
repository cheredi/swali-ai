"""Spaced repetition scheduling based on SM-2."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class SM2State:
    repetitions: int = 0
    interval_days: int = 1
    ease_factor: float = 2.5


def next_sm2_state(previous: SM2State | None, quality: int) -> tuple[SM2State, datetime]:
    quality = max(0, min(5, quality))
    state = previous or SM2State()

    if quality < 3:
        state.repetitions = 0
        state.interval_days = 1
    else:
        if state.repetitions == 0:
            state.interval_days = 1
        elif state.repetitions == 1:
            state.interval_days = 6
        else:
            state.interval_days = int(round(state.interval_days * state.ease_factor))
        state.repetitions += 1

    ef_delta = 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
    state.ease_factor = max(1.3, state.ease_factor + ef_delta)
    due_at = datetime.utcnow() + timedelta(days=state.interval_days)
    return state, due_at
