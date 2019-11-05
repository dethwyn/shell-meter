import serial


class Controller(object):
    def __init__(self, port: str):
        self.port_name = port
        self.controller = serial.Serial(self.port_name, 115200)
        answer = self.controller.readline()
        print(answer)

    def disconnect(self):
        self.controller.close()

    def move_to_xy(self, x: float, y: float):
        command = f'G01 X{x} Y{y} F1000\n'
        command = command.encode('ASCII')
        self.controller.write(command)
