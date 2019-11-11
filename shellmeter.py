from math import tan, atan, sqrt, pow, pi
import time
import urllib.request

import serial
import cv2 as cv
import numpy as np
import matplotlib.pylab


class GRBL:
    def __init__(self, port: str):
        self.port_name = port
        self.controller = serial.Serial(self.port_name, 115200)
        self.controller.readline()
        self.x, self.y = 0, 0

    def disconnect(self):
        self.controller.close()

    def move_to_xy(self, x: float, y: float):
        command = f'G90 X{x} Y{y}\n'
        command = command.encode('ASCII')
        self.controller.write(command)
        self.x, self.y = x, y

    def go_home(self):
        command = f'G90 G0 X0 Y0\n'
        command = command.encode('ASCII')
        self.controller.write(command)

    def move_x(self, x: int):
        command = f'G21G91G1X{x}F1000\n'
        command = command.encode('ASCII')
        self.controller.write(command)
        self.x += x
        t = 4
        if x >= 26:
            t = (x - 25.6) / 16.6 + 4
        time.sleep(t)

    def move_y(self, y: int):
        command = f'G21G91G1Y{y}F1000\n'
        command = command.encode('ASCII')
        self.controller.write(command)
        self.y += y
        t = 4
        if y >= 26:
            t = (y - 25.6) / 16.6 + 4
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
        cv.destroyAllWindows()


class Shell:
    def __init__(self, cam: Camera, img: np.numarray, n: str):
        self.name = n
        self.camera = cam
        self.image = img.copy()
        self.img_contour, self.contour = self.find_contour()
        self.shell_c = self.find_center()
        self.shell_c = int(self.shell_c[0]), int(self.shell_c[1])
        self.width, self.height, _ = self.image.shape
        self.img_c = int(self.height / 2), int(self.width / 2)
        img = self.image.copy()
        cv.circle(img, self.shell_c, 10, (255, 0, 0), -1, cv.LINE_AA)
        cv.circle(img, self.img_c, 10, (0, 255, 0), -1, cv.LINE_AA)
        cv.imwrite(self.name + '_centers.jpg', img)
        self.res_x, self.res_y = self.pix2mm()
        c1 = self.img_c[0] * self.res_x, self.img_c[1] * self.res_y
        c2 = self.shell_c[0] * self.res_x, self.shell_c[1] * self.res_y
        self.shell_c_mm = c2[0] - c1[0], (c2[1] - c1[1]) * (-1)

    def find_contour(self):
        img = self.image.copy()
        blur = cv.blur(img.copy(), (4, 4))
        img_gray = cv.cvtColor(blur.copy(), cv.COLOR_RGB2GRAY)
        _, thresh = cv.threshold(img_gray.copy(), 180, 255, cv.THRESH_BINARY)
        contours, _ = cv.findContours(thresh.copy(), cv.RETR_TREE,
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
        aov_x = 2 * atan(self.camera.matrix_width / (2 * self.camera.focus))
        aov_y = 2 * atan(self.camera.matrix_height / (2 * self.camera.focus))
        aov_x = 71 * pi / 180.0
        aov_y = 58 * pi / 180.0
        fov_x = 2 * tan(aov_x / 2) * self.camera.distance
        fov_y = 2 * tan(aov_y / 2) * self.camera.distance
        mm_in_px_x = 0.69
        mm_in_px_y = 0.69
        return mm_in_px_x, mm_in_px_y

    def draw_profiloram(self):
        r = []
        phi = []
        angle = 0
        step = 360 / len(self.contour)
        for c in self.contour:
            x = self.shell_c[0] - c[0][0]
            y = self.shell_c[1] - c[0][1]
            r.append(sqrt(x * x + y * y) * self.res_x)
            phi.append(angle)
            angle += step
        matplotlib.pylab.plot(phi, r)
        matplotlib.pylab.savefig('profilogram.png')
