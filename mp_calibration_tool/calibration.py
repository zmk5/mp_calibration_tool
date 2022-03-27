from dataclasses import dataclass
from typing import List
from typing import Union

import numpy as np


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
        [0, 0, 0, 0],
        [-90, -90, -90, -90]
    ])
    # servo_neutral_langle: List[List[Union[float, int]]] = [
    servo_neutral_langle: np.ndarray = np.array([
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [-90, -90, -90, -90],
    ])
    # no_calibration_servo_angle: List[List[Union[float, int]]] = [
    no_calibration_servo_angle: np.ndarray = np.array([
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [-90, -90, -90, -90]
    ])
    # calibration_servo_angle: List[List[Union[float, int]]] = [
    calibration_servo_angle: np.ndarray = np.array([
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [-90, -90, -90, -90]
    ])
