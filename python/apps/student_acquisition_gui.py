from __future__ import annotations

import re
import threading
import tkinter as tk
from collections import deque
from datetime import datetime
from pathlib import Path
from queue import Empty, SimpleQueue
from tkinter import filedialog, messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from acquisition.arduino_cli_wrapper import (
    ArduinoCli,
    ArduinoCliError,
    DetectedBoardPort,
    SUPPORTED_BOARDS,
    UNO_R4_WIFI_BOARD,
)
from acquisition.gui_models import (
    DEFAULT_ACTIVE_SIGNAL_COUNT,
    MAX_SIGNAL_COUNT,
    PULSEOX_ROLE_AUTO,
    PULSEOX_SIGNAL_ROLES,
    GuiAcquisitionConfig,
    SignalConfiguration,
    default_gui_config,
    validate_gui_config,
)
from acquisition.gui_plot_layout import (
    MAX_SUBPLOT_COUNT,
    clamp_subplot_count,
    default_subplot_signal_indices,
    format_signal_reference_text,
    selected_subplot_signal_indices,
)
from acquisition.protocol import UNO_R4_ANALOG_PORTS
from acquisition.gui_session import GuiAcquisitionSession, SessionMessage, SessionSample
from acquisition.lab_profiles import LAB_PROFILE_ORDER, LabProfile, get_lab_profile
from acquisition.presets import LAB_PRESETS, get_preset
from acquisition.serial_tools import list_available_ports
from acquisition.system_check import render_system_check, run_system_check


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data" / "gui_sessions"
PLOT_COLORS = ("#0F766E", "#B45309", "#1D4ED8", "#BE123C", "#4338CA", "#047857")
TIMESTAMP_SUFFIX_PATTERN = re.compile(r"_\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}$")


class StudentAcquisitionGui:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Biomedical Instrumentation Lab")
        self.root.geometry("1280x820")
        self.root.minsize(1120, 720)

        self.default_config = default_gui_config(DEFAULT_OUTPUT_DIR)
        self.session: GuiAcquisitionSession | None = None
        self.background_queue: SimpleQueue = SimpleQueue()
        self.cli_task_running = False

        self.board_var = tk.StringVar(value=UNO_R4_WIFI_BOARD.display_name)
        self.port_var = tk.StringVar(value="")
        self.output_dir_var = tk.StringVar(value=str(self.default_config.output_dir))
        self.output_basename_var = tk.StringVar(value=self.default_config.output_basename)
        self.signal_count_var = tk.IntVar(value=DEFAULT_ACTIVE_SIGNAL_COUNT)
        self.subplot_count_var = tk.IntVar(value=1)
        self.connection_summary_var = tk.StringVar(value="Waiting for board detection")
        self.lab_profile_var = tk.StringVar(value="Choose Lab")
        self.current_lab_var = tk.StringVar(value="Loaded lab: Custom")
        self.controls_toggle_label_var = tk.StringVar(value="Hide Left Panel")
        self.status_toggle_label_var = tk.StringVar(value="Hide Status Log")
        self.firmware_summary_var = tk.StringVar(
            value="Firmware: Generated UNO R4 WiFi Acquisition Firmware. No lab profile loaded yet."
        )
        self.plot_signal_reference_var = tk.StringVar(value="Signals: none configured yet.")

        self.port_display_to_device: dict[str, str] = {}
        self.detected_board_ports: list[DetectedBoardPort] = []
        self.signal_name_vars: list[tk.StringVar] = []
        self.signal_preset_vars: list[tk.StringVar] = []
        self.signal_port_vars: list[tk.StringVar] = []
        self.signal_role_vars: list[tk.StringVar] = []
        self.signal_rows: list[tuple[ttk.Frame, ttk.Label]] = []
        self.signal_role_combos: list[ttk.Combobox] = []
        self.lab_profile_combo: ttk.Combobox | None = None
        self.current_lab_profile: LabProfile | None = None
        self.subplot_count_spinbox: ttk.Spinbox | None = None
        self.subplot_rows: list[ttk.Frame] = []
        self.subplot_signal_vars: list[list[tk.BooleanVar]] = []
        self.subplot_checkbuttons: list[list[ttk.Checkbutton]] = []
        self.updating_subplot_controls = False
        self.plot_axes = []
        self.plot_line_groups: list[dict[int, object]] = []
        self.plot_time_s: deque[float] = deque(maxlen=2500)
        self.plot_signal_values: list[deque[int]] = []
        self.plot_history_seconds = 10.0
        self.controls_visible = True
        self.status_visible = True
        self.controls_container: ttk.Frame | None = None
        self.status_area: ttk.Frame | None = None
        self.controls_canvas: tk.Canvas | None = None
        self.controls_frame: ttk.Frame | None = None
        self.controls_window_id: int | None = None

        self._build_ui()
        self._bind_scroll_events()
        self._refresh_output_basename()
        self._refresh_ports(log_message=False)
        self._apply_signal_count()
        self._refresh_plot_preview()
        self._append_status("Ready.")
        self.root.after(100, self._poll_background_work)

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=0)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=0)

        toolbar = ttk.LabelFrame(self.root, text="Lab Menu", padding=10)
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(12, 0))
        toolbar.columnconfigure(0, weight=1)

        self.controls_container = ttk.Frame(self.root, padding=(12, 12, 0, 0))
        self.controls_container.grid(row=1, column=0, sticky="nsew")
        self.controls_container.columnconfigure(0, weight=1)
        self.controls_container.rowconfigure(0, weight=1)

        self.controls_canvas = tk.Canvas(self.controls_container, highlightthickness=0, width=380)
        self.controls_canvas.grid(row=0, column=0, sticky="nsew")

        controls_scrollbar = ttk.Scrollbar(
            self.controls_container,
            orient="vertical",
            command=self.controls_canvas.yview,
        )
        controls_scrollbar.grid(row=0, column=1, sticky="ns")
        self.controls_canvas.configure(yscrollcommand=controls_scrollbar.set)

        self.controls_frame = ttk.Frame(self.controls_canvas, padding=12)
        self.controls_frame.columnconfigure(0, weight=1)
        self.controls_window_id = self.controls_canvas.create_window(
            (0, 0),
            window=self.controls_frame,
            anchor="nw",
        )
        self.controls_frame.bind("<Configure>", self._sync_controls_scrollregion)
        self.controls_canvas.bind("<Configure>", self._resize_controls_window)

        plot_area = ttk.Frame(self.root, padding=(0, 12, 12, 0))
        plot_area.grid(row=1, column=1, sticky="nsew")
        plot_area.columnconfigure(0, weight=1)
        plot_area.rowconfigure(0, weight=1)

        self.status_area = ttk.Frame(self.root, padding=12)
        self.status_area.grid(row=2, column=0, columnspan=2, sticky="nsew")
        self.status_area.columnconfigure(0, weight=1)
        self.status_area.rowconfigure(0, weight=1)

        self._build_toolbar_frame(toolbar)
        self._build_connection_frame(self.controls_frame)
        self._build_firmware_frame(self.controls_frame)
        self._build_output_frame(self.controls_frame)
        self._build_signal_frame(self.controls_frame)
        self._build_control_frame(self.controls_frame)
        self._build_plot_frame(plot_area)
        self._build_status_frame(self.status_area)

    def _build_toolbar_frame(self, parent: ttk.LabelFrame) -> None:
        selector_row = ttk.Frame(parent)
        selector_row.grid(row=0, column=0, sticky="ew")
        selector_row.columnconfigure(1, weight=1)

        ttk.Label(selector_row, text="Lab").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.lab_profile_combo = ttk.Combobox(
            selector_row,
            textvariable=self.lab_profile_var,
            values=LAB_PROFILE_ORDER,
            state="readonly",
        )
        self.lab_profile_combo.grid(row=0, column=1, sticky="ew")
        self.lab_profile_combo.bind("<<ComboboxSelected>>", self._on_lab_profile_selected)
        self._bind_combobox_scroll_guard(self.lab_profile_combo)

        ttk.Button(
            selector_row,
            textvariable=self.controls_toggle_label_var,
            command=self._toggle_controls_panel,
        ).grid(row=0, column=2, sticky="e", padx=(8, 0))

        ttk.Button(
            selector_row,
            textvariable=self.status_toggle_label_var,
            command=self._toggle_status_panel,
        ).grid(row=0, column=3, sticky="e", padx=(8, 0))

        ttk.Label(parent, textvariable=self.current_lab_var, wraplength=1000, justify="left").grid(
            row=1,
            column=0,
            sticky="w",
            pady=(8, 4),
        )
        ttk.Label(parent, textvariable=self.firmware_summary_var, wraplength=1000, justify="left").grid(
            row=2,
            column=0,
            sticky="w",
        )

    def _toggle_controls_panel(self) -> None:
        if self.controls_container is None:
            return

        if self.controls_visible:
            self.controls_container.grid_remove()
            self.controls_visible = False
            self.controls_toggle_label_var.set("Show Left Panel")
        else:
            self.controls_container.grid()
            self.controls_visible = True
            self.controls_toggle_label_var.set("Hide Left Panel")

    def _toggle_status_panel(self) -> None:
        if self.status_area is None:
            return

        if self.status_visible:
            self.status_area.grid_remove()
            self.status_visible = False
            self.status_toggle_label_var.set("Show Status Log")
        else:
            self.status_area.grid()
            self.status_visible = True
            self.status_toggle_label_var.set("Hide Status Log")

    def _bind_scroll_events(self) -> None:
        self.root.bind_all("<MouseWheel>", self._on_controls_mousewheel, add="+")
        self.root.bind_all("<Button-4>", self._on_controls_mousewheel, add="+")
        self.root.bind_all("<Button-5>", self._on_controls_mousewheel, add="+")

    def _bind_combobox_scroll_guard(self, combobox: ttk.Combobox) -> None:
        combobox.bind("<MouseWheel>", self._on_combobox_mousewheel, add="+")
        combobox.bind("<Button-4>", self._on_combobox_mousewheel, add="+")
        combobox.bind("<Button-5>", self._on_combobox_mousewheel, add="+")

    def _sync_controls_scrollregion(self, _event=None) -> None:
        if self.controls_canvas is None:
            return
        self.controls_canvas.configure(scrollregion=self.controls_canvas.bbox("all"))

    def _resize_controls_window(self, event: tk.Event) -> None:
        if self.controls_canvas is None or self.controls_window_id is None:
            return
        self.controls_canvas.itemconfigure(self.controls_window_id, width=event.width)

    def _widget_is_in_controls_pane(self, widget) -> bool:
        if self.controls_canvas is None or self.controls_frame is None:
            return False

        current = widget
        while current is not None:
            if current == self.controls_canvas or current == self.controls_frame:
                return True
            current = getattr(current, "master", None)
        return False

    def _controls_can_scroll(self) -> bool:
        if self.controls_canvas is None:
            return False

        bbox = self.controls_canvas.bbox("all")
        if bbox is None:
            return False

        content_height = bbox[3] - bbox[1]
        visible_height = self.controls_canvas.winfo_height()
        return content_height > visible_height

    def _on_controls_mousewheel(self, event: tk.Event) -> str | None:
        if self.controls_canvas is None or not self._controls_can_scroll():
            return None

        if not self._widget_is_in_controls_pane(event.widget):
            return None

        if getattr(event, "num", None) == 4:
            delta_units = -1
        elif getattr(event, "num", None) == 5:
            delta_units = 1
        elif getattr(event, "delta", 0):
            if abs(event.delta) >= 120:
                delta_units = int(-event.delta / 120)
            else:
                delta_units = -1 if event.delta > 0 else 1
        else:
            return None

        self.controls_canvas.yview_scroll(delta_units, "units")
        return "break"

    def _on_combobox_mousewheel(self, event: tk.Event) -> str:
        scroll_result = self._on_controls_mousewheel(event)
        return scroll_result or "break"

    def _build_connection_frame(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Connection", padding=10)
        frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Board").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=(0, 8))
        self.board_combo = ttk.Combobox(
            frame,
            textvariable=self.board_var,
            state="readonly",
            values=[board.display_name for board in SUPPORTED_BOARDS],
        )
        self.board_combo.grid(row=0, column=1, sticky="ew", pady=(0, 8))
        self._bind_combobox_scroll_guard(self.board_combo)

        ttk.Label(frame, text="Serial port").grid(row=1, column=0, sticky="w", padx=(0, 8))
        self.port_combo = ttk.Combobox(frame, textvariable=self.port_var, state="readonly")
        self.port_combo.grid(row=1, column=1, sticky="ew")
        self._bind_combobox_scroll_guard(self.port_combo)

        summary_label = ttk.Label(frame, textvariable=self.connection_summary_var, wraplength=300, justify="left")
        summary_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))

        self.refresh_ports_button = ttk.Button(frame, text="Refresh Ports", command=self._refresh_ports)
        self.refresh_ports_button.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        self.system_check_button = ttk.Button(frame, text="Run System Check", command=self._run_system_check)
        self.system_check_button.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        self.board_combo.bind("<<ComboboxSelected>>", self._on_board_selected)

    def _build_firmware_frame(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Firmware", padding=10)
        frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        frame.columnconfigure(0, weight=1)

        self.setup_cli_button = ttk.Button(frame, text="Setup Arduino CLI", command=self._setup_arduino_cli)
        self.setup_cli_button.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        self.compile_button = ttk.Button(frame, text="Compile Loaded Firmware", command=self._compile_demo_firmware)
        self.compile_button.grid(row=1, column=0, sticky="ew", pady=(0, 6))

        self.upload_button = ttk.Button(frame, text="Upload Loaded Firmware", command=self._upload_demo_firmware)
        self.upload_button.grid(row=2, column=0, sticky="ew")

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
        pulseox_role_names = list(PULSEOX_SIGNAL_ROLES)

        for index in range(MAX_SIGNAL_COUNT):
            signal_frame = ttk.Frame(frame, padding=(0, 8, 0, 0))
            signal_frame.grid(row=index + 3, column=0, sticky="ew")
            signal_frame.columnconfigure(0, weight=1)

            name_var = tk.StringVar(value=defaults[index].name)
            preset_var = tk.StringVar(value=defaults[index].preset_name)
            port_var = tk.StringVar(value=defaults[index].analog_port)
            role_var = tk.StringVar(value=defaults[index].pulseox_role)
            self.signal_name_vars.append(name_var)
            self.signal_preset_vars.append(preset_var)
            self.signal_port_vars.append(port_var)
            self.signal_role_vars.append(role_var)
            name_var.trace_add("write", lambda *_args: self._refresh_signal_reference_text())
            role_var.trace_add("write", lambda *_args, row_index=index: self._update_signal_preset_info(row_index))

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

            ttk.Label(signal_frame, text="PulseOx role").grid(row=6, column=0, sticky="w")
            role_combo = ttk.Combobox(
                signal_frame,
                textvariable=role_var,
                values=pulseox_role_names,
                state="disabled",
            )
            role_combo.grid(row=7, column=0, sticky="ew", pady=(4, 4))
            self._bind_combobox_scroll_guard(role_combo)
            self.signal_role_combos.append(role_combo)

            info_label = ttk.Label(signal_frame, text="", wraplength=300, justify="left")
            info_label.grid(row=8, column=0, sticky="w")
            self.signal_rows.append((signal_frame, info_label))

            preset_var.trace_add("write", lambda *_args, row_index=index: self._update_signal_preset_info(row_index))
            self._update_signal_preset_info(index)

    def _build_control_frame(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Acquisition", padding=10)
        frame.grid(row=4, column=0, sticky="ew")
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        self.start_button = ttk.Button(frame, text="Start Acquisition", command=self._start_acquisition)
        self.start_button.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.stop_button = ttk.Button(frame, text="Stop Acquisition", command=self._stop_acquisition, state="disabled")
        self.stop_button.grid(row=0, column=1, sticky="ew", padx=(6, 0))

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
                "Use S1 to S6 to place each configured signal on one or more subplots. "
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
            for signal_index in range(MAX_SIGNAL_COUNT):
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

    def _build_status_frame(self, parent: ttk.Frame) -> None:
        self.status_text = tk.Text(parent, height=12, wrap="word")
        self.status_text.grid(row=0, column=0, sticky="nsew")
        self.status_text.configure(state="disabled")

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.status_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.status_text.configure(yscrollcommand=scrollbar.set)

    def _refresh_ports(self, log_message: bool = True) -> None:
        cli_error = ""
        self.detected_board_ports = []

        try:
            cli = ArduinoCli.from_environment()
            self.detected_board_ports = cli.list_supported_board_ports()
        except (ArduinoCliError, FileNotFoundError) as error:
            cli_error = str(error)

        ports = list_available_ports()
        self.port_display_to_device = {}

        for detected in self.detected_board_ports:
            board_name = detected.matched_board.display_name if detected.matched_board is not None else detected.board_name
            display = f"{detected.port} - {board_name}"
            self.port_display_to_device[display] = detected.port

        for port in ports:
            display = f"{port.device} - {port.description}"
            self.port_display_to_device.setdefault(display, port.device)

        values = list(self.port_display_to_device)
        self.port_combo.configure(values=values)

        selected_port = self._auto_populate_detected_connection()
        if not selected_port:
            if values and self.port_var.get() not in values:
                self.port_var.set(values[0])
            elif not values:
                self.port_var.set("")

        if log_message:
            if self.detected_board_ports:
                if len(self.detected_board_ports) == 1:
                    detected = self.detected_board_ports[0]
                    self._append_status(
                        f"Arduino CLI detected {detected.matched_board.display_name} on {detected.port}."
                    )
                else:
                    self._append_status(f"Arduino CLI detected {len(self.detected_board_ports)} supported board connection(s).")
            elif values:
                fallback_note = " Arduino CLI detection was unavailable." if cli_error else ""
                self._append_status(f"Found {len(values)} serial port(s).{fallback_note}")
            else:
                self._append_status("No serial ports detected.")

        if cli_error and not self.detected_board_ports:
            self.connection_summary_var.set("Arduino CLI not available. Showing serial ports only.")

    def _on_board_selected(self, _event=None) -> None:
        if self._auto_populate_detected_connection():
            selected_board = self._selected_board()
            self._append_status(f"Selected {selected_board.display_name}; port filled from Arduino CLI.")

    def _set_selected_port_by_device(self, port_device: str) -> bool:
        for display, device in self.port_display_to_device.items():
            if device == port_device:
                self.port_var.set(display)
                return True
        return False

    def _auto_populate_detected_connection(self) -> bool:
        if not self.detected_board_ports:
            if self.port_display_to_device:
                self.connection_summary_var.set("Select a board and port to continue.")
            else:
                self.connection_summary_var.set("Connect a board and refresh ports.")
            return False

        selected_board = self._selected_board()
        matching = [detected for detected in self.detected_board_ports if detected.matched_board == selected_board]

        if len(self.detected_board_ports) == 1:
            detected = self.detected_board_ports[0]
            if detected.matched_board is not None:
                self.board_var.set(detected.matched_board.display_name)
            self._set_selected_port_by_device(detected.port)
            self.connection_summary_var.set(
                f"Auto-detected {detected.matched_board.display_name} on {detected.port}."
            )
            return True

        if len(matching) == 1:
            detected = matching[0]
            self._set_selected_port_by_device(detected.port)
            self.connection_summary_var.set(
                f"Using Arduino CLI detection for {selected_board.display_name} on {detected.port}."
            )
            return True

        if matching:
            self.connection_summary_var.set(
                f"Multiple {selected_board.display_name} boards detected. Choose the correct port."
            )
            return False

        self.connection_summary_var.set("Select a detected board to auto-fill its port.")
        return False

    def _choose_output_dir(self) -> None:
        selected = filedialog.askdirectory(initialdir=self.output_dir_var.get() or str(DEFAULT_OUTPUT_DIR))
        if selected:
            self.output_dir_var.set(selected)

    def _run_system_check(self) -> None:
        report = run_system_check()
        self._append_status(render_system_check(report))

    def _on_lab_profile_selected(self, _event=None) -> None:
        profile_name = self.lab_profile_var.get().strip()
        if profile_name in LAB_PROFILE_ORDER:
            self._load_lab_profile(profile_name)

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
            self.signal_role_vars[index].set(signal.pulseox_role)

        for index in range(len(profile.signal_configurations), MAX_SIGNAL_COUNT):
            default_signal = self.default_config.signal_configurations[index]
            self.signal_name_vars[index].set(default_signal.name)
            self.signal_preset_vars[index].set(default_signal.preset_name)
            self.signal_port_vars[index].set(default_signal.analog_port)
            self.signal_role_vars[index].set(default_signal.pulseox_role)

        self.current_lab_var.set(f"Loaded lab: {profile.display_name}")
        self.firmware_summary_var.set(f"Firmware: {profile.firmware_label}. {profile.note}")
        self._apply_signal_count()

        if log_message:
            self._append_status(
                f"Loaded {profile.display_name} profile with {len(profile.signal_configurations)} signal(s)."
            )

    def _selected_firmware_label(self) -> str:
        if self.current_lab_profile is not None:
            return self.current_lab_profile.firmware_label
        return "Generated UNO R4 WiFi Acquisition Firmware"

    def _setup_arduino_cli(self) -> None:
        self._run_cli_task("Arduino CLI setup", self._setup_arduino_cli_task)

    def _compile_demo_firmware(self) -> None:
        self._run_cli_task(f"Firmware compile ({self._selected_firmware_label()})", self._compile_demo_firmware_task)

    def _upload_demo_firmware(self) -> None:
        self._run_cli_task(f"Firmware upload ({self._selected_firmware_label()})", self._upload_demo_firmware_task)

    def _setup_arduino_cli_task(self) -> None:
        cli = ArduinoCli.from_environment()
        cli.update_index()
        cli.install_core(self._selected_board().core)

    def _compile_demo_firmware_task(self) -> None:
        board = self._selected_board()
        cli = ArduinoCli.from_environment()
        return cli.compile_generated_analog_capture(
            signal_configurations=self._selected_signal_configurations(),
            fqbn=board.fqbn,
            baud_rate=self.default_config.baud_rate,
        )

    def _upload_demo_firmware_task(self) -> None:
        board = self._selected_board()
        cli = ArduinoCli.from_environment()

        selected_port = self._selected_port_device()
        if not selected_port:
            selected_port = cli.detect_port_for_board(board)

        compile_artifact = cli.compile_generated_analog_capture(
            signal_configurations=self._selected_signal_configurations(),
            fqbn=board.fqbn,
            baud_rate=self.default_config.baud_rate,
        )
        cli.upload(compile_artifact.sketch_dir, board.fqbn, selected_port)
        return compile_artifact

    def _run_cli_task(self, task_name: str, task_function) -> None:
        if self.cli_task_running:
            messagebox.showinfo("Busy", "Wait for the current Arduino CLI task to finish.")
            return

        self.cli_task_running = True
        self._set_cli_buttons_state("disabled")
        self._append_status(f"Starting {task_name}...")

        def worker() -> None:
            try:
                result = task_function()
            except Exception as error:
                self.background_queue.put(("message", SessionMessage(level="error", text=f"{task_name} failed: {error}")))
            else:
                self.background_queue.put(("message", SessionMessage(level="info", text=f"{task_name} finished.")))
                if result and getattr(result, "acquisition_class", "") == "PHASED_CYCLE":
                    joined_ports = ", ".join(result.analog_ports)
                    self.background_queue.put(
                        (
                            "message",
                            SessionMessage(
                                level="info",
                                text=(
                                    f"Generated PHASED_CYCLE Arduino code at {result.cycle_rate_hz} cycles/s "
                                    f"({result.phase_rate_hz} phase samples/s) for ports {joined_ports}."
                                ),
                            ),
                        )
                    )
                elif result and hasattr(result, "sample_rate_hz") and hasattr(result, "analog_ports"):
                    joined_ports = ", ".join(result.analog_ports)
                    self.background_queue.put(
                        (
                            "message",
                            SessionMessage(
                                level="info",
                                text=f"Generated Arduino code at {result.sample_rate_hz} Hz for ports {joined_ports}.",
                            ),
                        )
                    )
                if result and getattr(result, "uses_pulseox_led_cycle", False):
                    self.background_queue.put(
                        (
                            "message",
                            SessionMessage(
                                level="info",
                                text="PulseOx phased cycle enabled: D6=RED, D5=IR, PHASE packets plus corrected CYCLE packets.",
                            ),
                        )
                    )
                if result and hasattr(result, "snapshot_path"):
                    self.background_queue.put(
                        ("message", SessionMessage(level="info", text=f"Saved Arduino code copy to {result.snapshot_path}"))
                    )
                elif result:
                    self.background_queue.put(
                        ("message", SessionMessage(level="info", text=f"Saved Arduino code copy to {result}"))
                    )
            finally:
                self.background_queue.put(("cli_task_done", None))

        threading.Thread(target=worker, daemon=True).start()

    def _set_cli_buttons_state(self, state: str) -> None:
        self.setup_cli_button.configure(state=state)
        self.compile_button.configure(state=state)
        self.upload_button.configure(state=state)

    def _selected_board(self):
        for board in SUPPORTED_BOARDS:
            if board.display_name == self.board_var.get():
                return board
        return UNO_R4_WIFI_BOARD

    def _selected_port_device(self) -> str:
        return self.port_display_to_device.get(self.port_var.get(), self.port_var.get().strip())

    def _selected_signal_configurations(self) -> tuple[SignalConfiguration, ...]:
        signal_count = int(self.signal_count_var.get())
        return tuple(
            SignalConfiguration(
                name=self.signal_name_vars[index].get().strip(),
                preset_name=self.signal_preset_vars[index].get(),
                analog_port=self.signal_port_vars[index].get(),
                pulseox_role=self.signal_role_vars[index].get(),
            )
            for index in range(signal_count)
        )

    def _plot_signal_configurations(self) -> tuple[SignalConfiguration, ...]:
        if self.session is not None:
            return self.session.config.signal_configurations
        return self._selected_signal_configurations()

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

        self._refresh_signal_reference_text(signal_count)
        self._apply_subplot_count(reset_assignments=True)

    def _refresh_signal_reference_text(self, signal_count: int | None = None) -> None:
        if signal_count is None:
            try:
                signal_count = int(self.signal_count_var.get())
            except tk.TclError:
                signal_count = DEFAULT_ACTIVE_SIGNAL_COUNT

        active_names = [self.signal_name_vars[index].get() for index in range(max(0, min(MAX_SIGNAL_COUNT, signal_count)))]
        self.plot_signal_reference_var.set(format_signal_reference_text(active_names))

    def _apply_subplot_count(self, reset_assignments: bool = True) -> None:
        if self.updating_subplot_controls:
            return

        try:
            requested_subplot_count = int(self.subplot_count_var.get())
        except tk.TclError:
            requested_subplot_count = 1

        signal_count = len(self._plot_signal_configurations())
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
        signal_configurations = self._plot_signal_configurations()
        if not signal_configurations:
            return
        self._rebuild_plot_layout(signal_configurations)

    def _update_signal_preset_info(self, row_index: int) -> None:
        preset_name = self.signal_preset_vars[row_index].get()
        info_label = self.signal_rows[row_index][1]
        role_combo = self.signal_role_combos[row_index]

        if preset_name not in LAB_PRESETS:
            info_label.configure(text="Unknown preset")
            role_combo.configure(state="disabled")
            return

        preset = get_preset(preset_name)
        rate_text = (
            f"{preset.default_sample_rate_hz} samples/s"
            if preset.default_sample_rate_hz is not None
            else f"{preset.default_cycle_rate_hz} cycles/s"
        )
        packets = "/".join(preset.packet_types)
        if preset_name == "PulseOx":
            role_combo.configure(state="readonly")
            role_text = self.signal_role_vars[row_index].get()
            if role_text == PULSEOX_ROLE_AUTO:
                role_note = "Choose RED or IR"
            else:
                role_note = f"Role: {role_text}"
            info_label.configure(text=f"{preset.acquisition_class} | {rate_text} | {packets} | {role_note}")
            return

        if self.signal_role_vars[row_index].get() != PULSEOX_ROLE_AUTO:
            self.signal_role_vars[row_index].set(PULSEOX_ROLE_AUTO)
        role_combo.configure(state="disabled")
        info_label.configure(
            text=f"{preset.acquisition_class} | {rate_text} | {packets}",
        )

    def _build_gui_config(self) -> GuiAcquisitionConfig:
        signal_count = int(self.signal_count_var.get())
        signal_configurations = []

        for index in range(signal_count):
            signal_configurations.append(
                SignalConfiguration(
                    name=self.signal_name_vars[index].get().strip(),
                    preset_name=self.signal_preset_vars[index].get(),
                    analog_port=self.signal_port_vars[index].get(),
                    pulseox_role=self.signal_role_vars[index].get(),
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
        self._reset_plot(config.signal_configurations)

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

    def _reset_plot(self, signal_configurations: tuple[SignalConfiguration, ...]) -> None:
        self.plot_time_s = deque(maxlen=2500)
        self.plot_signal_values = [deque(maxlen=2500) for _ in signal_configurations]
        self.plot_history_seconds = max(get_preset(signal.preset_name).plotting.history_seconds for signal in signal_configurations)
        self._rebuild_plot_layout(signal_configurations)

    def _rebuild_plot_layout(self, signal_configurations: tuple[SignalConfiguration, ...]) -> None:
        if not signal_configurations:
            return

        signal_count = len(signal_configurations)
        try:
            requested_subplot_count = int(self.subplot_count_var.get())
        except tk.TclError:
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
                    signal = signal_configurations[signal_index]
                    line, = axis.plot(
                        [],
                        [],
                        label=signal.name,
                        color=PLOT_COLORS[signal_index % len(PLOT_COLORS)],
                        linewidth=1.8,
                    )
                    line_group[signal_index] = line

                axis.set_title(self._subplot_title(subplot_index, signal_configurations, selected_indices))
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
        signal_configurations: tuple[SignalConfiguration, ...],
        selected_indices: tuple[int, ...],
    ) -> str:
        selected_names = ", ".join(signal_configurations[signal_index].name for signal_index in selected_indices)
        return f"Subplot {subplot_index + 1}: {selected_names}"

    def _append_sample(self, sample: SessionSample) -> None:
        if not self.plot_signal_values:
            return

        self.plot_time_s.append(sample.device_time_ms / 1000.0)
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

    def _append_status(self, message: str) -> None:
        self.status_text.configure(state="normal")
        self.status_text.insert("end", f"{message}\n")
        self.status_text.see("end")
        self.status_text.configure(state="disabled")

    def _poll_background_work(self) -> None:
        plot_updated = False

        while True:
            try:
                item_type, payload = self.background_queue.get_nowait()
            except Empty:
                break

            if item_type == "message":
                self._append_status(payload.text)
            elif item_type == "cli_task_done":
                self.cli_task_running = False
                self._set_cli_buttons_state("normal")

        if self.session is not None:
            while True:
                try:
                    sample = self.session.sample_queue.get_nowait()
                except Empty:
                    break

                self._append_sample(sample)
                plot_updated = True

            while True:
                try:
                    message = self.session.message_queue.get_nowait()
                except Empty:
                    break

                self._append_status(message.text)

            if not self.session.is_running():
                self.session.join(timeout=0.0)
                self.session = None
                self._set_acquisition_controls(running=False)

        if plot_updated:
            self._refresh_plot()

        self.root.after(100, self._poll_background_work)


def main() -> int:
    root = tk.Tk()
    app = StudentAcquisitionGui(root)

    def on_close() -> None:
        if app.session is not None:
            app.session.stop()
            app.session.join(timeout=2.0)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()
    return 0
