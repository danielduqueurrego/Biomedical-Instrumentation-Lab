from __future__ import annotations

from queue import Empty

import tkinter as tk
from tkinter import ttk

from acquisition.student_gui.constants import GUI_POLL_INTERVAL_MS


class StatusMixin:
    def _build_status_frame(self, parent: ttk.Frame) -> None:
        self.status_text = tk.Text(parent, height=12, wrap="word")
        self.status_text.grid(row=0, column=0, sticky="nsew")
        self.status_text.configure(state="disabled")

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.status_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.status_text.configure(yscrollcommand=scrollbar.set)

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

        self.root.after(GUI_POLL_INTERVAL_MS, self._poll_background_work)
