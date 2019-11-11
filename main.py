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
mjpeg_url = os.getenv('MJPEG_URL')
focus = float(os.getenv('FOCUS'))
distance = float(os.getenv('DISTANCE'))
matrix_width = float(os.getenv('MATRIX_WIDTH'))
matrix_height = float(os.getenv('MATRIX_HEIGHT'))


def main():


    grbl = GRBL(port_name)
    i = 0
    full_time = 0
    while (True):
        print(f'Step #{i}')
        t1 = time.time()
        camera = Camera(camera_url, matrix_width, matrix_height, focus,
                        distance)
        img = camera.get_frame()
        shell = Shell(camera, img.copy(), str(i))
        x = int(shell.shell_c_mm[0])
        y = int(shell.shell_c_mm[1])
        print(f'Center in x = {x}; y = {y}')
        if -1 <= x <= 1 and -1 <= y <= 1:
            print('Center found!')
            print('Drawing profilogram...')
            shell.draw_profiloram()
            break
        grbl.move_x(x)
        grbl.move_y(y)
        t2 = time.time()
        full_time += t2 - t1
        print(f'Step #{i} successfully completed in {t2 - t1} seconds')
        i += 1
    print(f'Well done! Full time = {full_time} seconds')
    print('Go home')
    grbl.go_home()
    time.sleep(30)
    grbl.disconnect()


if __name__ == "__main__":
    main()
