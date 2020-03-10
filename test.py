import cv2
import os
import numpy as np
import time


def get_frame():
    url_rtsp = 'rtsp://admin:admin@192.168.1.168:554/0'
    cam = cv2.VideoCapture(url_rtsp)
    for i in range(0, 10):
        _, img = cam.read()
        cv2.imwrite(f'test{i}.png', img)
        time.sleep(0.5)


def nothing(x):
    pass


def test():

    img = cv2.imread('test0.png')
    scale_percent = 60  # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    # resize image
    img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray = cv2.GaussianBlur(gray, (9, 9), 0)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)
    _, thresh = cv2.threshold(gray, 90, 150, cv2.THRESH_BINARY_INV)
    # edge = cv2.Canny(thresh, 127, 255)
    circles = cv2.HoughCircles(thresh, cv2.HOUGH_GRADIENT, 1, 400)
    circles = np.uint16(np.around(circles))
    print(circles)
    for i in circles[0, :]:
        # draw the outer circle
        cv2.circle(img, (i[0], i[1]), i[2], (0, 255, 0), 2)
        # draw the center of the circle
        cv2.circle(img, (i[0], i[1]), 2, (0, 0, 255), 3)
    
    cv2.imwrite('thresh.jpg', thresh)
    cv2.imwrite('img.jpg', img)

    """
    cv2.namedWindow('test')
    cv2.createTrackbar('min', 'test', 0, 255, nothing)
    cv2.createTrackbar('max', 'test', 0, 255, nothing)
    img = cv2.imread('test0.png')
    scale_percent = 40  # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    # resize image
    img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray = cv2.GaussianBlur(gray, (9, 9), 0)
    while True:
        min = cv2.getTrackbarPos('min', 'test')
        max = cv2.getTrackbarPos('max', 'test')
        _, thresh = cv2.threshold(gray, min, max, cv2.THRESH_BINARY_INV)
        cv2.imshow('test', thresh)
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break
    cv2.destroyAllWindows()
    """

def test2():
    img1 = cv2.imread('test0.png')
    img2 = cv2.imread('test1.png')
    result = cv2.addWeighted(img1, 1, img2, 0.5, 0)
    cv2.imwrite('res.png', result)
    for i in range(2, 5):
        img1 = cv2.imread('res.png')
        img2 = cv2.imread(f'test{i}.png')
        result = cv2.addWeighted(img1, 1, img2, 0.5, 0)
        cv2.imwrite('res.png', result)


test()
