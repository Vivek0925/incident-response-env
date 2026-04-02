---
title: Incident Response Env
emoji: ⚡
colorFrom: purple
colorTo: blue
sdk: docker
pinned: false
---

# AI DevOps Incident Response Environment

This environment simulates real-world DevOps incidents such as traffic spikes,
memory leaks, database overload, and failed deployments.

## Why This Environment

Modern production systems fail in chains:

```
traffic spike → database overload → service instability → rising error rates
```

This environment lets AI agents practice multi-step infrastructure recovery under realistic conditions — with time pressure, cascading failures, and operational cost tradeoffs. It mirrors the decision-making loop of a real Site Reliability Engineer.

---

## Observation Space

Each step returns a full infrastructure snapshot:

```json
{
  "incident": "traffic_spike",
  "cpu_usage": 95,
  "memory_usage": 80,
  "database_latency": 100,
  "network_errors": 5,
  "error_rate": 8,
  "servers": 3,
  "time_elapsed_s": 12,
  "resolved": false
}
```

| Field | Type | Description |
|---|---|---|
| `incident` | `string` | Active incident type |
| `cpu_usage` | `int` | CPU load percentage (0–100) |
| `memory_usage` | `int` | Memory usage percentage (0–100) |
| `database_latency` | `int` | DB response time in ms |
| `network_errors` | `int` | Network error count per second |
| `error_rate` | `int` | HTTP 5xx errors per second |
| `servers` | `int` | Active server instances |
| `time_elapsed_s` | `int` | Seconds since incident started |
| `resolved` | `bool` | Whether the incident is resolved |

---

## Action Space

6 discrete infrastructure actions:

| Action | Effect | Best For |
|---|---|---|
| `scale_servers` | Increases server count, reduces CPU load | `traffic_spike` |
| `restart_service` | Restarts app process, clears instability | `failed_deployment` |
| `restart_database` | Resets DB connections, reduces latency | `database_overload` |
| `clear_cache` | Flushes cache, lowers memory pressure | `traffic_spike`, `database_overload` |
| `rollback_deployment` | Reverts to last stable release | `failed_deployment` |
| `ignore_alert` | No operation | — |

---

## Reward Function

```
reward = -1 per step (time cost)
       + 10 for effective action
       - 5  for wrong action
       - 20 if system enters critical state
       + 100 on successful resolution
       - 50  on episode timeout
```

The optimal policy identifies the incident type early and applies the correct action chain in minimum steps.

---

## Incident Types

### Easy — Traffic Spike
Sudden HTTP load surge causing CPU saturation. Resolvable with a single `scale_servers` action.

### Medium — Database Overload
Connection pool exhaustion raising latency and error rate. Requires `restart_database` or `clear_cache`.

### Hard — Failed Deployment
A bad release triggers cascading failures across the stack. Requires `rollback_deployment` followed by `restart_service`.

---

## Environment Dynamics

### Cascading Failures
Incidents evolve if left unhandled:

```
database overload → network errors rise → error rate spikes → service instability
```

### Time-Based Degradation
Each step without intervention worsens system health — CPU, memory, and DB latency all drift upward.

### Incident Propagation
Hard difficulty incidents chain across components, requiring agents to resolve multiple failure modes in sequence.

---

## API Interface

### Reset environment

```bash
POST /reset?difficulty=easy   # easy | medium | hard
```

### Take action

```bash
POST /step
Content-Type: application/json

{ "action": "restart_service" }
```

### Get current state

```bash
GET /state
```

Full interactive docs at `/docs` once the server is running.

---

## Quickstart

```bash
# Install dependencies
pip install -r requirements.txt

# Start the environment server
python -m uvicorn server.app:app --reload

# Open API docs
open http://127.0.0.1:8000/docs
```

### Docker

```bash
docker build -t incident-env .
docker run -p 8000:8000 incident-env
```

---

## Example: Baseline Agent

```bash
python baseline_agent.py
```

```python
import requests, random

BASE = "http://localhost:8000"
ACTIONS = ["scale_servers", "restart_service", "restart_database",
           "clear_cache", "rollback_deployment", "ignore_alert"]

obs = requests.post(f"{BASE}/reset", params={"difficulty": "easy"}).json()
total_reward = 0

for step in range(60):
    action = random.choice(ACTIONS)
    result = requests.post(f"{BASE}/step", json={"action": action}).json()
    total_reward += result["reward"]
    print(f"Step {step+1:02d} | {action:<22} | reward: {result['reward']:+.0f} | done: {result['done']}")
    if result["done"]:
        break

print(f"\nTotal reward: {total_reward:.0f}")
```

### Example: LLM Agent

```python
import anthropic, requests

client = anthropic.Anthropic()
BASE = "http://localhost:8000"
ACTIONS = ["scale_servers", "restart_service", "restart_database",
           "clear_cache", "rollback_deployment", "ignore_alert"]

obs = requests.post(f"{BASE}/reset", params={"difficulty": "hard"}).json()

for step in range(60):
    result = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=20,
        messages=[{
            "role": "user",
            "content": f"""You are an SRE agent resolving a production incident.

State: {obs}

Actions: {', '.join(ACTIONS)}

Reply with only the single best action name."""
        }]
    )
    action = result.content[0].text.strip()
    step_result = requests.post(f"{BASE}/step", json={"action": action}).json()
    obs = step_result["observation"]
    print(f"Step {step+1:02d} | {action:<22} | reward: {step_result['reward']:+.0f}")
    if step_result["done"]:
        print(f"Resolved in {step+1} steps.")
        break
```

---

## Project Structure

```
incident-response-env/
├── env/
│   └── incident_env.py       # Core RL environment logic
├── tasks/
│   ├── scenarios.py          # Incident definitions and difficulty tiers
│   └── graders.py            # Reward and evaluation logic
├── server/
│   └── app.py                # FastAPI server
├── baseline_agent.py         # Random baseline agent
├── openenv.yaml              # OpenEnv spec
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## Evaluation Metrics

| Metric | Description |
|---|---|
| Resolution rate | % of episodes successfully resolved |
| Mean steps to resolution | Average steps in resolved episodes |
| Mean episode reward | Average cumulative reward per episode |
| Wrong action rate | % of steps with an ineffective action |

---

## Use Cases

- Training autonomous SRE agents
- Benchmarking LLM tool-use and planning ability
- Reinforcement learning research on sequential decision making
- DevOps automation prototyping

---

## Roadmap

- [ ] Gymnasium (`gym.Env`) wrapper for standard RL library compatibility
- [ ] Multi-incident cascading scenarios
- [ ] Noisy / misleading alerts to test agent robustness
- [ ] Agent leaderboard

---

## License

MIT