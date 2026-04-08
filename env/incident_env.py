import random
from tasks.graders import grade_incident


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

    def reset(self, difficulty="easy"):

        if difficulty == "easy":
            incident = "traffic_spike"

        elif difficulty == "medium":
            incident = "database_overload"

        elif difficulty == "hard":
            incident = "failed_deployment"

        else:
            raise ValueError("Invalid difficulty")

        if incident == "traffic_spike":
            self.state = {
                "incident": incident,
                "cpu_usage": 95,
                "memory_usage": 80,
                "database_latency": 100,
                "network_errors": 5,
                "error_rate": 8,
                "servers": 3
            }

        elif incident == "database_overload":
            self.state = {
                "incident": incident,
                "cpu_usage": 85,
                "memory_usage": 70,
                "database_latency": 400,
                "network_errors": 8,
                "error_rate": 12,
                "servers": 3
            }

        elif incident == "failed_deployment":
            self.state = {
                "incident": incident,
                "cpu_usage": 75,
                "memory_usage": 65,
                "database_latency": 200,
                "network_errors": 15,
                "error_rate": 20,
                "servers": 2
            }

        self.done = False
        self.steps = 0

        return self.state

    def step(self, action):

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
            self.state["database_latency"] = max(
                0, self.state["database_latency"] - 200)

        elif action == "clear_cache":
            self.state["memory_usage"] = max(
                0, self.state["memory_usage"] - 30)

        elif action == "rollback_deployment":
            if self.state["incident"] == "failed_deployment":
                self.state["error_rate"] = max(
                    0, self.state["error_rate"] - 15)

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

        # ---------- REWARD ----------

        reward = grade_incident(self.state)

        if self.done:
            reward += 0.2

        reward = max(0.01, min(reward, 0.99))

        return self.state, reward, self.done

    def get_state(self):
        return self.state