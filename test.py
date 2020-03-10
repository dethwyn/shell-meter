import cv2 as cv
import os
import numpy as np
import time
from matplotlib import pyplot as plt


def get_frame():
    url_rtsp = 'rtsp://admin:admin@192.168.1.168:554/0'
    cam = cv.VideoCapture(url_rtsp)
    for i in range(2, 3):
        _, img = cam.read()
        cv.imwrite(f'test/test{i}.png', img)
        time.sleep(0.5)


def test():
    img = cv.imread('test/test2.png')
    source = img.copy()
    source = cv.cvtColor(source, cv.COLOR_RGB2GRAY)
    ret, thresh_bin = cv.threshold(source, 72, 255, cv.THRESH_BINARY_INV)
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


def test3():
    img = cv.imread('test/test1.png')
    gray = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
    blur = cv.GaussianBlur(gray, (9, 9), 0)
    _, th = cv.threshold(blur, 90, 255, cv.THRESH_BINARY)
    th1 = cv.adaptiveThreshold(blur, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv.THRESH_BINARY_INV, 11, 2)
    cv.imwrite('test/thresh.png', th)
    cv.imwrite('test/thresh1.png', th1)


def test4():
    img = cv.imread('test/test1.png')
    hsv = cv.cvtColor(img, cv.COLOR_RGB2HSV)
    cv.imwrite('test/hsv.png', hsv)
    blur = cv.GaussianBlur(hsv, (9, 9), 0)
    lower = np.array([110, 55, 70])
    upper = np.array([120, 120, 120])
    mask = cv.inRange(blur, lower, upper)
    rows = mask.shape[0]
    circles = cv.HoughCircles(mask, cv.HOUGH_GRADIENT, 1, rows / 8,
                              param1=100, param2=30)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        id = 0
        for i in circles[0, :]:
            center = (i[0], i[1])
            # circle center
            cv.circle(img, center, 1, (0, 100, 100), 3)
            # circle outline
            radius = i[2]
            cv.circle(img, center, radius, (255, 0, 255), 3)
            y_min = i[1] - i[2] - 50
            y_max = i[1] + i[2] + 50
            x_min = i[0] - i[2] - 50
            x_max = i[0] + i[2] + 50
            crop_img = img[y_min:y_max, x_min:x_max]
            cv.imwrite(f'test/crop{id}.png', crop_img)
            id += 1
    cv.imwrite('test/res_circle.png', img)
    cv.imwrite('test/mask.png', mask)


def test5(color):
    c = np.uint8(color)
    hsv_green = cv.cvtColor(c, cv.COLOR_BGR2HSV)
    print(hsv_green)


test4()
test5([[[73, 56, 60]]])
test5([[[77, 70, 66]]])
test5([[[54, 47, 41]]])
test5([[[74, 67, 63]]])
