from collections import deque
from queue import Empty, SimpleQueue

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from acquisition.protocol import DataPacket


class ThreeChannelLivePlot:
    """Keeps a short rolling window of three channels for live display."""

    def __init__(
        self,
        packet_queue: SimpleQueue,
        channel_labels: tuple[str, str, str] = ("ch1", "ch2", "ch3"),
        history_seconds: float = 10.0,
        update_interval_ms: int = 100,
    ):
        self.packet_queue = packet_queue
        self.channel_labels = channel_labels
        self.history_seconds = history_seconds
        self.update_interval_ms = update_interval_ms
        self.max_points = max(1500, int(history_seconds * 150 * 2))

        self.time_s = deque(maxlen=self.max_points)
        self.ch1 = deque(maxlen=self.max_points)
        self.ch2 = deque(maxlen=self.max_points)
        self.ch3 = deque(maxlen=self.max_points)

        self.figure, self.axis = plt.subplots(figsize=(10, 6))
        self.lines = [
            self.axis.plot([], [], label=channel_labels[0])[0],
            self.axis.plot([], [], label=channel_labels[1])[0],
            self.axis.plot([], [], label=channel_labels[2])[0],
        ]

        self.axis.set_title("CONT_MED Three-Channel Demo")
        self.axis.set_xlabel("Device time (s)")
        self.axis.set_ylabel("ADC value")
        self.axis.grid(True)
        self.axis.legend(loc="upper right")

        self._animation = None
        self._should_stop = lambda: False
        self._on_close = lambda: None

    def show(self, should_stop, on_close) -> None:
        self._should_stop = should_stop
        self._on_close = on_close
        self.figure.canvas.mpl_connect("close_event", self._handle_close)
        self._animation = FuncAnimation(
            self.figure,
            self._update_plot,
            interval=self.update_interval_ms,
            blit=False,
            cache_frame_data=False,
        )
        plt.tight_layout()
        plt.show()

    def _handle_close(self, _event) -> None:
        self._on_close()

    def _update_plot(self, _frame_number):
        if self._should_stop():
            plt.close(self.figure)
            return self.lines

        new_samples = self._drain_queue()
        if new_samples == 0 and not self.time_s:
            return self.lines

        self._refresh_lines()
        return self.lines

    def _drain_queue(self) -> int:
        sample_count = 0

        while True:
            try:
                packet: DataPacket = self.packet_queue.get_nowait()
            except Empty:
                break

            if len(packet.values) != 3:
                continue

            sample_count += 1
            self.time_s.append(packet.device_time_us / 1_000_000.0)
            self.ch1.append(packet.values[0])
            self.ch2.append(packet.values[1])
            self.ch3.append(packet.values[2])

        return sample_count

    def _refresh_lines(self) -> None:
        x_values = list(self.time_s)
        y_values = [list(self.ch1), list(self.ch2), list(self.ch3)]

        for line, channel_values in zip(self.lines, y_values):
            line.set_data(x_values, channel_values)

        latest_time = x_values[-1]
        left_edge = max(0.0, latest_time - self.history_seconds)
        right_edge = max(self.history_seconds, latest_time)
        self.axis.set_xlim(left_edge, right_edge)

        visible_values = []
        for timestamp, value_1, value_2, value_3 in zip(x_values, self.ch1, self.ch2, self.ch3):
            if timestamp >= left_edge:
                visible_values.extend([value_1, value_2, value_3])

        if not visible_values:
            visible_values = [0, 1]

        min_value = min(visible_values)
        max_value = max(visible_values)
        padding = max(10.0, (max_value - min_value) * 0.05)
        self.axis.set_ylim(min_value - padding, max_value + padding)
