from __future__ import annotations

from datetime import datetime
from pathlib import Path

from tkinter import filedialog, messagebox, ttk

from acquisition.gui_models import MAX_SIGNAL_COUNT
from acquisition.gui_session import GuiAcquisitionSession
from acquisition.presets import get_preset
from acquisition.lab_profiles import CUSTOM_LAB_PROFILE_NAME
from acquisition.student_gui.constants import DEFAULT_OUTPUT_DIR, DEFAULT_SESSION_PRESET_DIR, TIMESTAMP_SUFFIX_PATTERN
from acquisition.student_gui.preset_io import (
    build_session_preset,
    default_plot_series_names,
    load_session_preset,
    resolve_preset_path,
    save_session_preset,
)


class SessionControlsMixin:
    def _build_output_frame(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Save Output", padding=10)
        frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        frame.columnconfigure(0, weight=1)

        ttk.Label(frame, text="Save folder").grid(row=0, column=0, sticky="w")
        self.output_dir_entry = ttk.Entry(frame, textvariable=self.output_dir_var)
        self.output_dir_entry.grid(row=1, column=0, sticky="ew", pady=(4, 6))
        self.output_dir_button = ttk.Button(frame, text="Choose Folder", command=self._choose_output_dir)
        self.output_dir_button.grid(row=2, column=0, sticky="ew", pady=(0, 8))

        ttk.Label(frame, text="Output filename").grid(row=3, column=0, sticky="w")
        self.output_basename_entry = ttk.Entry(frame, textvariable=self.output_basename_var)
        self.output_basename_entry.grid(row=4, column=0, sticky="ew", pady=(4, 0))

    def _build_control_frame(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Acquisition", padding=10)
        frame.grid(row=4, column=0, sticky="ew")
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        self.start_button = ttk.Button(frame, text="Start Acquisition", command=self._start_acquisition)
        self.start_button.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.stop_button = ttk.Button(frame, text="Stop Acquisition", command=self._stop_acquisition, state="disabled")
        self.stop_button.grid(row=0, column=1, sticky="ew", padx=(6, 0))

    def _choose_output_dir(self) -> None:
        selected = filedialog.askdirectory(initialdir=self.output_dir_var.get() or str(DEFAULT_OUTPUT_DIR))
        if selected:
            self.output_dir_var.set(selected)

    def _timestamp_suffix(self) -> str:
        return datetime.now().strftime("_%Y_%m_%d_%H_%M_%S")

    def _default_output_prefix(self) -> str:
        if self.current_lab_profile is not None:
            return self.current_lab_profile.output_basename
        return self.default_config.output_basename

    def _output_prefix_without_timestamp(self) -> str:
        current_value = self.output_basename_var.get().strip()
        if not current_value:
            return self._default_output_prefix()

        prefix = TIMESTAMP_SUFFIX_PATTERN.sub("", current_value).rstrip("_")
        return prefix or self._default_output_prefix()

    def _refresh_output_basename(self, prefix: str | None = None) -> None:
        selected_prefix = (prefix or self._output_prefix_without_timestamp()).strip()
        if not selected_prefix:
            selected_prefix = self._default_output_prefix()
        self.output_basename_var.set(f"{selected_prefix}{self._timestamp_suffix()}")

    def _save_session_preset_to_file(self) -> None:
        signal_configurations = self._selected_signal_configurations()
        try:
            plot_series_names = self._preview_plot_series_names() or default_plot_series_names(signal_configurations)
            subplot_count = int(self.subplot_count_var.get())
            subplot_signal_indices = self._selected_subplot_signal_indices(len(plot_series_names), subplot_count)
            preset = build_session_preset(
                preset_name=self.current_lab_profile.display_name if self.current_lab_profile is not None else "Session Preset",
                lab_profile_name=self.current_lab_profile.display_name if self.current_lab_profile is not None else None,
                board_name=self._selected_board().display_name,
                output_dir=Path(self.output_dir_var.get()).expanduser(),
                output_basename_prefix=self._output_prefix_without_timestamp(),
                signal_configurations=signal_configurations,
                plot_subplot_count=subplot_count,
                plot_selected_series_indices=subplot_signal_indices,
                plot_series_names=plot_series_names,
            )
        except Exception as error:
            messagebox.showerror("Could not Save Preset", str(error))
            self._append_status(f"Could not save preset: {error}")
            return

        DEFAULT_SESSION_PRESET_DIR.mkdir(parents=True, exist_ok=True)
        suggested_name = f"{preset.output_basename_prefix}_preset.json"
        target = filedialog.asksaveasfilename(
            initialdir=str(DEFAULT_SESSION_PRESET_DIR),
            defaultextension=".json",
            filetypes=[("JSON preset", "*.json")],
            initialfile=suggested_name,
            title="Save Session Preset",
        )
        if not target:
            return

        preset_path = Path(target)
        save_session_preset(preset, preset_path)
        self._append_status(f"Saved session preset to {preset_path}")

    def _load_session_preset_from_file(self) -> None:
        preset_dir = DEFAULT_SESSION_PRESET_DIR if DEFAULT_SESSION_PRESET_DIR.exists() else DEFAULT_OUTPUT_DIR
        target = filedialog.askopenfilename(
            initialdir=str(preset_dir),
            filetypes=[("JSON preset", "*.json")],
            title="Load Session Preset",
        )
        if not target:
            return

        try:
            preset = load_session_preset(Path(target))
            self._apply_session_preset(preset)
        except Exception as error:
            messagebox.showerror("Could not Load Preset", str(error))
            self._append_status(f"Could not load preset: {error}")
            return

        self._append_status(f"Loaded session preset from {target}")

    def _apply_session_preset(self, preset) -> None:
        self.board_var.set(preset.board_name)
        self.output_dir_var.set(str(resolve_preset_path(preset.save_folder)))
        self.current_lab_profile = None

        if preset.lab_profile_name is not None:
            self._load_lab_profile(preset.lab_profile_name, log_message=False)
        else:
            self.lab_profile_var.set(CUSTOM_LAB_PROFILE_NAME)
            self.current_lab_var.set("Loaded lab: Custom")
            self.firmware_summary_var.set("Firmware: Generated UNO R4 WiFi Acquisition Firmware. Loaded from preset.")

        self.signal_count_var.set(len(preset.signals))
        for index, signal in enumerate(preset.signals):
            self.signal_name_vars[index].set(signal.name)
            self.signal_preset_vars[index].set(signal.preset_name)
            self.signal_port_vars[index].set(signal.analog_port)

        for index in range(len(preset.signals), MAX_SIGNAL_COUNT):
            default_signal = self.default_config.signal_configurations[index]
            self.signal_name_vars[index].set(default_signal.name)
            self.signal_preset_vars[index].set(default_signal.preset_name)
            self.signal_port_vars[index].set(default_signal.analog_port)

        self._apply_signal_count()
        self._refresh_output_basename(preset.output_basename_prefix)
        self._apply_saved_subplot_assignments(
            preset.plot_subplot_count,
            preset.plot_selected_series_indices,
        )
        self._refresh_ports(log_message=False)

    def _start_acquisition(self) -> None:
        if self.session is not None:
            messagebox.showinfo("Acquisition Running", "Stop the current acquisition before starting another one.")
            return

        try:
            self._refresh_output_basename()
            config = self._build_gui_config()
            session = GuiAcquisitionSession(config)
            session.start()
        except Exception as error:
            messagebox.showerror("Could not Start Acquisition", str(error))
            self._append_status(f"Could not start acquisition: {error}")
            return

        self.session = session
        self._set_acquisition_controls(running=True)
        self._reset_plot()

    def _stop_acquisition(self) -> None:
        if self.session is None:
            return

        self.session.stop()
        self.session.join(timeout=2.0)
        self.session = None
        self._set_acquisition_controls(running=False)
        self._refresh_output_basename()

    def _set_acquisition_controls(self, running: bool) -> None:
        entry_state = "disabled" if running else "normal"
        combo_state = "disabled" if running else "readonly"
        spinbox_state = "disabled" if running else "normal"

        self.board_combo.configure(state=combo_state)
        self.port_combo.configure(state=combo_state)
        self.refresh_ports_button.configure(state=entry_state)
        self.output_dir_entry.configure(state=entry_state)
        self.output_dir_button.configure(state=entry_state)
        self.output_basename_entry.configure(state=entry_state)
        self.signal_count_spinbox.configure(state=spinbox_state)
        if self.lab_profile_combo is not None:
            self.lab_profile_combo.configure(state=combo_state)

        for index in range(MAX_SIGNAL_COUNT):
            children = self.signal_rows[index][0].winfo_children()
            for widget in children:
                if isinstance(widget, ttk.Combobox):
                    widget.configure(state="disabled" if running else combo_state)
                elif isinstance(widget, ttk.Entry):
                    widget.configure(state=entry_state)

        self.start_button.configure(state="disabled" if running else "normal")
        self.stop_button.configure(state="normal" if running else "disabled")

        if not running:
            for index in range(MAX_SIGNAL_COUNT):
                self._update_signal_preset_info(index)
            self._refresh_plot_series_reference_text()
