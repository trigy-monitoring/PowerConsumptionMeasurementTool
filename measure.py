import matplotlib.pyplot as plt
import re
import subprocess
import sys
import threading
import time

x_data = []
y_data = []
readed_line_regex = re.compile('^(?P<time>[0-9.]+?) (?P<current>[0-9.]+?)[\t\s\n]+$')

figure = plt.figure(figsize=(12, 6), facecolor='#DEDEDE')
ax = figure.add_subplot(111)
ax.set_facecolor('#DEDEDE')
ax.set_xlabel('Seconds')
ax.set_ylabel('Current (mA)')
ax.set_title('mA\n')


class Tail():
    def __init__(self, file_name, callback_line=sys.stdout.write):
        self.file_name = file_name
        self.callback_line = callback_line

    def follow(self):
        command = subprocess.Popen(
            ['tail', '-f', self.file_name],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        while True:
            line = command.stdout.readline().decode("utf-8")
            self.callback_line(line)
            time.sleep(0.01)


def append_data_from_line(line):
    matches = readed_line_regex.match(line)
    if not (matches):
        return False

    data_to_plot = [
        float(matches.group('time')),
        float(matches.group('current'))
    ]

    print(data_to_plot)
    x_data.append(data_to_plot[0])
    y_data.append(data_to_plot[1])

    return True


def plot_chart():
    plt.cla()
    x_last = x_data[-1]
    y_last = y_data[-1]
    ax.plot(x_data, y_data, c='#EC5E29')
    ax.text(x_last, y_last, "{} mA".format(x_last))
    ax.scatter(x_last, y_last, c='#EC5E29')
    plt.draw()


def observe_file_within_thread(path_to_observe):
    tail = Tail(
        path_to_observe,
        lambda line: plot_chart() if append_data_from_line(line) else 0
    )
    follow_file = lambda x: tail.follow()
    file_observer_thread = threading.Thread(target=follow_file, args=(1,))
    file_observer_thread.start()


if __name__ == "__main__":
    if (len(sys.argv) <= 1):
        print("[FAIL] Missing path to read.")
        sys.exit(-1)

    path_to_observe = sys.argv[1]
    observe_file_within_thread(path_to_observe)

    plt.show()
