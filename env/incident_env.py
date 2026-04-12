import random
from scenarios import TASKS
from graders import (
    grade_traffic_spike,
    grade_database_overload,
    grade_failed_deployment
)

random.seed(42)


class IncidentEnv:

    VALID_ACTIONS = [
        "scale_servers",
        "restart_service",
        "restart_database",
        "clear_cache",
        "rollback_deployment",
        "ignore_alert"
    ]

    def __init__(self):
        self.state = {}
        self.done = False
        self.steps = 0
        self.max_steps = 20
        self.current_task_id = None
        self.current_grader = None

    def reset(self, task=None, difficulty=None):
        """
        Reset environment.

        Supports:
        - task id string
        - task dict
        - difficulty
        """

        self.done = False
        self.steps = 0

        # difficulty fallback
        if task is None and difficulty is not None:

            if difficulty == "easy":
                task = "traffic_spike"

            elif difficulty == "medium":
                task = "database_overload"

            elif difficulty == "hard":
                task = "failed_deployment"

        # task id string
        if isinstance(task, str):

            for t in TASKS:
                if t["id"] == task:
                    task = t
                    break

            else:
                task = TASKS[0]

        # direct task dict
        if isinstance(task, dict):
            task_data = task

        else:
            task_data = TASKS[0]

        self.state = task_data["initial_state"].copy()

        self.current_task_id = task_data["id"]

        # assign grader
        if self.current_task_id == "traffic_spike":
            self.current_grader = grade_traffic_spike

        elif self.current_task_id == "database_overload":
            self.current_grader = grade_database_overload

        elif self.current_task_id == "failed_deployment":
            self.current_grader = grade_failed_deployment

        else:
            self.current_grader = grade_traffic_spike

        return self.state

    def step(self, action):

        if action not in self.VALID_ACTIONS:
            return self.state, 0.01, False

        self.steps += 1

        if action == "scale_servers":
            self.state["servers"] += 1
            self.state["cpu_usage"] = max(0, self.state["cpu_usage"] - 25)

        elif action == "restart_service":
            self.state["error_rate"] = max(0, self.state["error_rate"] - 8)

        elif action == "restart_database":
            self.state["database_latency"] = max(0, self.state["database_latency"] - 200)

        elif action == "clear_cache":
            self.state["memory_usage"] = max(0, self.state["memory_usage"] - 30)

        elif action == "rollback_deployment":
            if self.state["incident"] == "failed_deployment":
                self.state["error_rate"] = max(0, self.state["error_rate"] - 15)

        # system drift
        self.state["cpu_usage"] += random.randint(0, 3)
        self.state["memory_usage"] += random.randint(0, 2)
        self.state["database_latency"] += random.randint(0, 20)
        self.state["network_errors"] += random.randint(0, 1)

        # cascading failures
        if self.state["database_latency"] > 300:
            self.state["network_errors"] += 2
            self.state["error_rate"] += 1

        if self.state["cpu_usage"] > 90:
            self.state["error_rate"] += 2

        if self.state["memory_usage"] > 85:
            self.state["cpu_usage"] += 5

        # incident propagation
        if self.state["incident"] == "traffic_spike" and self.state["database_latency"] > 250:
            self.state["incident"] = "database_overload"

        # metric bounds
        self.state["cpu_usage"] = min(100, self.state["cpu_usage"])
        self.state["memory_usage"] = min(100, self.state["memory_usage"])
        self.state["error_rate"] = min(100, self.state["error_rate"])

        # termination
        if self.state["error_rate"] < 2:
            self.done = True

        if self.steps >= self.max_steps:
            self.done = True

        reward = self.current_grader(self.state)

        if self.done:
            reward += 0.2

        reward = max(0.01, min(reward, 0.99))

        return self.state, reward, self.done

    def get_state(self):
        return self.state