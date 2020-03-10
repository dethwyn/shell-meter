import cv2 as cv
import os
import numpy as np
import time
from matplotlib import pyplot as plt


def get_frame():
    url_rtsp = 'rtsp://admin:admin@192.168.1.168:554/0'
    cam = cv.VideoCapture(url_rtsp)
    for i in range(0, 10):
        _, img = cam.read()
        cv.imwrite(f'test/test{i}.png', img)
        time.sleep(0.5)


def test():
    img = cv.imread('test/test0.png')
    source = img.copy()
    source = cv.cvtColor(source, cv.COLOR_RGB2GRAY)
    ret, thresh_bin = cv.threshold(source, 180, 255, cv.THRESH_BINARY)
    cv.imwrite('test/threshee.png', thresh_bin)
    contours, _ = cv.findContours(thresh_bin, cv.RETR_TREE,
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
    cv.imwrite('test/res1.png', img)


def test2():
    img1 = cv.imread('test0.png')
    img2 = cv.imread('test1.png')
    result = cv.addWeighted(img1, 0.7, img2, 0.5, 0)
    cv.imwrite('res.png', result)


get_frame()
