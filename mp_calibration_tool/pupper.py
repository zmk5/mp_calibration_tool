"""Pupper class definition."""
import os
import re
from typing import Union

import numpy as np

from pupper.HardwareInterface import HardwareInterface

from mp_calibration_tool.calibration import LegCalibrationData
from mp_calibration_tool.leg import Leg


class Pupper():
    """MiniPupper Class containing joint values and other attributes."""

    def __init__(
            self,
            calibration_file: str
        ) -> None:
        with open('/home/ubuntu/.hw_version', 'r') as hw_f:
            hw_version = hw_f.readline()

        if hw_version == 'P1\n':
            self._calibration_file = '/home/ubuntu/.nv_file'
            self.servo1_en = 19
            self.servo2_en = 26
        else:
            self._calibration_file = calibration_file
            self.servo1_en = 25
            self.servo2_en = 21

        # Stop the robot daemon
        self.stop_daemon()

        # Instantiate the hardware servo
        self.hardware_interface = HardwareInterface()

        # Set all four legs
        self.leg = {
            'lf': Leg('left-front', '1: Left-Front', 0, 0, -90, 'green'),
            'rf': Leg('right-front', '2: Right-Front', 0, 0, -90, 'blue'),
            'lb': Leg('left-back', '3: Left-Back', 0, 0, -90, 'green'),
            'rb': Leg('right-back', '4: Right-Back', 0, 0, -90, 'blue'),
        }

        # Leg calibration data
        self.calibration = LegCalibrationData()

        # Initialize overload counter
        self.overload_hold_counter = 0

    def read_calibration_file(self) -> bool:
        """Read all lines text from EEPROM."""
        try:
            with open(self._calibration_file, 'rb') as nv_f:
                # TODO Figure out a way to replace `eval`
                arr1 = np.array(eval(nv_f.readline()))
                arr2 = np.array(eval(nv_f.readline()))
                matrix = np.append(arr1, arr2)
                arr3 = np.array(eval(nv_f.readline()))
                matrix = np.append(matrix, arr3)
                matrix.resize(3,4)
                self.calibration.matrix_eeprom = matrix
                print(f'Get nv calibration params: \n {matrix}')
        except:
            matrix = np.array([
                [0, 0, 0, 0],
                [45, 45, 45, 45],
                [-45, -45, -45, -45]
            ])
            self.calibration.matrix_eeprom = matrix

        for i in range(3):
            for j in range(4):
                self.calibration.no_calibration_servo_angle[i][j] = self.calibration.matrix_eeprom[i, j]
                self.calibration.calibration_servo_angle[i][j] = self.calibration.matrix_eeprom[i, j]

        return True

    def update_calibration_matrix(self, angle: Union[float, int]) -> bool:
        """Update calibration matrix using new angle values."""
        for i in range(3):
            for j in range(4):
                self.calibration.matrix_eeprom[i, j] = angle[i][j]

        return True

    def write_calibration_file(self) -> bool:
        """Write matrix to EEPROM."""
        buf_matrix = np.zeros((3, 4))
        for i in range(3):
            for j in range(4):
                buf_matrix[i,j]= self.calibration.matrix_eeprom[i, j]

        # Format array object string for np.array
        p1 = re.compile("([0-9]\.) ( *)")  # pattern to replace the space that follows each number with a comma
        partially_formatted_matrix = p1.sub(r"\1,\2", str(buf_matrix))
        p2 = re.compile("(\]\n)")  # pattern to add a comma at the end of the first two lines
        formatted_matrix_with_required_commas = p2.sub("],\n", partially_formatted_matrix)

        with open(self._calibration_file, 'w') as nv_f:
            _tmp = str(buf_matrix)
            _tmp = _tmp.replace('.' , ',')
            _tmp = _tmp.replace('[' , '')
            _tmp = _tmp.replace(']' , '')
            print(_tmp, file = nv_f)
            nv_f.close()

        return True

    def modify_all_leg_joint_values(self, values) -> None:
        """Modify all four leg's joint values."""
        self.leg['lf'].change_joint_values(
            values[0][0], values[0][1], values[0][2])
        self.leg['rf'].change_joint_values(
            values[1][0], values[1][1], values[1][2])
        self.leg['lb'].change_joint_values(
            values[2][0], values[2][1], values[2][2])
        self.leg['rb'].change_joint_values(
            values[3][0], values[3][1], values[3][2])

    def reset_leg_joint_values(self) -> bool:
        """Reset all the leg joint values."""
        values = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
        for i in range(3):
            for j in range(4):
                values[j][i] = self.calibration.servo_standard_langle[i][j]

        self.modify_all_leg_joint_values(values)

        return True

    def update_leg_joint_values(self) -> bool:
        """Update all the leg joint values."""
        # NOTE: be careful here since the original value and angle are 3x4 not 4x3.
        value = []
        value.append(self.leg['lf'].get_all_joint_values())
        value.append(self.leg['rf'].get_all_joint_values())
        value.append(self.leg['lb'].get_all_joint_values())
        value.append(self.leg['rb'].get_all_joint_values())
        angle = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
        for i in range(3):
            for j in range(4):
                angle[j][i] = self.calibration.servo_standard_langle[i][j] \
                    - value[j][i] \
                    + self.calibration.no_calibration_servo_angle[i][j]

                # limit angles if needed
                if angle[j][i] > 90:
                    angle[j][i] = 90
                elif angle[j][i] < -90:
                    angle[j][i] = -90

        # NOTE: Be careful updating the matrix since there is no message box
        # that serves as a warning like in the original GUI version.
        return True

    def overload_detection(
            self,
            overload_current_max: int = 1500000,
            overload_hold_counter_max: int = 100) -> bool:
        """Detect any system overloads from battery."""
        overload = False

        r = os.popen('cat /sys/class/power_supply/max1720x_battery/current_now')
        feedback = str(r.readlines())
        current_now = int(feedback[3:len(feedback)-4])

        if current_now > overload_current_max:
            self.overload_hold_counter += 1
            if self.overload_hold_counter > overload_hold_counter_max:
                self.overload_hold_counter = overload_hold_counter_max     
                os.popen(f'echo 0 > /sys/class/gpio/gpio{self.servo1_en}/value')
                os.popen(f'echo 0 > /sys/class/gpio/gpio{self.servo2_en}/value')
                overload = True
            else:
                overload = False
        else:
            self.overload_hold_counter -= 10
            if self.overload_hold_counter < 0:
                self.overload_hold_counter = 0
                os.popen(f'echo 1 > /sys/class/gpio/gpio{self.servo1_en}/value')
                os.popen(f'echo 1 > /sys/class/gpio/gpio{self.servo2_en}/value')
                overload = False

        return overload

    def stop_daemon(self) -> None:
        """Stop the robot daemon to allow for calibration."""
        os.system('sudo systemctl stop robot')
        os.system(f'echo 1 > /sys/class/gpio/gpio{self.servo1_en}/value')
        os.system(f'echo 1 > /sys/class/gpio/gpio{self.servo2_en}/value')

    def start_daemon(self) -> None:
        """Start the robot daemon after finishing calibration."""
        os.system('sudo systemctl start robot')
        os.system(f'echo 1 > /sys/class/gpio/gpio{self.servo1_en}/value')
        os.system(f'echo 1 > /sys/class/gpio/gpio{self.servo2_en}/value')
