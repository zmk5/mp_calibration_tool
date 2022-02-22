#! /usr/bin/env bash

r="\e[31m" # red
g="\e[32m" # green
y="\e[33m" # yellow
b="\e[94m" # blue
c="\e[34m" # cyan
rs="\e[0m" # reset to default 
B="\e[1m"  # bold text

# some echoing options for clarity
log_debug="${B}${y}[DEBUG]${rs}:"
log_info="${B}${b}[INFO]${rs}:"
log_ok="${B}${g}[OK]${rs}: "
log_warn="${B}${y}[WARN]${rs}:"
log_error="${B}${r}[ERROR]${rs}:"

# Return to the original working dir and exit the script with $1 value
#
function quit_with_popd() {
    popd > /dev/null 2>&1
    exit $1
}