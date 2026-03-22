from __future__ import annotations

from typing import Sequence

from acquisition.gui_models import MAX_SIGNAL_COUNT


MAX_SUBPLOT_COUNT = MAX_SIGNAL_COUNT


def clamp_subplot_count(requested_count: int, signal_count: int | None = None) -> int:
    """Clamp subplot count to a student-friendly range."""

    upper_bound = MAX_SUBPLOT_COUNT
    if signal_count is not None:
        upper_bound = max(1, min(MAX_SUBPLOT_COUNT, signal_count))

    return max(1, min(upper_bound, int(requested_count)))


def default_subplot_signal_indices(signal_count: int, subplot_count: int) -> tuple[tuple[int, ...], ...]:
    """Split active signals into contiguous subplot groups."""

    bounded_signal_count = max(0, min(MAX_SIGNAL_COUNT, int(signal_count)))
    bounded_subplot_count = clamp_subplot_count(subplot_count, bounded_signal_count or 1)

    if bounded_subplot_count == 1:
        return (tuple(range(bounded_signal_count)),)

    base_group_size, remainder = divmod(bounded_signal_count, bounded_subplot_count)
    subplot_groups = []
    start_index = 0

    for subplot_index in range(bounded_subplot_count):
        group_size = base_group_size + (1 if subplot_index < remainder else 0)
        end_index = min(start_index + group_size, bounded_signal_count)
        subplot_groups.append(tuple(range(start_index, end_index)))
        start_index = end_index

    return tuple(subplot_groups)


def selected_subplot_signal_indices(
    selection_grid: Sequence[Sequence[bool]],
    signal_count: int,
    subplot_count: int,
) -> tuple[tuple[int, ...], ...]:
    """Read selected signal indices from a Boolean selection grid."""

    bounded_signal_count = max(0, min(MAX_SIGNAL_COUNT, int(signal_count)))
    bounded_subplot_count = clamp_subplot_count(subplot_count, bounded_signal_count or 1)
    subplot_groups = []

    for subplot_index in range(bounded_subplot_count):
        row = selection_grid[subplot_index] if subplot_index < len(selection_grid) else ()
        subplot_groups.append(
            tuple(
                signal_index
                for signal_index in range(bounded_signal_count)
                if signal_index < len(row) and bool(row[signal_index])
            )
        )

    return tuple(subplot_groups)


def format_signal_reference_text(signal_names: Sequence[str]) -> str:
    """Create a short signal reference label for the subplot controls."""

    if not signal_names:
        return "Signals: none configured yet."

    references = []
    for signal_index, name in enumerate(signal_names, start=1):
        normalized_name = name.strip() or f"Signal {signal_index}"
        references.append(f"S{signal_index}={normalized_name}")

    return "Signals: " + " | ".join(references)
