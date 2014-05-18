#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#
# This file is part of Coruja-scripts
#
# Coruja-scripts is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Coruja-scripts is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Coruja-scripts.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2011 Grupo Falabrasil - http://www.laps.ufpa.br/falabrasil
#
# Author 2011: Pedro Batista - pedosb@gmail.com

import numpy as np


class SignalError(Exception):
    pass


class Signal():
    def __init__(self, data, fs, window=None, window_len=None, frame_rate=None):
        self.data = data
        self.fs = fs
        self.frame_rate = frame_rate
        self.set_window(window, window_len)

    def set_window(self, window=None, window_len=None):
        if window is None and window_len is not None:
            self.window = np.hamming(self.fs * window_len)
        elif window is not None:
            self.window = window
        elif window_len is None:
            raise SignalError("Window size or Window is required")

    def get_frame(self, m, frame_rate=None):
        if self.frame_rate is None and frame_rate is None:
            raise SignalError("The frame_rate is required")

        if self.window is None:
            raise SignalError("A Window is required try call Signal.set_window")

        if m > len(self.data) - len(self.window):
            return 0
        elif m < 0:
            return 0
        return self.data[m:m + len(self.window)] * self.window

    def get_frames_positions(self):
        frames = np.arange(0, len(self.data), self.fs / self.frame_rate)
        frames = frames[frames < len(self.data) - len(self.window) - 1]
        return frames

    def get_number_of_frames(self):
        return len(self.get_frames_positions())

    def power(self, m):
        return sum(self.get_frame(m) ** 2)