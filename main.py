import os

import cv2 as cv
import numpy as np
import serial
from dotenv import load_dotenv

from controller import Controller

load_dotenv()

port_name = os.getenv('PORT_NAME')

controller = Controller(port_name)
controller.move_to_xy(10, 20)
controller.move_to_xy(0, 0)
controller.move_to_xy(10, 20)
controller.disconnect()

