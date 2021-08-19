import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import re
import signal
import sys
import threading
import serial

signal.signal(signal.SIGINT, lambda sig, frame: plt.close('all'))
readed_line_regex = re.compile('^(?P<time>[0-9.]+?) (?P<current>[0-9.]+?)[\t\s\n]+$')


class TailSerial():
    def __init__(self, serial, callback_line=sys.stdout.write):
        self.serial = serial
        self.callback_line = callback_line

    def follow(self):
        while True:
            line = self.serial.readline()
            try:
                self.callback_line(line.decode("utf-8"))
            except ValueError:
                pass


class ElectricalCurrentChart():
    def __init__(self, subplot=111):
        figure = plt.figure(figsize=(12, 6), facecolor='#DEDEDE')
        self.ax = figure.add_subplot(subplot)
        self.x_data = []
        self.y_data = []
        self.reads = 0
        self.milisseconds_at_begin = 0
        self.max_current = 0
        self.aggregated_current = 0
        self.setup()

    def append_data(self, milliseconds, current):
        print([milliseconds, current])
        self.reads += 1

        if len(self.x_data) == 0:
            self.milisseconds_at_begin = milliseconds

        # Prevents to plot more than two repeated values
        if len(self.y_data) >= 2:
            if (current == self.y_data[-1] and self.y_data[-1] == self.y_data[-2]):
                self.y_data.pop()
                self.x_data.pop()

        self.x_data.append(milliseconds - self.milisseconds_at_begin)
        self.y_data.append(current)

        self.aggregated_current += current
        if (current > self.max_current):
            self.max_current = current

    def setup(self):
        plt.cla()
        self.ax.set_facecolor('#DEDEDE')
        self.ax.set_xlabel('Milliseconds')
        self.ax.set_ylabel('Current (mA)')
        self.ax.set_title('Power Consumption\n')

    def plot(self):
        # Plot once each 100 reads
        if (self.reads == 0 or self.reads % 100 != 0):
            return

        self.setup()
        x_last = self.x_data[-1]
        y_last = self.y_data[-1]
        self.ax.plot(self.x_data, self.y_data)
        self.ax.text(x_last, y_last, "{} mA".format(y_last))
        self.ax.scatter(x_last, y_last)

        avg_current = self.aggregated_current/len(self.y_data)
        consumption = avg_current*(self.x_data[-1] - self.x_data[0])/(3.6*10**6)
        label =  f"Reads: {self.reads}\n"
        label += f"Avg current: {'{:.4f}'.format(round(avg_current, 4))} mA\n"
        label += f"Max current: {'{:.4f}'.format(round(self.max_current, 4))} mA\n"
        label += f"Consumption: {'{:.4f}'.format(round(consumption, 4))} mAh"
        plt.legend(handles=[mpatches.Patch(label=label)], loc="upper right")
        plt.draw()


def append_line_in_chart(chart, line):
    matches = readed_line_regex.match(line)
    if not (matches):
        return

    chart.append_data(
        int(matches.group('time')),
        float(matches.group('current'))
    )
    chart.plot()


def observe_serial(port, baudrate, on_new_line):
    serial_port = serial.Serial(port, baudrate)
    serial_port.close()
    serial_port.open()

    tail_serial = TailSerial(serial_port, on_new_line)
    serial_follow = threading.Thread(target=lambda x: tail_serial.follow(), args=(1,))
    serial_follow.setDaemon(True)
    serial_follow.start()


if __name__ == "__main__":
    if (len(sys.argv) <= 1):
        print("\033[91m [FAIL] Missing serial port")
        sys.exit(-1)

    if (len(sys.argv) <= 2):
        print(f"\033[91m [FAIL] Missing baudrate for port \"`{sys.argv[1]}`\"")
        sys.exit(-1)

    chart = ElectricalCurrentChart()
    observe_serial(
        sys.argv[1],
        sys.argv[2],
        lambda line: append_line_in_chart(chart, line))

    plt.show()

    sys.exit(0)
