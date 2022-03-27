"""Keyboard related functions.

get_key() is modified from code used in the Turtlebot Teleop package.
"""
import sys
import tty
import select
import termios

from typing import List
from typing import Optional


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


def main():
    """Run keyboard test code."""
    settings = None
    settings = termios.tcgetattr(sys.stdin)

    while 1:
        key = get_key(settings)
        if key in ['q', 'Q']:
            break

        print(key)

if __name__ == '__main__':
    main()
