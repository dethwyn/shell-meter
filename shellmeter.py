from math import tan, atan, sqrt, pow, pi, fabs
import time
import os

import serial
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline


class GRBL:
    def __init__(self, port: str):
        self.max_x = 470
        self.max_y = 370
        self.min_x = 0
        self.min_y = 0

        self.port_name = port
        self.controller = serial.Serial(self.port_name, 115200)
        self.controller.readline()
        self.controller.readline()
        self.controller.readline()
        self.x, self.y = 0, 0
        self.go_home()

    def disconnect(self):
        self.controller.close()

    def move_to_xy(self, x: float, y: float):
        tx, ty = 0, 0
        if fabs(x) >= 26:
            tx = (fabs(x) - 25.6) / 16.6 + 4
        if fabs(y) >= 26:
            ty = (fabs(y) - 25.6) / 16.6 + 4
        print(f'Move x in {x}; y in {y}')
        command = f'G90 X{x} Y{y}\n'
        command = command.encode('ASCII')
        self.controller.write(command)
        self.x, self.y = x, y
        time.sleep(max([tx, ty]))

    def go_home(self):
        print('Finding home...')
        command = f'$H\n'
        command = command.encode('ASCII')
        self.controller.write(command)

        self.controller.readline()
        print('Home found!')

    def go_x0y0(self):
        tx, ty = 0, 0
        if fabs(self.x) >= 26:
            tx = (fabs(self.x) - 25.6) / 16.6 + 4
        if fabs(self.y) >= 26:
            ty = (fabs(self.y) - 25.6) / 16.6 + 4
        print('Move x in 0; y in 0')
        command = f'G90 G0 X0 Y0\n'
        command = command.encode('ASCII')
        self.controller.write(command)
        time.sleep(max([tx, ty]))

    def move_x(self, x: int):
        if self.x + x >= self.max_x:
            x = self.max_x - self.x
            self.x += x
        elif self.x + x <= self.min_x:
            x = self.min_x - self.x
            self.x += x
        else:
            self.x += x
        t = 4
        if fabs(x) >= 26:
            t = (fabs(x) - 25.6) / 16.6 + 4
        print(f'Move x in {x}...')
        command = f'G21G91G1X{x}F1000\n'
        command = command.encode('ASCII')
        self.controller.write(command)
        time.sleep(t)

    def move_y(self, y: int):
        if self.y + y >= self.max_y:
            y = self.max_y - self.y
            self.y += y
        elif self.y + y <= self.min_y:
            y = self.min_y - self.y
            self.y += y
        else:
            self.y += y
        t = 4
        if fabs(y) >= 26:
            t = (fabs(y) - 25.6) / 16.6 + 4
        print(f'Move y in {y}...')
        command = f'G21G91G1Y{y}F1000\n'
        command = command.encode('ASCII')
        self.controller.write(command)
        time.sleep(t)


class Camera:
    def __init__(self, url: str, m_w: float, m_h: float, f: float, d: float):
        self.capture = cv.VideoCapture(url)
        self.focus = f
        self.distance = d
        self.matrix_width = m_w
        self.matrix_height = m_h

    def get_frame(self) -> np.numarray:
        _, frame = self.capture.read()
        return frame

    def close_camera(self):
        self.capture.release()


class Shell:
    def __init__(self, cam: Camera, img: np.numarray, n: str):
        self.name = n
        self.camera = cam
        self.image = img
        self.img_contour, self.contour = self.find_contour()
        self.shell_c = self.find_center()
        self.shell_c = int(self.shell_c[0]), int(self.shell_c[1])
        self.width, self.height, _ = self.image.shape
        self.img_c = int(self.height / 2), int(self.width / 2)
        cv.circle(self.image, self.shell_c, 10, (255, 0, 0), -1, cv.LINE_AA)
        cv.circle(self.image, self.img_c, 10, (0, 255, 0), -1, cv.LINE_AA)
        cv.imwrite(self.name + '_centers.jpg', self.image)
        self.res_x, self.res_y = self.pix2mm()
        c1 = self.img_c[0] * self.res_x, self.img_c[1] * self.res_y
        c2 = self.shell_c[0] * self.res_x, self.shell_c[1] * self.res_y
        self.shell_c_mm = c2[0] - c1[0], (c2[1] - c1[1]) * (-1)

    def find_contour(self):
        img = self.image.copy()
        blur = cv.blur(img, (4, 4))
        img_gray = cv.cvtColor(blur, cv.COLOR_RGB2GRAY)
        _, thresh = cv.threshold(img_gray, 200, 255, cv.THRESH_BINARY)
        contours, _ = cv.findContours(thresh, cv.RETR_TREE,
                                      cv.CHAIN_APPROX_NONE)
        area = 0
        contour_index = 0
        for i in range(0, len(contours)):
            rect = cv.minAreaRect(contours[i])
            next_area = int(rect[1][0] * rect[1][1])
            if next_area > area:
                area = next_area
                contour_index = i
        cv.fillPoly(img, [contours[contour_index]], (0, 255, 255))
        return img, contours[contour_index]

    def find_center(self):
        img = self.img_contour
        ix = 0
        iy = 0
        area = cv.contourArea(self.contour)
        x, y, w, h = cv.boundingRect(self.contour)
        for i in range(y, y + h):
            for j in range(x, x + w):
                r, g, b = img[i, j][2], img[i, j][1], img[i, j][0]
                if r >= 250 and g >= 250 and b == 0:
                    ix += j
                    iy += i
        return int(ix / area), int(iy / area)

    def pix2mm(self):
        m = self.camera.matrix_width
        d = self.camera.distance
        f = self.camera.focus
        fov = (m * d) / f
        res = self.width / fov
        return res, res

    def draw_profiloram(self):
        r = []
        phi = []
        x_list = []
        y_list = []
        angle = 1.0
        i = 0
        step = 360 / len(self.contour)
        for point in self.contour:
            x = (self.shell_c[0] - point[0][0]) * self.res_x
            y = (self.shell_c[1] - point[0][1]) * self.res_y
            x_list.append(x)
            y_list.append(y)
            i += step
            r.append(sqrt(x * x + y * y))
            phi.append(angle)
            angle += step
        plt.plot(phi, r)
        plt.grid()
        plt.xlabel('Angle (Degree)')
        plt.ylabel('Radius (mm)')
        plt.savefig('profilogram_polar.png')
        plt.cla()
        plt.plot(x_list, y_list)
        plt.grid()
        plt.xlabel('X (mm)')
        plt.ylabel('Y (mm)')
        plt.savefig('profilogram_decart.png')
