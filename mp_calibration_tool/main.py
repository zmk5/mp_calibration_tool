"""Mini-Pupper non-GUI Calibration Tool"""
from dataclasses import dataclass
import re
import _thread
import time
from typing import List
import os

import numpy as np
# from pupper.HardwareInterface import HardwareInterface

ServoCalibrationFilePath = '/sys/bus/nvmem/devices/3-00501/nvmem'

from rich import print as r_print
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout


class LegPositionPanel(Panel):
    """LegPositionPanel Class."""

    def __init__(self, leg_name: str, **kwargs) -> None:
        super().__init__(leg_name, **kwargs)


@dataclass
class PupperLeg():
    """PupperLeg Class"""
    name: str
    _hip: int
    _thigh: int
    _calf: int

    @property
    def hip(self) -> int:
        return self._hip

    @hip.setter
    def hip(self, value: int) -> None:
        if value > 90:
            self._hip = 90

        elif value < -90:
            self._hip = -90

        else:
            self._hip = value

        raise TypeError('Hip value must be an int!')

    @property
    def thigh(self) -> int:
        return self._thigh

    @thigh.setter
    def thigh(self, value: int) -> None:
        if value > 90:
            self._thigh = 90

        elif value < -90:
            self._thigh = -90

        else:
            self._thigh = value

        raise TypeError('Thigh value must be an int!')

    @property
    def calf(self) -> int:
        return self._calf

    @calf.setter
    def calf(self, value: int) -> None:
        if value > 90:
            self._calf = 90

        elif value < -90:
            self._calf = -90

        else:
            self._calf = value

        raise TypeError('Calf value must be an int!')

    def generate_table(self) -> Table:
        """Generate rich.Table with current hip, calf, and thigh values."""
        table = Table()
        table.add_column(f'{self.name}', justify='right', style='cyan')
        table.add_column('Value', style='magenta')

        table.add_row('Hip', f'-90 <---------- {self.hip} ----------> 90')
        table.add_row('Thigh', f'-90 <---------- {self.thigh} ----------> 90')
        table.add_row('Calf', f'-90 <---------- {self.calf} ----------> 90')

        return table


if __name__ == '__main__':
    # panel_group = Group(
    #     LegPositionPanel('Left-Front', style='on blue'),
    #     LegPositionPanel('Left-Back', style='blue'),
    #     LegPositionPanel('Right-Front', style='on green'),
    #     LegPositionPanel('Right-Back', style='green'),
    # )
    # r_print(Panel(panel_group))

    minipupper = {
        'left-front': PupperLeg('Left-Front', 0, 0, 0),
        'right-front': PupperLeg('Right-Front', 0, 0, 0),
        'left-back': PupperLeg('Left-Back', 0, 0, 0),
        'right-back': PupperLeg('Right-Back', 0, 0, 0),
    }

    panel = LegPositionPanel('Left-Front', style='on blue')

    layout = Layout()
    layout.split_column(
        Layout(name='upper'),
        Layout(name='lower')
    )
    layout['upper'].split_row(
        Layout(panel, name='left-front'),
        Layout(LegPositionPanel('Right-Front', style='on green'), name='right-front'),
    )
    layout['lower'].split_row(
        Layout(LegPositionPanel('Left-Back', style='blue'), name='left-back'),
        Layout(LegPositionPanel('Right-Back', style='green'), name='right-back'),
    )

    r_print(layout)

    time.sleep(2)

    layout['left-front'].update(minipupper['left-front'].generate_table())
    r_print(layout)
    time.sleep(5)