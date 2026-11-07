#!/bin/bash

FORCE_REBUILD=false
CLEAN=false
IMAGE_NAME="myplanutils"
CONTAINER_NAME="myplanutils-container"

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
    docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
    docker image rm "$IMAGE_NAME" >/dev/null 2>&1 || true
    echo "Removed container $CONTAINER_NAME and image $IMAGE_NAME."
    exit 0
fi

OLD_IMAGE_ID=""
if docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
    OLD_IMAGE_ID=$(docker image inspect --format '{{.Id}}' "$IMAGE_NAME")
fi

if [[ "$FORCE_REBUILD" == "true" ]] || \
   ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then

    echo "Building image $IMAGE_NAME..."
    BUILD_ARGS=(
        --rm
        --platform linux/amd64
        --tag "$IMAGE_NAME"
        --file Dockerfile
        .
    )

    if [[ "$FORCE_REBUILD" == "true" ]]; then
        BUILD_ARGS+=(--no-cache)
        BUILD_ARGS+=(--network=host)
    fi

    docker build "${BUILD_ARGS[@]}"

    NEW_IMAGE_ID=$(docker image inspect --format '{{.Id}}' "$IMAGE_NAME")
    if [[ "$FORCE_REBUILD" == "true" ]]; then
        docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
    fi
    if [[ -n "$OLD_IMAGE_ID" && "$OLD_IMAGE_ID" != "$NEW_IMAGE_ID" ]]; then
        docker image rm "$OLD_IMAGE_ID" >/dev/null 2>&1 || true
    fi
fi

if docker container inspect "$CONTAINER_NAME" >/dev/null 2>&1; then
    docker start -ai "$CONTAINER_NAME"
else
    docker run --name "$CONTAINER_NAME" \
        -v "$(pwd)":/project \
        -w /project \
        -it \
        --privileged \
        --platform linux/amd64 \
        "$IMAGE_NAME" \
        bash
fi
