# PlanSys2 Interplanetary Museum

This README describes how to execute the ROS 2 implementation of Task 5.

The instructions below assume that the current working directory is the `problem5/` folder. If not, navigate to it first:

```bash
cd problem5
```

The execution requires two terminals connected to the same Docker container.

## Terminal 1

First, start the Docker environment:

```bash
./start_docker.sh
```

This script creates and starts the Docker container using the provided `Dockerfile`, installs all required dependencies, and mounts the necessary directories inside the container.

Once inside the container, the workspace is located at:

```bash
/root/plansys2_ws
```

Prepare the ROS 2 workspace by running:

```bash
./setup.sh
```

This script:
- parses the `problem.pddl` file located in `plansys2_abyssus_base/pddl`;
- generates the corresponding Plansys2 problem file;
- builds the `plansys2_abyssus_base` package.

After the setup is completed, launch the Plansys2 nodes with:

```bash
./terminal_1.sh
```

Keep this terminal running.

## Terminal 2

Open a second terminal and connect to the running container:

```bash
docker exec -it <docker_id> bash
```

Then start the Plansys2 terminal:

```bash
./terminal_2.sh
```

Load the problem generated from the interplanetary museum PDDL during the setup step:

```bash
source ./plansys2_abyssus_base/launch/problem 1
```

Generate a plan using the POPF planner:

```bash
get plan
```

Finally, execute the generated plan:

```bash
run
```

## Expected Output

During execution:
- Terminal 2 displays the actions being executed.
- Terminal 1 reports the status of the Plansys2 executor.

A successful execution ends with:

```text
[executor]: Plan Succeeded
```