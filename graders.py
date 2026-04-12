# tasks/graders.py

def _clamp(score: float) -> float:
    return min(max(score, 0.05), 0.95)


def grade_traffic_spike(state):
    cpu = state.get("cpu_usage", 100)
    servers = state.get("servers", 1)
    error = state.get("error_rate", 10)

    score = 0.1

    if cpu < 60:
        score += 0.3
    elif cpu < 80:
        score += 0.2

    if servers >= 5:
        score += 0.3
    elif servers >= 4:
        score += 0.2

    if error < 2:
        score += 0.2
    elif error < 5:
        score += 0.1

    return _clamp(score)


def grade_database_overload(state):
    latency = state.get("database_latency", 200)
    errors = state.get("network_errors", 10)
    err_rate = state.get("error_rate", 10)

    score = 0.1

    if latency < 50:
        score += 0.4
    elif latency < 100:
        score += 0.25

    if errors == 0:
        score += 0.3
    elif errors < 3:
        score += 0.15

    if err_rate < 2:
        score += 0.2
    elif err_rate < 5:
        score += 0.1

    return _clamp(score)


def grade_failed_deployment(state):
    err = state.get("error_rate", 10)
    mem = state.get("memory_usage", 100)
    cpu = state.get("cpu_usage", 100)

    score = 0.1

    if err == 0:
        score += 0.4
    elif err < 3:
        score += 0.25

    if mem < 60:
        score += 0.3
    elif mem < 80:
        score += 0.15

    if cpu < 60:
        score += 0.2
    elif cpu < 80:
        score += 0.1

    return _clamp(score)


def grade_incident(state, **kwargs):
    incident = state.get("incident")

    if incident == "traffic_spike":
        return grade_traffic_spike(state)

    elif incident == "database_overload":
        return grade_database_overload(state)

    elif incident == "failed_deployment":
        return grade_failed_deployment(state)

    return 0.5