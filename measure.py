import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import re
import signal
import sys
import threading
import serial

x_data = []
y_data = []
milisseconds_beginning = 0
current_aggregate = 0
current_max = 0
readed_line_regex = re.compile('^(?P<time>[0-9.]+?) (?P<current>[0-9.]+?)[\t\s\n]+$')

figure = plt.figure(figsize=(12, 6), facecolor='#DEDEDE')
ax = figure.add_subplot(111)
signal.signal(signal.SIGINT, lambda sig, frame: plt.close('all'))


class TailSerial():
    def __init__(self, serial, callback_line=sys.stdout.write):
        self.serial = serial
        self.callback_line = callback_line
        self.should_stop = False

    def stop(self):
        self.should_stop = True

    def follow(self):
        while True:
            line = serial.readline().decode("utf-8")
            self.callback_line(line)
            if (self.should_stop):
                break

        print("Stop following file!")
        self.should_stop = False


def append_data_from_line(line):
    global current_aggregate
    global current_max
    global milisseconds_beginning
    matches = readed_line_regex.match(line)
    if not (matches):
        return False

    data_to_plot = [
        int(matches.group('time')),
        float(matches.group('current'))
    ]

    if len(x_data) == 0:
        milisseconds_beginning = data_to_plot[0]

    print(data_to_plot)
    x_data.append(data_to_plot[0] - milisseconds_beginning)
    y_data.append(data_to_plot[1])

    current_aggregate += data_to_plot[1]
    if (data_to_plot[1] > current_max):
        current_max = data_to_plot[1]

    return True


def plot_chart():
    if (len(x_data) == 0 or len(x_data) % 100 != 0):
        return

    plt.cla()
    ax.set_facecolor('#DEDEDE')
    ax.set_xlabel('Milliseconds')
    ax.set_ylabel('Current (mA)')
    ax.set_title('mA\n')

    x_last = x_data[-1]
    y_last = y_data[-1]
    ax.plot(x_data, y_data, c='#EC5E29')
    ax.text(x_last, y_last, "{} mA".format(y_last))
    ax.scatter(x_last, y_last, c='#EC5E29')

    avg_current = round(current_aggregate/len(y_data), 2)
    consumption = avg_current*(x_data[-1] - x_data[0])/(3.6*10**6)
    handles = [
        mpatches.Patch(
            label=f"avg current: {avg_current} mA",
            visible=False),
        mpatches.Patch(
            label=f"max current: {round(current_max, 2)} mA",
            visible=False),
        mpatches.Patch(
            label=f"consumption: {round(consumption, 3)} mAh",
            visible=False)
    ]
    plt.legend(handles=handles, loc="upper right")
    plt.draw()


def plot_data_from_serial(serial):
    tail = TailSerial(
        serial,
        lambda line: plot_chart() if append_data_from_line(line) else 0
    )

    follow_serial = lambda x: tail.follow()
    serial_observer_thread = threading.Thread(target=follow_serial, args=(1,))
    serial_observer_thread.setDaemon(True)
    serial_observer_thread.start()


if __name__ == "__main__":
    if (len(sys.argv) <= 1):
        print("\033[91m [FAIL] Missing serial port")
        sys.exit(-1)

    if (len(sys.argv) <= 2):
        print(f"\033[91m [FAIL] Missing baudrate for port \"`{sys.argv[1]}`\"")
        sys.exit(-1)

    serial = serial.Serial(sys.argv[1], sys.argv[2], timeout=5)
    serial.close()
    serial.open()

    plot_data_from_serial(serial)

    plt.show()
    sys.exit(0)
