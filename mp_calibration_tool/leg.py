from typing import List

from rich import box
from rich.align import Align
from rich.panel import Panel
from rich.table import Table



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
            'hip': {
                'min': -100,
                'max': 100,
            },
            'thigh': {
                'min': -100,
                'max': 100,
            },
            'calf': {
                'min': -200,
                'max': 0,
            }
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