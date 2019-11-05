import os
import logging

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
martix_height = float(os.getenv('MATRIX_HEIGHT'))

# grbl = GRBL(port_name)
# grbl.move_to_xy(30, 30)
# grbl.disconnect()
camera = Camera(camera_url, matrix_width, martix_height, focus, distance)
logging.info('Camera ready')
shell = Shell(file_name='1.jpg', camera=camera, contour_pos=1)

print(shell.fig_center_px)
