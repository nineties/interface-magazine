import time
import socket
import struct
import numpy as np
import matplotlib.pyplot as plt
from threading import Thread, Lock

data_lock = Lock()
ts = []     # time stamps
ds = []     # data series

def receiver():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('192.168.1.26', 9000))
    while True:
        msg = sock.recv(7*4)
        t, = struct.unpack('f', msg[:4])
        d = struct.unpack('6f', msg[4:])

        with data_lock:
            ts.append(t)
            ds.append(d)

def plotter():
    labels = ['acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z']
    W = 5

    plt.ion()
    axes = []
    for i in range(6):
        axes.append(plt.plot([], [], label=labels[i])[0])
    plt.legend(loc=2)
    plt.show()

    while True:
        with data_lock:
            if not ts:
                continue

            t = ts[-1]
            while ts[0] < t-W:
                ts.pop(0)
                ds.pop(0)
            T = np.array(ts)
            D = np.array(ds)

        for i in range(6):
            axes[i].set_data(T, D[:, i])
        plt.xlim(t-W, t)
        plt.ylim(-1.5, 1.5)
        plt.draw()
        plt.pause(0.1)

th = Thread(target=receiver)
th.daemon = True
th.start()
plotter()
