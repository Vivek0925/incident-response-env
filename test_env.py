from env.incident_env import IncidentEnv
from grader.grader import evaluate

env = IncidentEnv()

state = env.reset()

print("Initial State:", state)

state, reward, done, _ = env.step("scale_servers")
print("After scaling:", state)

state, reward, done, _ = env.step("restart_service")
print("After restart:", state)

score = evaluate(state)

print("Final Score:", score)