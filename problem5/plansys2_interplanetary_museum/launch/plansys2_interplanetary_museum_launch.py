import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, OpaqueFunction, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node


def load_env(path): # allows to load the .env file without the need to install external dipendencies
    cfg = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            cfg[k.strip()] = v.strip().strip('"')
    return cfg

# Launch setup
def launch_setup(context, *args, **kwargs):

    config_file = LaunchConfiguration('config_file').perform(context)
    if not config_file:
        raise RuntimeError("config_file not provided")

    cfg = load_env(config_file)

    pkg_name = cfg['PROJECT_NAME']

    share_dir = get_package_share_directory(pkg_name)
    domain_file = os.path.join(share_dir, "pddl", "domain.pddl")

    namespace = LaunchConfiguration('namespace')

    nodes = []

    # PlanSys2 bringup node
    plansys2_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('plansys2_bringup'),
                'launch',
                'plansys2_bringup_launch_monolithic.py'
            )
        ),
        launch_arguments={
            'model_file': domain_file,
            'namespace': namespace
        }.items()
    )

    actions = [
        "wait",
        "pickup_standard_artifact",
        "drop_standard_artifact",
        "pickup_thermosensitive_artifact",
        "pickup_sensitive_artifact",
        "safe_drop_seismic_sensitive_artifact",
        "safe_drop_thermosensitive_artifact",
        "safe_drop_seismic_and_thermo_sensitive_artifact",
        "fly",
        "move",
        "seal",
        "unseal",
        "take_pod",
        "drop_pod",
        "charge_battery",
        "start_earthquake",
        "stop_earthquake",
    ]

    for action in actions:
        nodes.append(
            Node(
                package=pkg_name,
                executable=f"{action}_action_node",
                name=f"{action}_action_node",
                namespace=namespace,
                output='screen',
            )
        )

    return [plansys2_cmd] + nodes


def generate_launch_description():

    return LaunchDescription([

        # Path to config file from bash
        DeclareLaunchArgument(
            'config_file',
            description='Path to config.env file'
        ),

        # Optional namespace
        DeclareLaunchArgument(
            'namespace',
            default_value='',
            description='Namespace'
        ),

        # Make logs easier to read
        SetEnvironmentVariable(
            'RCUTILS_LOGGING_USE_STDOUT',
            '1'
        ),
        SetEnvironmentVariable(
            'RCUTILS_LOGGING_BUFFERED_STREAM',
            '1'
        ),

        # Launch everything
        OpaqueFunction(function=launch_setup)
    ])
