import os
import logging
import time

import cv2 as cv
import numpy as np
import serial
from dotenv import load_dotenv


from shellmeter import GRBL, Camera, Shell

load_dotenv()
logging.basicConfig(filename='main.log', level=logging.INFO)

port_name = os.getenv('PORT_NAME')
camera_url = os.getenv('CAMERA_URL')
focus = float(os.getenv('FOCUS'))
distance = float(os.getenv('DISTANCE'))
matrix_width = float(os.getenv('MATRIX_WIDTH'))
matrix_height = float(os.getenv('MATRIX_HEIGHT'))


def main():
    grbl = GRBL(port_name)
    i = 0

    while (True):
        camera = Camera(camera_url, matrix_width, matrix_height, focus,
                        distance)
        img = camera.get_frame()
        shell = Shell(camera, img.copy(), str(i))
        x = int(shell.shell_c_mm[0])
        y = int(shell.shell_c_mm[1])
        print(x, y)
        if -2 <= x <= 2 and -2 <= y <= 2:
            shell.draw_profiloram()
            break
        grbl.move_x(x)
        grbl.move_y(y)
        i += 1
    grbl.go_home()
    time.sleep(60)
    grbl.disconnect()


if __name__ == "__main__":
    main()
"""
camera = Camera(camera_url, matrix_width, matrix_height, focus, distance)
img = cv.imread('source.jpg')
shell = Shell(camera, img.copy(), '0')
logging.info(str(shell.shell_c))
"""
