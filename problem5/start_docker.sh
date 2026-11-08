#!/bin/bash

source plansys2_interplanetary_museum/config.env

FORCE_REBUILD=false
CLEAN=false
CONTAINER_NAME="plansys2-humble-container"

for arg in "$@"; do
    case "$arg" in
        --rebuild)
            FORCE_REBUILD=true
            ;;
        --clean)
            CLEAN=true
            ;;
        *)
            echo "Usage: $0 [--rebuild] [--clean]"
            exit 1
            ;;
    esac
done

if [[ "$CLEAN" == "true" ]]; then
    sudo docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
    sudo docker image rm "$IMAGE_NAME" >/dev/null 2>&1 || true
    echo "Removed container $CONTAINER_NAME and image $IMAGE_NAME."
    exit 0
fi

OLD_IMAGE_ID=""
if sudo docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
    OLD_IMAGE_ID=$(sudo docker image inspect --format '{{.Id}}' "$IMAGE_NAME")
fi

if [[ "$FORCE_REBUILD" == "true" ]] || \
   ! sudo docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then

    echo "Building image $IMAGE_NAME..."
    sudo docker build \
        --no-cache \
        --rm \
        --tag "$IMAGE_NAME" \
        --file Dockerfile \
        .

    NEW_IMAGE_ID=$(sudo docker image inspect --format '{{.Id}}' "$IMAGE_NAME")
    sudo docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
    if [[ -n "$OLD_IMAGE_ID" && "$OLD_IMAGE_ID" != "$NEW_IMAGE_ID" ]]; then
        sudo docker image rm "$OLD_IMAGE_ID" >/dev/null 2>&1 || true
    fi
fi

if sudo docker container inspect "$CONTAINER_NAME" >/dev/null 2>&1; then
    sudo docker start -ai "$CONTAINER_NAME"
else
    sudo docker run \
        -v /tmp/.X11-unix/:/tmp/.X11-unix/ \
        -v "$(pwd)/$PROJECT_NAME:$PLANSYS2_WS/$PROJECT_NAME" \
        -v "$(pwd)/terminal_1.sh:$PLANSYS2_WS/terminal_1.sh" \
        -v "$(pwd)/terminal_2.sh:$PLANSYS2_WS/terminal_2.sh" \
        -v "$(pwd)/setup.sh:$PLANSYS2_WS/setup.sh" \
        --volume="$HOME/.Xauthority:/root/.Xauthority:rw" \
        --network=host \
        --name "$CONTAINER_NAME" \
        --env DISPLAY \
        -w "$PLANSYS2_WS" \
        -it "$IMAGE_NAME" bash
fi