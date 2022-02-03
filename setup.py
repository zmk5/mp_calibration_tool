from setuptools import setup

PACKAGE_NAME = 'mp_calibration_tool'

setup(
    name=PACKAGE_NAME,
    version='0.0.1',
    packages=[PACKAGE_NAME],
    data_files=[
        ('dockerfiles')
    ],
    install_requires=['setuptools', 'rich'],
    zip_safe=False,
    maintainer='zmk5',
    maintainer_email='zkakish@gmail.com',
    description='A non-GUI Calibration Tool for the Mini-Pupper.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'mpct = mp_calibration_tool.main:main',
        ],
    },
)
