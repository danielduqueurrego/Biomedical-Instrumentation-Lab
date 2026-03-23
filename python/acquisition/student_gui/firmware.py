from __future__ import annotations

import threading
from tkinter import messagebox, ttk

from acquisition.arduino_cli_wrapper import ArduinoCli, ArduinoCliError
from acquisition.gui_session import SessionMessage


class FirmwareMixin:
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

    def _compile_demo_firmware_task(self):
        board = self._selected_board()
        cli = ArduinoCli.from_environment()
        return cli.compile_generated_analog_capture(
            signal_configurations=self._selected_signal_configurations(),
            fqbn=board.fqbn,
            baud_rate=self.default_config.baud_rate,
        )

    def _upload_demo_firmware_task(self):
        board = self._selected_board()
        cli = ArduinoCli.from_environment()

        detected_ports = [
            detected_board.port
            for detected_board in cli.list_supported_board_ports()
            if detected_board.matched_board is not None and detected_board.matched_board.fqbn == board.fqbn
        ]
        if not detected_ports:
            raise ArduinoCliError(
                f"No {board.display_name} board was detected. Connect the board, click Refresh Ports, and try again."
            )

        selected_port = self._selected_port_device()
        if selected_port and selected_port not in detected_ports:
            if len(detected_ports) == 1:
                selected_port = detected_ports[0]
            else:
                joined_ports = ", ".join(detected_ports)
                raise ArduinoCliError(
                    f"The selected port is no longer available for {board.display_name}. "
                    f"Choose one of the detected ports: {joined_ports}."
                )
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
                                text=(
                                    "PulseOx phased cycle enabled: D6=RED, D5=IR, A0-A3 sampled on every phase, "
                                    "PHASE packets plus corrected CYCLE packets."
                                ),
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
