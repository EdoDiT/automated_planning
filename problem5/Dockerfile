FROM ros:humble

SHELL ["/bin/bash", "-c"]

# Update to latest version
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ="Europe/London"
RUN apt-get update && apt-get install -y \
    ros-${ROS_DISTRO}-desktop \
    ros-${ROS_DISTRO}-demo-nodes-cpp \
    ros-${ROS_DISTRO}-demo-nodes-py \
    git \
    vim \
    gdb \
    terminator \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root

RUN mkdir -p ~/plansys2_ws/src && \
    cd ~/plansys2_ws/src && \
    git clone https://github.com/PlanSys2/ros2_planning_system.git && \
    cd ros2_planning_system && \
    git checkout ${ROS_DISTRO}-devel && \
    git clone --branch main --depth 1 https://github.com/PlanSys2/kairos.git kairos && \
    git clone --branch ${ROS_DISTRO}-devel --depth 1 \
    https://github.com/fmrico/cascade_lifecycle.git cascade_lifecycle
    
RUN apt-get update && \
    cd ~/plansys2_ws && \
    rosdep install -y -r -q \
    --from-paths src \
    --ignore-src \
    --rosdistro ${ROS_DISTRO} && \
    rm -rf /var/lib/apt/lists/*

RUN cd ~/plansys2_ws && source /opt/ros/${ROS_DISTRO}/setup.bash && colcon build --symlink-install --parallel-workers 1

CMD /bin/bash