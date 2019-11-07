import os
import logging

import cv2 as cv
import numpy as np
import serial
from dotenv import load_dotenv

from shellmeter import GRBL, Camera

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
cv.imwrite('1.jpg', camera.get_frame())
