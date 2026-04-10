import random
random.seed(42)

try:
    from tasks.graders import grade_traffic_spike, grade_database_overload, grade_failed_deployment
    from tasks.scenarios import TASKS
except ModuleNotFoundError:
    # Support direct execution: python env/incident_env.py
    import os
    import sys

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from tasks.graders import grade_traffic_spike, grade_database_overload, grade_failed_deployment
    from tasks.scenarios import TASKS


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
        self.done = False
        self.state = {}
        self.steps = 0
        self.max_steps = 20
        self.current_task_id = None
        self.current_grader = None

    def reset(self, task=None, difficulty=None):
        """
        Reset the environment with a specific task.
        
        Args:
            task: Can be a task dict from scenarios.py, or a task_id string
            difficulty: Legacy parameter (kept for backward compatibility)
        
        Returns:
            dict: The initial state of the environment
        """
        self.done = False
        self.steps = 0
        
        # Handle different input types that the validator might send
        if task is None and difficulty is not None:
            # Legacy mode: use difficulty string
            if difficulty == "easy":
                task_id = "traffic_spike"
            elif difficulty == "medium":
                task_id = "database_overload"
            elif difficulty == "hard":
                task_id = "failed_deployment"
            else:
                raise ValueError("Invalid difficulty")
            
            # Find the task by id
            for t in TASKS:
                if t["id"] == task_id:
                    task = t
                    break
            else:
                raise ValueError(f"Task {task_id} not found")
        
        elif isinstance(task, str):
            # Task is a string ID
            for t in TASKS:
                if t["id"] == task:
                    task = t
                    break
            else:
                raise ValueError(f"Task {task} not found")
        
        elif isinstance(task, dict):
            # Task is already a dict - use as is
            pass
        
        elif task is None:
            # Default to first task
            task = TASKS[0]
        
        # Load initial state from the task
        self.state = task["initial_state"].copy()
        
        # Store the grader reference and task ID for this task
        self.current_task_id = task["id"]
        
        # Parse grader string (e.g., "tasks.graders:grade_traffic_spike")
        grader_path = task["grader"]
        grader_name = grader_path.split(":")[1]
        
        # Map grader name to actual function
        grader_map = {
            "grade_traffic_spike": grade_traffic_spike,
            "grade_database_overload": grade_database_overload,
            "grade_failed_deployment": grade_failed_deployment,
        }
        self.current_grader = grader_map.get(grader_name, grade_traffic_spike)
        
        return self.state

    def step(self, action, debug=False):
        """
        Execute an action in the environment.
        
        Args:
            action: One of VALID_ACTIONS
            debug: If True, print debug information
        
        Returns:
            tuple: (next_state, reward, done)
        """
        # ---------- INVALID ACTION CHECK ----------
        if action not in self.VALID_ACTIONS:
            return self.state, 0.01, False

        self.steps += 1

        # ---------- ACTIONS ----------

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

        elif action == "ignore_alert":
            pass

        # ---------- SYSTEM DRIFT ----------
        self.state["cpu_usage"] += random.randint(0, 3)
        self.state["memory_usage"] += random.randint(0, 2)
        self.state["database_latency"] += random.randint(0, 20)
        self.state["network_errors"] += random.randint(0, 1)

        # ---------- CASCADING FAILURES ----------
        if self.state["database_latency"] > 300:
            self.state["network_errors"] += 2
            self.state["error_rate"] += 1

        if self.state["cpu_usage"] > 90:
            self.state["error_rate"] += 2

        if self.state["memory_usage"] > 85:
            self.state["cpu_usage"] += 5

        # ---------- INCIDENT PROPAGATION ----------
        if self.state["incident"] == "traffic_spike" and self.state["database_latency"] > 250:
            self.state["incident"] = "database_overload"

        if self.state["incident"] == "database_overload" and self.state["error_rate"] > 15:
            self.state["incident"] = "service_instability"

        if self.state["incident"] == "failed_deployment" and self.state["cpu_usage"] > 90:
            self.state["incident"] = "system_instability"

        # ---------- METRIC LIMITS ----------
        self.state["cpu_usage"] = min(self.state["cpu_usage"], 100)
        self.state["memory_usage"] = min(self.state["memory_usage"], 100)
        self.state["error_rate"] = min(self.state["error_rate"], 100)

        # ---------- INCIDENT RESOLUTION ----------
        if self.state["error_rate"] < 2:
            self.done = True

        if self.steps >= self.max_steps:
            self.done = True

        # ---------- REWARD - Use task-specific grader ----------
        reward = self.current_grader(self.state, debug=debug)

        # Bonus for resolving incident before max steps
        if self.done:
            reward += 0.2

        # Clamp reward strictly between 0 and 1
        reward = max(0.01, min(reward, 0.99))

        return self.state, reward, self.done

    def get_state(self):
        """Return the current state."""
        return self.state


if __name__ == "__main__":
    env = IncidentEnv()
    
    # Test with task parameter (what validator expects)
    print("=== Testing with task parameter ===")
    state = env.reset(task="traffic_spike")
    print(f"Initial state for task 'traffic_spike': {state}")
    print(f"Current grader: {env.current_grader.__name__}")
    
    # Run a few actions
    actions = ["scale_servers", "restart_service", "restart_database"]
    for idx, action in enumerate(actions, start=1):
        state, reward, done = env.step(action, debug=True)
        print(f"step={idx} action={action} reward={reward:.4f} done={done}")
        if done:
            break
    
    print("\n=== Testing database_overload task ===")
    state = env.reset(task="database_overload")
    print(f"Initial database_latency: {state['database_latency']}")
    
    print("\n=== Testing failed_deployment task ===")
    state = env.reset(task="failed_deployment")
    print(f"Initial error_rate: {state['error_rate']}")