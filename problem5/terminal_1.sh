CONFIG_FILE_PATH=plansys2_abyssus_base/config.env

source ${CONFIG_FILE_PATH}

#setup bash
source /opt/ros/humble/setup.bash

# run PlanSys2 framework
echo -e "\n ## Launching plansys2 ## \n"
source install/setup.bash
ros2 launch ${PROJECT_NAME} ${PROJECT_NAME}_launch.py config_file:=$CONFIG_FILE_PATH