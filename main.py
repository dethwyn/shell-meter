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

# grbl = GRBL(port_name)
# grbl.move_to_xy(30, 30)
# grbl.disconnect()
camera = Camera(camera_url, matrix_width, matrix_height, focus, distance)
# cv.imwrite('source.jpg', camera.get_frame())

img = camera.get_frame()
shell1 = Shell(camera, img, '1')
print(shell1.shell_c_mm)
#grbl = GRBL(port_name)
#grbl.move_to_xy(int(shell1.shell_c_mm[0]), int(shell1.shell_c_mm[1]))
#time.sleep(120)
#img = camera.get_frame()
#shell2 = Shell(camera, img, '2')
#print(shell2.shell_c_mm)
#grbl.go_home()
#time.sleep(120)
#grbl.disconnect()
