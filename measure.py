import matplotlib.pyplot as plt
import sys
import threading
import subprocess

toPlotX = []
toPlotY = []

fig = plt.figure(figsize=(12, 6), facecolor='#DEDEDE')
ax = fig.add_subplot(111)
ax.set_facecolor('#DEDEDE')
ax.set_xlabel('Seconds')
ax.set_ylabel('Current (mA)')
ax.set_title('mA\n')


class Tail():
    def __init__(self, file_name, callback=sys.stdout.write):
        self.file_name = file_name
        self.callback = callback

    def follow(self):
        f = subprocess.Popen(['tail', '-f', self.file_name], \
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        while True:
            line = f.stdout.readline().decode("utf-8")
            self.callback(line)


def plot_chart(line, plt):
    if (line == "\n"):
        return

    splittedLine = line.split(" ")
    if (len(splittedLine) != 2):
        return

    print(splittedLine)
    toPlotX.append(int(splittedLine[0]))
    toPlotY.append(int(splittedLine[1]))

    plt.cla()
    ax.plot(toPlotX, toPlotY, c='#EC5E29')
    ax.text(toPlotX[-1], toPlotY[-1], "{} mA".format(splittedLine[1]))
    ax.scatter(toPlotX[-1], toPlotY[-1], c='#EC5E29')

    plt.draw()


def observeFile(pathToObserve, plt):
    tail = Tail(pathToObserve, lambda line: plot_chart(line, plt))
    tail.follow()


if __name__ == "__main__":
    if (len(sys.argv) <= 1):
        print("[FAIL] Missing path to read.")
        exit(-1)

    pathToRead = sys.argv[1]

    fileObserverThread = (threading
        .Thread(target=lambda x: observeFile(pathToRead, plt), args=(1,))
        .start())

    plt.show()
