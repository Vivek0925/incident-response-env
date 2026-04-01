from env.incident_env import IncidentEnv

env = IncidentEnv()

# EASY TASK
print("===== EASY TASK =====")
state = env.reset("easy")
print("Initial:", state)

state, reward, done, _ = env.step("scale_servers")
print("After scale:", state)

state, reward, done, _ = env.step("restart_service")
print("After restart:", state)

# MEDIUM TASK
print("\n===== MEDIUM TASK =====")
state = env.reset("medium")
print("Initial:", state)

state, reward, done, _ = env.step("restart_service")
print("After restart:", state)

# HARD TASK
print("\n===== HARD TASK =====")
state = env.reset("hard")
print("Initial:", state)

state, reward, done, _ = env.step("restart_service")
print("After restart:", state)