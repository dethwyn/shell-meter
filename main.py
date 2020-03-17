import os
import logging
import time

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


def main_cycle():
    grbl = GRBL(port_name)
    print('Setup system in center')
    grbl.move_to_xy(int(grbl.max_x / 2), int(grbl.max_y / 2))
    print('Start to find center')
    i = 0
    full_time = 0
    while True:
        print(f'Step #{i}')
        t1 = time.time()
        camera = Camera(camera_url, matrix_width, matrix_height, focus,
                        distance)
        img = camera.get_frame()
        shell = Shell(camera, img, str(i))
        x = int(shell.shell_c_mm[0])
        y = int(shell.shell_c_mm[1])
        print(f'Center in x = {x}; y = {y}')
        if -2 <= x <= 2 and -2 <= y <= 2:
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
    grbl.go_home()
    grbl.disconnect()
    print(f'left = {shell.dx_min}')
    print(f'right = {shell.dx_max}')
    print(f'up = {shell.dy_min}')
    print(f'down = {shell.dy_max}')


if __name__ == "__main__":
    # test()
    main_cycle()
