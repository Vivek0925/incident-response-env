import random


class IncidentEnv:

    def __init__(self):
        self.done = False
        self.state = {}

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
        return self.state

    def step(self, action):

        reward = 0

        # ---------------- ACTIONS ----------------

        if action == "scale_servers":
            self.state["servers"] += 1
            self.state["cpu_usage"] = max(0, self.state["cpu_usage"] - 25)
            reward = 0.3

        elif action == "restart_service":
            self.state["error_rate"] = max(0, self.state["error_rate"] - 8)
            reward = 0.5

        elif action == "restart_database":
            self.state["database_latency"] = max(
                0, self.state["database_latency"] - 200)
            reward = 0.6

        elif action == "clear_cache":
            self.state["memory_usage"] = max(
                0, self.state["memory_usage"] - 30)
            reward = 0.4

        elif action == "rollback_deployment":

            if self.state["incident"] == "failed_deployment":
                self.state["error_rate"] = max(
                    0, self.state["error_rate"] - 15)
                reward = 0.8
            else:
                reward = -0.2

        elif action == "ignore_alert":
            reward = -1

        # ---------------- TIME-BASED SYSTEM DRIFT ----------------
        # infrastructure naturally degrades over time

        self.state["cpu_usage"] += random.randint(0, 3)
        self.state["memory_usage"] += random.randint(0, 2)
        self.state["database_latency"] += random.randint(0, 20)
        self.state["network_errors"] += random.randint(0, 1)

        # ---------------- CASCADING FAILURES ----------------

        if self.state["database_latency"] > 300:
            self.state["network_errors"] += 2
            self.state["error_rate"] += 1

        if self.state["cpu_usage"] > 90:
            self.state["error_rate"] += 2

        if self.state["memory_usage"] > 85:
            self.state["cpu_usage"] += 5

        # ---------------- INCIDENT PROPAGATION ----------------

        # traffic spike → database overload
        if self.state["incident"] == "traffic_spike" and self.state["database_latency"] > 250:
            self.state["incident"] = "database_overload"
            reward -= 0.2

        # database overload → service instability
        if self.state["incident"] == "database_overload" and self.state["error_rate"] > 15:
            self.state["incident"] = "service_instability"
            reward -= 0.3

        # failed deployment → system instability
        if self.state["incident"] == "failed_deployment" and self.state["cpu_usage"] > 90:
            self.state["incident"] = "system_instability"
            reward -= 0.4

        # ---------------- METRIC BOUNDS ----------------

        self.state["cpu_usage"] = min(self.state["cpu_usage"], 100)
        self.state["memory_usage"] = min(self.state["memory_usage"], 100)
        self.state["error_rate"] = min(self.state["error_rate"], 100)

        # ---------------- INCIDENT RESOLUTION ----------------

        if self.state["error_rate"] < 2:
            self.done = True
            reward += 1

        return self.state, reward, self.done, {}

    def get_state(self):
        return self.state