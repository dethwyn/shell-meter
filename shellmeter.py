from math import tan, atan, sqrt, pow, pi

import serial
import cv2 as cv
import numpy as np


class GRBL:
    def __init__(self, port: str):
        self.port_name = port
        self.controller = serial.Serial(self.port_name, 115200)
        answer = self.controller.readline()

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

    def get_frame(self) -> np.numarray:
        ret, frame = self.capture.read()
        # frame = cv.resize(frame, None, fx=0.5, fy=0.5,
        #                   interpolation=cv.INTER_CUBIC)
        return frame

    def close_camera(self):
        self.capture.release()
        cv.destroyAllWindows()


class Shell:
    def __init__(self, cam: Camera, img: np.numarray, n: str):
        self.name = n
        self.camera = cam
        self.image = img
        cv.imwrite(self.name + '_source.jpg', self.image)
        self.img_contour, self.contour = self.fill_contour()
        cv.imwrite(self.name + '_contour.jpg', self.img_contour)
        self.shell_c = self.find_center()

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

    def fill_contour(self):
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
        print(area, contour_index)
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
        print(aov_x, aov_y)
        aov_x = 71 * pi / 180.0
        aov_y = 58 * pi / 180.0
        print(aov_x, aov_y)
        fov_x = 2 * tan(aov_x / 2) * self.camera.distance
        fov_y = 2 * tan(aov_y / 2) * self.camera.distance
        mm_in_px_x = fov_x / self.width
        mm_in_px_y = fov_y / self.height
        return mm_in_px_x, mm_in_px_y
