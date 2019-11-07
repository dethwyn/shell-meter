from math import tan, atan, sqrt, pow

import serial
import cv2 as cv
import numpy as np


class GRBL:
    def __init__(self, port: str):
        self.port_name = port
        self.controller = serial.Serial(self.port_name, 115200)
        answer = self.controller.readline()
        print(answer)

    def disconnect(self):
        self.controller.close()

    def move_to_xy(self, x: float, y: float):
        command = f'G90 X{x} Y{y}\n'
        command = command.encode('ASCII')
        self.controller.write(command)

    def go_home(self):
        command = f'G01 X0 Y0 F10000\n'
        command = command.encode('ASCII')
        self.controller.write(command)


class Camera:
    def __init__(self, url: str, m_w: float, m_h: float, f: float, d: float):
        self.capture = cv.VideoCapture(url)
        self.focus = f
        self.distance = d
        self.matrix_width = m_w
        self.matrix_height = m_h

    def get_frame(self):
        ret, frame = self.capture.read()
        frame = cv.resize(frame, None, fx=0.5, fy=0.5,
                          interpolation=cv.INTER_CUBIC)
        return frame

    def close_camera(self):
        self.capture.release()
        cv.destroyAllWindows()
