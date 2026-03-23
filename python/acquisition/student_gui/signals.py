from __future__ import annotations

from pathlib import Path

import tkinter as tk
from tkinter import ttk

from acquisition.arduino_cli_wrapper import SUPPORTED_BOARDS, UNO_R4_WIFI_BOARD
from acquisition.gui_models import MAX_SIGNAL_COUNT, GuiAcquisitionConfig, SignalConfiguration, validate_gui_config
from acquisition.lab_profiles import LAB_PROFILE_ORDER, get_lab_profile
from acquisition.presets import LAB_PRESETS, get_preset
from acquisition.protocol import PULSEOX_ANALOG_PORTS, PULSEOX_CYCLE_VALUE_FIELDS, UNO_R4_ANALOG_PORTS


class SignalConfigurationMixin:
    def _build_signal_frame(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Signals", padding=10)
        frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        frame.columnconfigure(0, weight=1)

        ttk.Label(frame, text="Number of signals").grid(row=0, column=0, sticky="w", pady=(0, 6))
        self.signal_count_spinbox = ttk.Spinbox(
            frame,
            from_=1,
            to=MAX_SIGNAL_COUNT,
            textvariable=self.signal_count_var,
            width=6,
            command=self._apply_signal_count,
        )
        self.signal_count_spinbox.grid(row=1, column=0, sticky="w", pady=(0, 10))
        self.signal_count_var.trace_add("write", lambda *_args: self._apply_signal_count())

        ttk.Label(
            frame,
            text="UNO R4 WiFi analog inputs available in this demo: A0 to A5.",
            wraplength=320,
            justify="left",
        ).grid(row=2, column=0, sticky="w", pady=(0, 6))

        defaults = self.default_config.signal_configurations
        preset_names = list(LAB_PRESETS)
        analog_port_names = list(UNO_R4_ANALOG_PORTS)

        for index in range(MAX_SIGNAL_COUNT):
            signal_frame = ttk.Frame(frame, padding=(0, 8, 0, 0))
            signal_frame.grid(row=index + 3, column=0, sticky="ew")
            signal_frame.columnconfigure(0, weight=1)

            name_var = tk.StringVar(value=defaults[index].name)
            preset_var = tk.StringVar(value=defaults[index].preset_name)
            port_var = tk.StringVar(value=defaults[index].analog_port)
            self.signal_name_vars.append(name_var)
            self.signal_preset_vars.append(preset_var)
            self.signal_port_vars.append(port_var)
            name_var.trace_add("write", lambda *_args: self._refresh_plot_series_reference_text())

            ttk.Label(signal_frame, text=f"Signal {index + 1} name").grid(row=0, column=0, sticky="w")
            name_entry = ttk.Entry(signal_frame, textvariable=name_var)
            name_entry.grid(row=1, column=0, sticky="ew", pady=(4, 4))

            ttk.Label(signal_frame, text="Preset").grid(row=2, column=0, sticky="w")
            preset_combo = ttk.Combobox(signal_frame, textvariable=preset_var, values=preset_names, state="readonly")
            preset_combo.grid(row=3, column=0, sticky="ew", pady=(4, 4))
            self._bind_combobox_scroll_guard(preset_combo)

            ttk.Label(signal_frame, text="Analog port").grid(row=4, column=0, sticky="w")
            port_combo = ttk.Combobox(signal_frame, textvariable=port_var, values=analog_port_names, state="readonly")
            port_combo.grid(row=5, column=0, sticky="ew", pady=(4, 4))
            self._bind_combobox_scroll_guard(port_combo)
            self.signal_port_combos.append(port_combo)

            info_label = ttk.Label(signal_frame, text="", wraplength=300, justify="left")
            info_label.grid(row=6, column=0, sticky="w")
            self.signal_rows.append((signal_frame, info_label))

            preset_var.trace_add("write", lambda *_args, row_index=index: self._update_signal_preset_info(row_index))

        # Wait until all signal rows exist before running info-refresh logic.
        for index in range(MAX_SIGNAL_COUNT):
            self._update_signal_preset_info(index)

    def _on_lab_profile_selected(self, _event=None) -> None:
        profile_name = self.lab_profile_var.get().strip()
        if profile_name in LAB_PROFILE_ORDER:
            self._load_lab_profile(profile_name)

    def _load_lab_profile(self, profile_name: str, log_message: bool = True) -> None:
        profile = get_lab_profile(profile_name)
        self.current_lab_profile = profile
        self.lab_profile_var.set(profile.display_name)
        self.board_var.set(UNO_R4_WIFI_BOARD.display_name)
        self.signal_count_var.set(len(profile.signal_configurations))
        self._refresh_output_basename(profile.output_basename)

        for index, signal in enumerate(profile.signal_configurations):
            self.signal_name_vars[index].set(signal.name)
            self.signal_preset_vars[index].set(signal.preset_name)
            self.signal_port_vars[index].set(signal.analog_port)

        for index in range(len(profile.signal_configurations), MAX_SIGNAL_COUNT):
            default_signal = self.default_config.signal_configurations[index]
            self.signal_name_vars[index].set(default_signal.name)
            self.signal_preset_vars[index].set(default_signal.preset_name)
            self.signal_port_vars[index].set(default_signal.analog_port)

        self.current_lab_var.set(f"Loaded lab: {profile.display_name}")
        self.firmware_summary_var.set(f"Firmware: {profile.firmware_label}. {profile.note}")
        self._apply_signal_count()

        if log_message:
            self._append_status(
                f"Loaded {profile.display_name} profile with {len(profile.signal_configurations)} signal(s)."
            )

    def _selected_board(self):
        for board in SUPPORTED_BOARDS:
            if board.display_name == self.board_var.get():
                return board
        return UNO_R4_WIFI_BOARD

    def _selected_port_device(self) -> str:
        return self.port_display_to_device.get(self.port_var.get(), self.port_var.get().strip())

    def _selected_signal_configurations(self) -> tuple[SignalConfiguration, ...]:
        signal_count = int(self.signal_count_var.get())
        available_count = min(
            signal_count,
            len(self.signal_name_vars),
            len(self.signal_preset_vars),
            len(self.signal_port_vars),
        )
        return tuple(
            SignalConfiguration(
                name=self.signal_name_vars[index].get().strip(),
                preset_name=self.signal_preset_vars[index].get(),
                analog_port=self.signal_port_vars[index].get(),
            )
            for index in range(available_count)
        )

    def _preview_signal_configurations(self) -> tuple[SignalConfiguration, ...]:
        if self.session is not None:
            return self.session.config.signal_configurations
        return self._selected_signal_configurations()

    def _is_pulseox_configuration(self, signal_configurations: tuple[SignalConfiguration, ...]) -> bool:
        return bool(signal_configurations) and all(signal.preset_name == "PulseOx" for signal in signal_configurations)

    def _preview_plot_series_names(self) -> tuple[str, ...]:
        if self.session is not None:
            return self.session.plot_series_names

        signal_configurations = self._selected_signal_configurations()
        if self._is_pulseox_configuration(signal_configurations):
            return PULSEOX_CYCLE_VALUE_FIELDS

        return tuple(signal.name.strip() or f"Signal {index + 1}" for index, signal in enumerate(signal_configurations))

    def _apply_signal_count(self) -> None:
        try:
            signal_count = int(self.signal_count_var.get())
        except tk.TclError:
            return

        signal_count = max(1, min(MAX_SIGNAL_COUNT, signal_count))
        if self.signal_count_var.get() != signal_count:
            self.signal_count_var.set(signal_count)

        for index, (row_frame, _info_label) in enumerate(self.signal_rows):
            if index < signal_count:
                row_frame.grid()
            else:
                row_frame.grid_remove()

        self._refresh_plot_series_reference_text()
        self._apply_subplot_count(reset_assignments=True)

    def _update_signal_preset_info(self, row_index: int) -> None:
        preset_name = self.signal_preset_vars[row_index].get()
        info_label = self.signal_rows[row_index][1]
        port_combo = self.signal_port_combos[row_index]
        self._refresh_plot_series_reference_text()
        should_refresh_subplot_layout = hasattr(self, "figure") and bool(self.subplot_rows)

        if preset_name not in LAB_PRESETS:
            info_label.configure(text="Unknown preset")
            port_combo.configure(state="readonly")
            if should_refresh_subplot_layout:
                self._apply_subplot_count(reset_assignments=True)
            return

        preset = get_preset(preset_name)
        rate_text = (
            f"{preset.default_sample_rate_hz} samples/s"
            if preset.default_sample_rate_hz is not None
            else f"{preset.default_cycle_rate_hz} cycles/s"
        )
        packets = "/".join(preset.packet_types)
        default_field_text = ",".join(preset.default_fields[:2])
        if preset_name == "PulseOx":
            if row_index < len(PULSEOX_ANALOG_PORTS):
                self.signal_port_vars[row_index].set(PULSEOX_ANALOG_PORTS[row_index])
                port_combo.configure(state="disabled")
                port_note = f"Fixed pin {PULSEOX_ANALOG_PORTS[row_index]}"
            else:
                port_combo.configure(state="disabled")
                port_note = "PulseOx uses only the first four fixed channels"
            info_label.configure(
                text=(
                    f"{preset.acquisition_class} | {rate_text} | {packets} | {default_field_text} | "
                    f"{port_note}. PulseOx derives RED vs IR from the LED phase."
                )
            )
            if should_refresh_subplot_layout:
                self._apply_subplot_count(reset_assignments=True)
            return

        port_combo.configure(state="readonly")
        info_label.configure(
            text=f"{preset.acquisition_class} | {rate_text} | {packets} | {default_field_text}",
        )
        if should_refresh_subplot_layout:
            self._apply_subplot_count(reset_assignments=True)

    def _build_gui_config(self) -> GuiAcquisitionConfig:
        signal_count = int(self.signal_count_var.get())
        signal_configurations = []

        for index in range(signal_count):
            signal_configurations.append(
                SignalConfiguration(
                    name=self.signal_name_vars[index].get().strip(),
                    preset_name=self.signal_preset_vars[index].get(),
                    analog_port=self.signal_port_vars[index].get(),
                )
            )

        config = GuiAcquisitionConfig(
            board_name=self._selected_board().display_name,
            board_fqbn=self._selected_board().fqbn,
            port=self._selected_port_device(),
            output_dir=Path(self.output_dir_var.get()).expanduser(),
            output_basename=self.output_basename_var.get().strip(),
            baud_rate=self.default_config.baud_rate,
            signal_configurations=tuple(signal_configurations),
        )
        validate_gui_config(config)
        return config
