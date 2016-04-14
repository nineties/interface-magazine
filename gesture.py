import numpy as np
import time
from threading import Thread, Event
from Queue import Queue
from mpu6050 import MPU6050
from scipy.signal import savgol_filter

class GestureExtractor(object):
    def __init__(self, min_len=0.5, max_len=5.0, n_points=100, n_fft=21, wsize=20, sigma=0.25):
        self.min_len = min_len
        self.max_len = max_len
        self.n_points = n_points
        self.n_fft = n_fft
        self.wsize = wsize
        self.var_thresh = sigma**2
        self.sensor = MPU6050(normalize=True)

    def _feeder(self, queue, stop):
        while not stop.is_set():
            if not queue.full():
                queue.put(self.sensor.get())
            time.sleep(0.01)

    def _get_truncated_data(self):
        queue = Queue(100)
        stop = Event()
        feeder = Thread(target=self._feeder, args=(queue, stop))
        feeder.daemon = True
        feeder.start()

        data = []
        # Fill initial window
        for i in range(self.wsize):
            data.append(queue.get())

        while True:
            # Wait until the sensor become calm
            while np.var(data) > self.var_thresh:
                data.pop(0)
                data.append(queue.get())

            # Wait until the beginning of gesture
            while np.var(data) < self.var_thresh:
                data.pop(0)
                data.append(queue.get())

            # Start capturing the gesture
            gesture_start = time.time()
            while np.var(data[-self.wsize:]) >= self.var_thresh:
                data.append(queue.get())
            gesture_len = time.time() - gesture_start

            if gesture_len < self.min_len or gesture_len > self.max_len:
                data = data[-self.wsize:]
                continue

            stop.set()
            feeder.join()
            return data

    def _smooth(self, data):
        for i in range(6):
            data[i,:] = savgol_filter(data[i,:], 5, 5)

    def get(self):
        data = self._get_truncated_data()
        data = np.array(data)
        data = self._smooth(data)
        print len(data)
