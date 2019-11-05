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


class Shell:
    """Shell"""

    def __init__(self, file_name: str, camera: Camera, contour_pos: int):
        self.file_name = file_name
        self.raw_image = cv.imread(self.file_name, cv.IMREAD_COLOR)
        self.width, self.height, _ = self.raw_image.shape
        self.image_center_px = int(self.height / 2), int(self.width / 2)
        image, contour = self.find_contour(self.raw_image, contour_pos)

        self.fig_center_px = self.find_center(image, contour)
        file1 = open('r.txt', 'w')
        file2 = open('phi.txt', 'w')
        for i in contour:
            x = i[0][0]
            y = i[0][1]
            xc = self.fig_center_px[0]
            yc = self.fig_center_px[1]
            r = sqrt(pow(x - xc, 2) + pow(y - yc, 2))
            phi = atan(y / x)
            file1.write(str(r) + '\n')
            file2.write(str(phi) + '\n')
        file1.close()
        file2.close()
        cv.circle(self.raw_image, self.fig_center_px, 15, (255, 0, 0), -1,
                  cv.LINE_AA)
        cv.circle(self.raw_image, self.image_center_px, 15, (0, 255, 0), -1,
                  cv.LINE_AA)
        cv.imwrite('2.jpg', self.raw_image)
        self.resolution_x, self.resolution_y = self.pix2mm(camera)
        self.image_center_mm = self.image_center_px[0] * self.resolution_x, \
                               self.image_center_px[1] * self.resolution_y
        self.fig_center_mm = self.fig_center_px[0] * self.resolution_x, \
                             self.fig_center_px[1] * self.resolution_y

    @staticmethod
    def find_contour(image: np.array, number: int):
        test_image = image.copy()
        image = cv.cvtColor(image, cv.COLOR_RGB2GRAY)
        ret, thresh = cv.threshold(image.copy(), 200, 255, cv.THRESH_BINARY)
        cv.imwrite('thresh.jpg', thresh)
        contours, hierarchy = cv.findContours(thresh.copy(), cv.RETR_TREE,
                                              cv.CHAIN_APPROX_NONE)
        image = cv.cvtColor(image, cv.COLOR_GRAY2BGR)

        test_image1 = test_image.copy()
        cv.drawContours(test_image1, contours, -1, (255, 0, 0), 3,
                        cv.LINE_AA,
                        hierarchy, 1)
        cv.imwrite('test.jpg', test_image1)
        for i in range(0, len(contours)):
            rect = cv.minAreaRect(
                contours[i])  # пытаемся вписать прямоугольник
            area = int(rect[1][0] * rect[1][1])  # вычисление площади
            if area > 500:
                cv.fillPoly(image, [contours[number]], (0, 255, 255))

                cv.imwrite('3.jpg', image)
                return image, contours[number]

    @staticmethod
    def find_center(image: np.array, contour):
        ix = 0
        iy = 0
        area = cv.contourArea(contour)
        x, y, w, h = cv.boundingRect(contour)
        for i in range(y, y + h):
            for j in range(x, x + w):
                r, g, b = image[i, j][2], image[i, j][1], image[i, j][0]
                if r >= 250 and g >= 250 and b == 0:
                    ix += j
                    iy += i
        return int(ix / area), int(iy / area)

    def pix2mm(self, camera: Camera):
        aov_x = 2 * atan(camera.matrix_width / (2 * camera.focus))
        aov_y = 2 * atan(camera.matrix_height / (2 * camera.focus))
        fov_x = 2 * tan(aov_x / 2) * camera.distance
        fov_y = 2 * tan(aov_y / 2) * camera.distance
        mm_in_px_x = fov_x / self.width
        mm_in_px_y = fov_y / self.height
        return mm_in_px_x, mm_in_px_y
