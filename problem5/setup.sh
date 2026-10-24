source plansys2_abyssus_base/config.env

#setup bash
source /opt/ros/humble/setup.bash

# make sure problem file is present
echo -e "\n ## Creating problem file ## \n"
python3 $PLANSYS2_WS/$PROJECT_NAME/utils/pddl_parser.py $PLANSYS2_WS/$PROJECT_NAME/pddl $PLANSYS2_WS/$PROJECT_NAME/launch/problem

# compile the repository
echo -e "\n ## Compiling the repo ## \n"
colcon build --symlink-install
rosdep install --from-paths $PLANSYS2_WS/$PROJECT_NAME --ignore-src -r -y
colcon build --symlink-install
