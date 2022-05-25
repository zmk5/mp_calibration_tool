from typing import Tuple
import numpy as np

def read_calibration_file(
        servo_calibration_file_path: str
    ) -> Tuple[bool, np.ndarray]:
    """Read all lines text from EEPROM."""
    try:
        with open(servo_calibration_file_path, 'rb') as nv_f:
            arr1 = np.array(eval(nv_f.readline()))
            arr2 = np.array(eval(nv_f.readline()))
            matrix = np.append(arr1, arr2)
            arr3 = np.array(eval(nv_f.readline()))
            matrix = np.append(matrix, arr3)
            matrix.resize(3,4)
            print(f'Get nv calibration params: \n {matrix}')
    except:
        matrix = np.array(
            [[0, 0, 0, 0],
                [45, 45, 45, 45],
                [-45, -45, -45, -45]]
        )

    # TODO: incorporate this action into a generic function.
    # for i in range(3):
    #     for j in range(4):
    #         self.NocalibrationServoAngle[i][j] = self.Matrix_EEPROM[i,j]
    #         self.CalibrationServoAngle[i][j] = self.Matrix_EEPROM[i,j]

    return True, matrix