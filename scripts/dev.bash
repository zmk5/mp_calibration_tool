#! /usr/bin/env bash

# _this_dir="$( cd "$(dirname "$0")" ; pwd -P )"
# pushd `pwd` > /dev/null 2>&1
# cd $_this_dir

source "utils/help.bash"
source "utils/log.bash"

rebuild="false"
image_tag="mpct:dev"
image_file="Dockerfile"
container_name="mpct_dev_env"
override_command="/bin/bash"

for arg in "$@";
do
  shift
  case "$arg" in
    "--help")     set -- "$@" "-h" ;;
    "--rebuild")  set -- "$@" "-r" ;;
    *) set -- "$@" "$arg"
  esac
done

OPTIND=1
while getopts hdj:rg arg;
do
    case $arg in

        h)
            help_mpct
            exit 0
            ;;
        r)
            rebuild="true"
            ;;
        *)
            echo -e "$log_error input option '$arg' is not a valid option!"
            quit_with_popd 1
            ;;
    esac
done

echo -e "${B}Host Logs_______________________________________________________________________${rs}"


echo -e "${B}Image Build Logs________________________________________________________________${rs}"

if [[ "$(docker images -q ${image_tag} 2> /dev/null)" == "" ]];
then
    echo -e "$log_warn Docker image ${image_tag} does not exist! Building now..."
    docker build \
        -t ${image_tag} \
        -f "../${image_file}" \
        --build-arg USER_UID=$(id -u) \
        --build-arg USER_GID=$(id -g) \
        .
    echo -e "$log_ok Docker image ${image_tag} built!"
else
    if [[ ${rebuild} == "true" ]];
    then
        echo -e "$log_warn Docker image ${image_tag} is being rebuilt! Rebuilding now..."
        docker build \
            -t ${image_tag} \
            -f "../${image_file}" \
            --build-arg USER_UID=$(id -u) \
            --build-arg USER_GID=$(id -g) \
            .
        echo -e "$log_ok Docker image ${image_tag} rebuilt!"
    else
        echo -e "$log_ok Docker image ${image_tag} is already built and ready."
    fi
fi

echo -e "${B}Container Logs__________________________________________________________________${rs}"
docker run \
    --rm \
    -it \
    --name $container_name \
    --env=TERM="xterm-256color" \
    --tty \
    --user $(id -u):$(id -g) \
    --volume="$(pwd)/..":"/home/pupper/mp_calibration_tool":rw \
    $image_tag $override_command

exit $?
