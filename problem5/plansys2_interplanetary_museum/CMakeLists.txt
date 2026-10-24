cmake_minimum_required(VERSION 3.5)
project(plansys2_abyssus_base)


find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(plansys2_msgs REQUIRED)
find_package(plansys2_executor REQUIRED)

set(CMAKE_CXX_STANDARD 17)

set(dependencies
    rclcpp
    rclcpp_action
    plansys2_msgs
    plansys2_executor
)

set(action_names
  wait
  pickup_standard_artifact
  drop_standard_artifact
  pickup_thermosensitive_artifact
  pickup_sensitive_artifact
  safe_drop_seismic_sensitive_artifact
  safe_drop_thermosensitive_artifact
  safe_drop_seismic_and_thermo_sensitive_artifact
  fly
  move
  seal
  unseal
  take_pod
  drop_pod
  charge_battery
  start_earthquake
  stop_earthquake
)

set(action_targets)
foreach(action_name IN LISTS action_names)
  set(target "${action_name}_action_node")
  add_executable(${target} "src/${target}.cpp")
  ament_target_dependencies(${target} ${dependencies})
  list(APPEND action_targets ${target})
endforeach()

# Load environment variables from config.env
file(STRINGS "${CMAKE_SOURCE_DIR}/config.env" ENV_LINES)

foreach(line ${ENV_LINES})
  if(line MATCHES "^([^=]+)=(.*)$")
    set(${CMAKE_MATCH_1} "${CMAKE_MATCH_2}")
  endif()
endforeach()

install(DIRECTORY launch pddl DESTINATION share/${PROJECT_NAME})

install(TARGETS
  ${action_targets}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()

  find_package(ament_cmake_gtest REQUIRED)
endif()

ament_export_dependencies(${dependencies})

ament_package()