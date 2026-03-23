from __future__ import annotations

from collections import deque

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import ttk

from acquisition.gui_plot_layout import (
    MAX_SUBPLOT_COUNT,
    clamp_subplot_count,
    default_subplot_signal_indices,
    format_signal_reference_text,
    selected_subplot_signal_indices,
)
from acquisition.presets import get_preset
from acquisition.student_gui.constants import PLOT_COLORS


class PlottingMixin:
    def _build_plot_frame(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Live Plot", padding=10)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        plot_controls_frame = ttk.Frame(frame)
        plot_controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        plot_controls_frame.columnconfigure(1, weight=1)

        ttk.Label(plot_controls_frame, text="Number of subplots").grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, 8),
        )
        self.subplot_count_spinbox = ttk.Spinbox(
            plot_controls_frame,
            from_=1,
            to=MAX_SUBPLOT_COUNT,
            textvariable=self.subplot_count_var,
            width=6,
            command=self._apply_subplot_count,
        )
        self.subplot_count_spinbox.grid(row=0, column=1, sticky="w")
        self.subplot_count_var.trace_add("write", lambda *_args: self._apply_subplot_count())

        ttk.Label(
            plot_controls_frame,
            text=(
                "Use S1 onward to place each plotted series on one or more subplots. "
                "Changing the subplot count resets to a simple default split."
            ),
            wraplength=760,
            justify="left",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 4))

        ttk.Label(
            plot_controls_frame,
            textvariable=self.plot_signal_reference_var,
            wraplength=760,
            justify="left",
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 8))

        subplot_selection_frame = ttk.Frame(plot_controls_frame)
        subplot_selection_frame.grid(row=3, column=0, columnspan=2, sticky="ew")
        subplot_selection_frame.columnconfigure(0, weight=1)

        for subplot_index in range(MAX_SUBPLOT_COUNT):
            subplot_row = ttk.Frame(subplot_selection_frame)
            subplot_row.grid(row=subplot_index, column=0, sticky="ew", pady=(0, 4))
            subplot_row.columnconfigure(1, weight=1)

            ttk.Label(subplot_row, text=f"Subplot {subplot_index + 1}").grid(
                row=0,
                column=0,
                sticky="w",
                padx=(0, 12),
            )

            checkbox_frame = ttk.Frame(subplot_row)
            checkbox_frame.grid(row=0, column=1, sticky="w")

            subplot_vars = []
            subplot_checkbuttons = []
            for signal_index in range(MAX_SUBPLOT_COUNT):
                signal_var = tk.BooleanVar(value=False)
                checkbutton = ttk.Checkbutton(
                    checkbox_frame,
                    text=f"S{signal_index + 1}",
                    variable=signal_var,
                    command=self._on_subplot_selection_changed,
                )
                checkbutton.grid(row=0, column=signal_index, sticky="w", padx=(0, 8))
                subplot_vars.append(signal_var)
                subplot_checkbuttons.append(checkbutton)

            self.subplot_rows.append(subplot_row)
            self.subplot_signal_vars.append(subplot_vars)
            self.subplot_checkbuttons.append(subplot_checkbuttons)

        self.figure = Figure(figsize=(8.0, 5.6), dpi=100, constrained_layout=True)

        self.canvas = FigureCanvasTkAgg(self.figure, master=frame)
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")

    def _refresh_plot_series_reference_text(self) -> None:
        self.plot_signal_reference_var.set(format_signal_reference_text(self._preview_plot_series_names()))

    def _apply_subplot_count(self, reset_assignments: bool = True) -> None:
        if self.updating_subplot_controls:
            return

        try:
            requested_subplot_count = int(self.subplot_count_var.get())
        except Exception:
            requested_subplot_count = 1

        signal_count = len(self._preview_plot_series_names())
        bounded_subplot_count = clamp_subplot_count(requested_subplot_count, signal_count or 1)

        self.updating_subplot_controls = True
        try:
            if self.subplot_count_var.get() != bounded_subplot_count:
                self.subplot_count_var.set(bounded_subplot_count)

            if reset_assignments:
                self._apply_default_subplot_assignments(signal_count, bounded_subplot_count)

            for subplot_index, subplot_row in enumerate(self.subplot_rows):
                if subplot_index < bounded_subplot_count:
                    subplot_row.grid()
                else:
                    subplot_row.grid_remove()

                for signal_index, checkbutton in enumerate(self.subplot_checkbuttons[subplot_index]):
                    if signal_index < signal_count:
                        checkbutton.grid()
                    else:
                        self.subplot_signal_vars[subplot_index][signal_index].set(False)
                        checkbutton.grid_remove()
        finally:
            self.updating_subplot_controls = False

        self._refresh_plot_preview()

    def _apply_default_subplot_assignments(self, signal_count: int, subplot_count: int) -> None:
        default_indices = default_subplot_signal_indices(signal_count, subplot_count)

        for subplot_index, subplot_vars in enumerate(self.subplot_signal_vars):
            selected_indices = set(default_indices[subplot_index]) if subplot_index < len(default_indices) else set()
            for signal_index, signal_var in enumerate(subplot_vars):
                signal_var.set(signal_index in selected_indices)

    def _apply_saved_subplot_assignments(
        self,
        subplot_count: int,
        selected_series_indices: tuple[tuple[int, ...], ...],
    ) -> None:
        signal_count = len(self._preview_plot_series_names())
        bounded_subplot_count = clamp_subplot_count(subplot_count, signal_count or 1)
        self.subplot_count_var.set(bounded_subplot_count)
        self._apply_subplot_count(reset_assignments=False)

        self.updating_subplot_controls = True
        try:
            for subplot_index, subplot_vars in enumerate(self.subplot_signal_vars):
                selected_indices = (
                    set(selected_series_indices[subplot_index])
                    if subplot_index < len(selected_series_indices)
                    else set()
                )
                for signal_index, signal_var in enumerate(subplot_vars):
                    signal_var.set(signal_index in selected_indices and signal_index < signal_count)
        finally:
            self.updating_subplot_controls = False

        self._refresh_plot_preview()

    def _selected_subplot_signal_indices(self, signal_count: int, subplot_count: int) -> tuple[tuple[int, ...], ...]:
        selection_grid = tuple(
            tuple(signal_var.get() for signal_var in subplot_vars)
            for subplot_vars in self.subplot_signal_vars
        )
        return selected_subplot_signal_indices(selection_grid, signal_count, subplot_count)

    def _on_subplot_selection_changed(self) -> None:
        if self.updating_subplot_controls:
            return
        self._refresh_plot_preview()

    def _refresh_plot_preview(self) -> None:
        signal_configurations = self._preview_signal_configurations()
        plot_series_names = self._preview_plot_series_names()
        if not signal_configurations or not plot_series_names:
            return
        self._rebuild_plot_layout(plot_series_names)

    def _reset_plot(self) -> None:
        plot_series_names = self._preview_plot_series_names()
        self.plot_time_s = deque(maxlen=2500)
        self.plot_signal_values = [deque(maxlen=2500) for _ in plot_series_names]

        signal_configurations = self._preview_signal_configurations()
        if signal_configurations:
            self.plot_history_seconds = max(
                get_preset(signal.preset_name).plotting.history_seconds for signal in signal_configurations
            )

        self._rebuild_plot_layout(plot_series_names)

    def _rebuild_plot_layout(self, plot_series_names: tuple[str, ...]) -> None:
        if not plot_series_names:
            return

        signal_count = len(plot_series_names)
        try:
            requested_subplot_count = int(self.subplot_count_var.get())
        except Exception:
            requested_subplot_count = 1

        subplot_count = clamp_subplot_count(requested_subplot_count, signal_count)
        selected_groups = self._selected_subplot_signal_indices(signal_count, subplot_count)

        self.figure.clear()
        axes_grid = self.figure.subplots(subplot_count, 1, sharex=True, squeeze=False)
        self.plot_axes = list(axes_grid.flat)
        self.plot_line_groups = []

        for subplot_index, axis in enumerate(self.plot_axes):
            axis.grid(True)
            axis.set_ylabel("ADC value")

            selected_indices = selected_groups[subplot_index] if subplot_index < len(selected_groups) else ()
            if selected_indices:
                line_group = {}
                for signal_index in selected_indices:
                    line, = axis.plot(
                        [],
                        [],
                        label=plot_series_names[signal_index],
                        color=PLOT_COLORS[signal_index % len(PLOT_COLORS)],
                        linewidth=1.8,
                    )
                    line_group[signal_index] = line

                axis.set_title(self._subplot_title(subplot_index, plot_series_names, selected_indices))
                axis.legend(loc="upper left")
                self.plot_line_groups.append(line_group)
            else:
                axis.set_title(f"Subplot {subplot_index + 1}: no signals selected")
                axis.text(
                    0.5,
                    0.5,
                    "Select one or more signals above.",
                    ha="center",
                    va="center",
                    transform=axis.transAxes,
                    color="#4B5563",
                )
                self.plot_line_groups.append({})

        if self.plot_axes:
            self.plot_axes[-1].set_xlabel("Device time (s)")

        self.canvas.draw_idle()

        if self.plot_time_s:
            self._refresh_plot()

    def _subplot_title(
        self,
        subplot_index: int,
        plot_series_names: tuple[str, ...],
        selected_indices: tuple[int, ...],
    ) -> str:
        selected_names = ", ".join(plot_series_names[signal_index] for signal_index in selected_indices)
        return f"Subplot {subplot_index + 1}: {selected_names}"

    def _append_sample(self, sample) -> None:
        if not self.plot_signal_values:
            return

        self.plot_time_s.append(sample.device_time_us / 1_000_000.0)
        for index, value in enumerate(sample.values):
            if index < len(self.plot_signal_values):
                self.plot_signal_values[index].append(value)

    def _refresh_plot(self) -> None:
        if not self.plot_axes or not self.plot_time_s:
            return

        x_values = list(self.plot_time_s)
        latest_time = x_values[-1]
        left_edge = max(0.0, latest_time - self.plot_history_seconds)
        right_edge = max(self.plot_history_seconds, latest_time)
        visible_indices = [index for index, timestamp in enumerate(x_values) if timestamp >= left_edge]
        signal_value_lists = [list(signal_values) for signal_values in self.plot_signal_values]

        for axis, line_group in zip(self.plot_axes, self.plot_line_groups):
            axis.set_xlim(left_edge, right_edge)

            visible_values = []
            for signal_index, line in line_group.items():
                signal_values = signal_value_lists[signal_index]
                line.set_data(x_values, signal_values)
                visible_values.extend(signal_values[index] for index in visible_indices if index < len(signal_values))

            if not visible_values:
                axis.set_ylim(0, 1)
                continue

            min_value = min(visible_values)
            max_value = max(visible_values)
            padding = max(10.0, (max_value - min_value) * 0.05)
            axis.set_ylim(min_value - padding, max_value + padding)

        self.canvas.draw_idle()
