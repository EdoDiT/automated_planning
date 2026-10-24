#!/bin/bash

source plansys2_abyssus_base/config.env

FORCE_REBUILD=false

if [[ "$1" == "--rebuild" ]]; then
    FORCE_REBUILD=true
fi

if [[ "$FORCE_REBUILD" == "true" ]] || \
   ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then

    echo "Building image $IMAGE_NAME..."
    sudo docker build \
        --no-cache \
        --rm \
        --tag "$IMAGE_NAME" \
        . \
        --file Dockerfile
fi

docker run \
    -v /tmp/.X11-unix/:/tmp/.X11-unix/ \
    -v "$(pwd)/$PROJECT_NAME:$PLANSYS2_WS/$PROJECT_NAME" \
    -v "$(pwd)/terminal_1.sh:$PLANSYS2_WS/terminal_1.sh" \
    -v "$(pwd)/terminal_2.sh:$PLANSYS2_WS/terminal_2.sh" \
    -v "$(pwd)/setup.sh:$PLANSYS2_WS/setup.sh" \
    --volume="$HOME/.Xauthority:/root/.Xauthority:rw" \
    --network=host \
    --name ubuntu_bash \
    --env DISPLAY \
    -w "$PLANSYS2_WS" \
    --rm -it "$IMAGE_NAME" bash