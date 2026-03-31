from tasks.scenarios import easy_scenario
class IncidentEnv:

    def __init__(self):
        self.done = False
        self.state = {}

    def reset(self):
     self.state = easy_scenario.copy()
     self.done = False
     return self.state

    def step(self, action):

        reward = 0

        if action == "scale_servers":
            self.state["servers"] += 1
            self.state["cpu_usage"] -= 30
            reward = 0.5

        elif action == "restart_service":
            self.state["error_rate"] = max(0, self.state["error_rate"] - 10)
            reward = 0.4

        elif action == "ignore_alert":
            reward = -1

        if self.state["error_rate"] < 2:
            self.done = True
            reward += 1

        return self.state, reward, self.done, {}

    def state(self):
        return self.state