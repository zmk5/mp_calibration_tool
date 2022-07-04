"""Mini-Pupper non-GUI Calibration Tool"""
import re
import sys
import _thread
import termios
import time
import os

import numpy as np

from rich import print as r_print
from rich.layout import Layout

# from pupper.HardwareInterface import HardwareInterface

from mp_calibration_tool.keyboard import get_key
from mp_calibration_tool.options import create_options_panel
from mp_calibration_tool.quadruped import Pupper
from mp_calibration_tool.title import create_title_panel


OverLoadCurrentMax = 1500000
OverLoadHoldCounterMax = 100  # almost 3s
ServoCalibrationFilePath = '/sys/bus/i2c/devices/3-0050/eeprom'

servo1_en = 25
servo2_en = 21
hw_version = ''


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
