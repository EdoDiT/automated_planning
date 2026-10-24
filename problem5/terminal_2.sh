# setup bash
source /opt/ros/humble/setup.bash
source install/setup.bash

# wait for PlanSys2 executor action server
echo "Waiting for PlanSys2 executor..."
until ros2 action list 2>/dev/null | grep -q "^/execute_plan$"; do
  sleep 1
done

# run plansys2 terminal
ros2 run plansys2_terminal plansys2_terminal
