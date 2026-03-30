from __future__ import annotations

from tkinter import ttk

from acquisition.arduino_cli_wrapper import ArduinoCli, ArduinoCliError, SUPPORTED_BOARDS
from acquisition.serial_tools import list_available_ports
from acquisition.system_check import render_system_check, run_system_check


class ConnectionMixin:
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

    def _refresh_ports(self, log_message: bool = True) -> None:
        cli_error = ""
        self.detected_board_ports = []
        cli_available = True

        try:
            cli = ArduinoCli.from_environment()
            self.detected_board_ports = cli.list_supported_board_ports()
        except (ArduinoCliError, FileNotFoundError) as error:
            cli_error = str(error)
            cli_available = False

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
                    self._append_status(
                        f"Arduino CLI detected {len(self.detected_board_ports)} supported board connection(s)."
                    )
            elif values:
                fallback_note = " Arduino CLI detection was unavailable." if cli_error else ""
                self._append_status(f"Found {len(values)} serial port(s).{fallback_note}")
            else:
                self._append_status("No serial ports detected.")

        self.cli_available = cli_available
        self.cli_last_error = cli_error
        if not cli_available and not self.detected_board_ports:
            self.connection_summary_var.set("Arduino CLI not available. Showing serial ports only.")
            if not getattr(self, "_auto_system_check_ran", False):
                self._auto_system_check_ran = True
                report = run_system_check()
                self._append_status(render_system_check(report))

        if hasattr(self, "_refresh_cli_button_state"):
            self._refresh_cli_button_state()

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

    def _run_system_check(self) -> None:
        report = run_system_check()
        self._append_status(render_system_check(report))
