"""Mini-Pupper non-GUI Calibration Tool"""
from dataclasses import dataclass
import re
import select
import sys
import termios
import tty
import os

from typing import List
from typing import Optional
from typing import Union

import numpy as np

from rich import box
from rich import print as r_print
from rich.align import Align
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table

os.chdir('/home/ubuntu/Robotics/QuadrupedRobot/StanfordQuadruped/')
from pupper.HardwareInterface import HardwareInterface

OverLoadCurrentMax = 1500000
OverLoadHoldCounterMax = 100  # almost 3s
ServoCalibrationFilePath = '/sys/bus/i2c/devices/3-0050/eeprom'

servo1_en = 25
servo2_en = 21
hw_version = ''


def get_key(settings: Optional[List] = None) -> str:
    """Return the latest pressed key on a keyboard."""
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


def create_title_panel() -> Panel:
    """Create an options rich.Panel that relays user options."""
    title = '[b red]Mini Pupper CLI Calibration Tool[/b red]'
    return Panel(
        Align.center(
            title,
            vertical='middle'
        ),
        box=box.ROUNDED
    )


def create_options_panel() -> Panel:
    """Create an options rich.Panel that relays user options."""
    options = Table.grid(padding=1)
    options.add_column()
    options.add_column()
    options.add_column()
    options.add_column()

    options.add_row('q/Q: Quit', 'a/A: Apply', '1-4: Select Leg', '', 'h/H: Select Hip')
    options.add_row('', 'i/I: Increase', '', '', 't/T: Select Thigh')
    options.add_row('', 'd/D: Decrease', '', '', 'c/C: Select Calf')

    return Panel(
        Align.center(options, vertical='middle'),
        box=box.ROUNDED,
        title='Keyboard Options'
    )


@dataclass
class LegCalibrationData():

    matrix_eeprom: np.ndarray = np.array([
            [0, 0, 0, 0],
            [45, 45, 45, 45],
            [-45, -45, -45, -45]
        ]
    )
    # servo_standard_langle: List[List[Union[float, int]]] = [
    servo_standard_langle: np.ndarray = np.array([
        [0, 0, 0, 0],
        [45, 45, 45, 45],
        [-45, -45, -45, -45]
    ])
    # servo_neutral_langle: List[List[Union[float, int]]] = [
    servo_neutral_langle: np.ndarray = np.array([
        [0, 0, 0, 0],
        [45, 45, 45, 45],
        [-45, -45, -45, -45]
    ])
    # no_calibration_servo_angle: List[List[Union[float, int]]] = [
    no_calibration_servo_angle: np.ndarray = np.array([
        [0, 0, 0, 0],
        [45, 45, 45, 45],
        [-45, -45, -45, -45]
    ])
    # calibration_servo_angle: List[List[Union[float, int]]] = [
    calibration_servo_angle: np.ndarray = np.array([
        [0, 0, 0, 0],
        [45, 45, 45, 45],
        [-45, -45, -45, -45]
    ])


class Leg():

    def __init__(
            self,
            name: str,
            title: str,
            hip: int,
            thigh: int,
            calf: int,
            color: str
        ) -> None:
        self._hip = hip
        self._thigh = thigh
        self._calf = calf

        self._name = name
        self._title = title
        self._color = color
        self._range = {
            'hip': {'min': -100, 'max': 100,},
            'thigh': {'min': -100, 'max': 100,},
            'calf': {'min': -200, 'max': 0,}
        }

    @property
    def hip(self) -> int:
        return self._hip

    @hip.setter
    def hip(self, value: int) -> None:
        if isinstance(value, int):
            self._hip = self._check_range(value, 'hip')
        else:
            raise TypeError('Hip value must be an int!')

    @property
    def thigh(self) -> int:
        return self._thigh

    @thigh.setter
    def thigh(self, value: int) -> None:
        if isinstance(value, int):
            self._thigh = self._check_range(value, 'thigh')
        else:
            raise TypeError('Thigh value must be an int!')

    @property
    def calf(self) -> int:
        return self._calf

    @calf.setter
    def calf(self, value: int) -> None:
        if isinstance(value, int):
            self._calf = self._check_range(value, 'calf')
        else:
            raise TypeError('Calf value must be an int!')

    def _check_range(self, value: int, section: str) -> int:
        """Check if the range of the set value is within max-min range."""
        if value > self._range[section]['max']:
            return self._range[section]['max']

        if value < self._range[section]['min']:
            return self._range[section]['min']

        return value

    def generate_table(self) -> Table:
        """Generate rich.Table with current hip, calf, and thigh values."""
        table = Table()
        table.add_column(f'{self._name}', justify='right', style='cyan')
        table.add_column('Value', style='magenta')

        table.add_row('Hip', f'-100 <---------- {self._hip} ----------> 100')
        table.add_row('Thigh', f'-100 <---------- {self._thigh} ----------> 100')
        table.add_row('Calf', f'-200 <---------- {self._calf} ----------> 0')

        return table

    def update(self, is_selected: bool = False) -> Panel:
        """Update leg information in the form of a rich.Panel."""
        table = self.generate_table()
        color = f'on {self._color}' if is_selected else self._color

        return Panel(
                Align.center(
                    table, vertical='middle',
                ),
                title=self._title,
                box=box.ROUNDED,
                style=color
            )

    def increase_joint_value(self, joint: str) -> None:
        """Increase a specific joint value by 1."""
        if joint == 'h':
            self.hip += 1
        elif joint == 't':
            self.thigh += 1
        elif joint == 'c':
            self.calf +=1

    def decrease_joint_value(self, joint: str) -> None:
        """Decrease a specific joint value by 1."""
        if joint == 'h':
            self.hip -= 1
        elif joint == 't':
            self.thigh -= 1
        elif joint == 'c':
            self.calf -=1

    def change_joint_values(
            self,
            new_hip: int,
            new_thigh: int,
            new_calf: int
        ) -> None:
        """Change all three joint values."""
        self.hip = new_hip
        self.thigh = new_thigh
        self.calf = new_calf

    def get_all_joint_values(self) -> List[int]:
        """Return all three joint values as a list."""
        return [self.hip, self.thigh, self.calf]


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
        self.left_front = Leg('left-front', '1: Left-Front', 0, 0, -90, 'green')
        self.right_front = Leg('right-front', '2: Right-Front', 0, 0, -90, 'blue')
        self.left_back = Leg('left-back', '3: Left-Back', 0, 0, -90, 'green')
        self.right_back = Leg('right-back', '4: Right-Back', 0, 0, -90, 'blue')

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
        self.left_front.change_joint_values(
            values[0][0], values[0][1], values[0][2])
        self.right_front.change_joint_values(
            values[1][0], values[1][1], values[1][2])
        self.left_back.change_joint_values(
            values[2][0], values[2][1], values[2][2])
        self.right_back.change_joint_values(
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
        value.append(self.left_front.get_all_joint_values())
        value.append(self.right_front.get_all_joint_values())
        value.append(self.left_back.get_all_joint_values())
        value.append(self.right_back.get_all_joint_values())
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


## main.py
def main():
    """Run the mini pupper calibration tool."""
    settings = termios.tcgetattr(sys.stdin)
    pupper = Pupper(ServoCalibrationFilePath)
    leg_options = {
        '1': 'left_front',
        '2': 'right_front',
        '3': 'left_back',
        '4': 'right_back',
    }

    # Create layout containing the minipupper leg and joint selection
    layout = Layout()
    layout.split_column(
        Layout(name='spacer', size=2),
        Layout(name='title_bar')
    )
    layout['title_bar'].split_column(
        Layout(create_title_panel(), name='title', size=5),
        Layout(name='upper')
    )
    layout['upper'].split_column(
        Layout(name='front_legs_viz', size=10),
        Layout(name='lower')
    )
    layout['lower'].split_column(
        Layout(name='back_legs_viz', size=10),
        Layout(create_options_panel(), name='options', size=10),
    )
    layout['front_legs_viz'].split_row(
        Layout(pupper.left_front.update(True), name='left_front'),
        Layout(pupper.right_front.update(), name='right_front'),
    )
    layout['back_legs_viz'].split_row(
        Layout(pupper.left_back.update(), name='left_back'),
        Layout(pupper.right_back.update(), name='right_back'),
    )

    # Print initial layout
    r_print(layout)

    # Select default leg and joint
    leg_selection = 'left_front'
    joint_selection = 'h'

    # Run the calibration tool
    while True:
        keyboard_input = get_key(settings)
        if keyboard_input in ['q', 'Q']:
            pupper.start_daemon()
            break

        if keyboard_input in ['1', '2', '3', '4']:
            for key, leg in leg_options.items():
                if key == keyboard_input:
                    is_leg_selected = True
                    leg_selection = leg
                else:
                    is_leg_selected = False

                layout[leg].update(
                    pupper.__dict__[leg].update(is_leg_selected)
                )

            r_print(layout, end='\r')
        elif keyboard_input in ['h', 'H', 't', 'T', 'c', 'C']:
            joint_selection = keyboard_input.lower()
            r_print(layout, end='\r')

        elif keyboard_input in ['i', 'I', 'd', 'D']:
            if keyboard_input.lower() == 'i':
                pupper.__dict__[leg_selection].increase_joint_value(joint_selection)
            elif keyboard_input.lower() == 'd':
                pupper.__dict__[leg_selection].decrease_joint_value(joint_selection)
            layout[leg_selection].update(
                pupper.__dict__[leg_selection].update(True)
            )
            r_print(layout, end='\r')


if __name__ == '__main__':
    main()
