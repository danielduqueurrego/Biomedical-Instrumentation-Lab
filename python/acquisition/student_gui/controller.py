from __future__ import annotations

import tkinter as tk
from queue import SimpleQueue
from tkinter import ttk

from acquisition.arduino_cli_wrapper import UNO_R4_WIFI_BOARD
from acquisition.gui_models import DEFAULT_ACTIVE_SIGNAL_COUNT, default_gui_config
from acquisition.lab_profiles import LAB_PROFILE_ORDER
from acquisition.student_gui.connection import ConnectionMixin
from acquisition.student_gui.constants import DEFAULT_OUTPUT_DIR, GUI_POLL_INTERVAL_MS
from acquisition.student_gui.firmware import FirmwareMixin
from acquisition.student_gui.plotting import PlottingMixin
from acquisition.student_gui.session_controls import SessionControlsMixin
from acquisition.student_gui.signals import SignalConfigurationMixin
from acquisition.student_gui.status import StatusMixin


class StudentAcquisitionGui(
    ConnectionMixin,
    FirmwareMixin,
    SignalConfigurationMixin,
    PlottingMixin,
    SessionControlsMixin,
    StatusMixin,
):
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Biomedical Instrumentation Lab")
        self.root.geometry("1280x820")
        self.root.minsize(1120, 720)

        self.default_config = default_gui_config(DEFAULT_OUTPUT_DIR)
        self.session = None
        self.background_queue: SimpleQueue = SimpleQueue()
        self.cli_task_running = False
        self.cli_available = True
        self.cli_last_error = ""
        self._auto_system_check_ran = False

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

        self.port_display_to_device = {}
        self.detected_board_ports = []
        self.signal_name_vars = []
        self.signal_preset_vars = []
        self.signal_port_vars = []
        self.signal_port_combos = []
        self.signal_rows = []
        self.lab_profile_combo = None
        self.current_lab_profile = None
        self.subplot_count_spinbox = None
        self.subplot_rows = []
        self.subplot_signal_vars = []
        self.subplot_checkbuttons = []
        self.updating_subplot_controls = False
        self.plot_axes = []
        self.plot_line_groups = []
        self.plot_time_s = None
        self.plot_signal_values = []
        self.plot_history_seconds = 10.0
        self.controls_visible = True
        self.status_visible = True
        self.controls_container = None
        self.status_area = None
        self.controls_canvas = None
        self.controls_frame = None
        self.controls_window_id = None

        self._build_ui()
        self._bind_scroll_events()
        self._refresh_output_basename()
        self._refresh_ports(log_message=False)
        self._apply_signal_count()
        self._refresh_plot_preview()
        self._append_status("Ready.")
        self.root.after(GUI_POLL_INTERVAL_MS, self._poll_background_work)

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

        ttk.Button(selector_row, text="Load Preset", command=self._load_session_preset_from_file).grid(
            row=0,
            column=2,
            sticky="e",
            padx=(8, 0),
        )
        ttk.Button(selector_row, text="Save Preset", command=self._save_session_preset_to_file).grid(
            row=0,
            column=3,
            sticky="e",
            padx=(8, 0),
        )
        ttk.Button(
            selector_row,
            textvariable=self.controls_toggle_label_var,
            command=self._toggle_controls_panel,
        ).grid(row=0, column=4, sticky="e", padx=(8, 0))
        ttk.Button(
            selector_row,
            textvariable=self.status_toggle_label_var,
            command=self._toggle_status_panel,
        ).grid(row=0, column=5, sticky="e", padx=(8, 0))

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
