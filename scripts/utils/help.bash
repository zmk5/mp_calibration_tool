#! /usr/bin/env bash

function help_mpct() {
    echo -e "
    ${B}Minipupper Calibration Tool Development Script
    ----------------------------------------------${rs}

    This script allows users to set up a dev environment for the minipupper
    calibration tool.

    ${B}Options
    -------${rs}

    ${B}${g}-h${rs}, ${B}${g}--help${rs}
        Help and other documenation.
    ${B}${g}-r${rs}, ${B}${g}--rebuild${rs}
        Rebuild the docker image provided by the codebase.

    ${B}Usage
    -----${rs}
    "
}
