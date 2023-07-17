import random
import time

class DescentIterator:
    def __init__(self, gradient_x, gradient_y, convergence_rate):
        self._gradient_x = gradient_x
        self._gradient_y = gradient_y
        self._convergence_rate = convergence_rate
        self._x = 0.0
        self._y = 0.0

    @staticmethod
    def _init_generator():
        seed = [int(time.monotonic_ns())]
        random.seed(seed)

    def reset_state(self, x, y):
        self._x = x
        self._y = y

    def random_state(self, half_extent_x, half_extent_y):
        dist_x = random.uniform(-half_extent_x, half_extent_x)
        self._x = dist_x
        dist_y = random.uniform(-half_extent_y, half_extent_y)
        self._y = dist_y

    def iterate(self):
        tmp_x = self._x
        tmp_y = self._y
        self._x = tmp_x - self._convergence_rate * self._gradient_x(tmp_x, tmp_y)
        self._y = tmp_y - self._convergence_rate * self._gradient_y(tmp_x, tmp_y)

    def get_state(self):
        return self._x, self._y
