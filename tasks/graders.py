import os


def _clamp(score: float) -> float:
    """Ensure score stays strictly between (0,1)."""
    return max(0.01, min(score, 0.99))


def _log_score(grader_name: str, raw_score: float, final_score: float, **kwargs) -> None:
    """Print scorer details when debug mode is enabled."""
    env_debug = os.getenv("GRADER_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}
    if kwargs.get("debug", False) or env_debug:
        print(
            f"[grader={grader_name}] raw_score={raw_score:.4f}, "
            f"final_score={final_score:.4f}"
        )


def grade_traffic_spike(state, **kwargs):
    """Grade how well a traffic spike was resolved."""
    cpu_usage = state.get("cpu_usage", 100)
    servers = state.get("servers", 1)
    error_rate = state.get("error_rate", 10)

    score = 0.05  # non-zero baseline

    if cpu_usage < 60:
        score += 0.35
    elif cpu_usage < 80:
        score += 0.2
    else:
        score += 0.05

    if servers >= 5:
        score += 0.35
    elif servers >= 4:
        score += 0.2
    else:
        score += 0.05

    if error_rate < 2:
        score += 0.2
    elif error_rate < 5:
        score += 0.1
    else:
        score += 0.05

    final_score = _clamp(score)
    _log_score("traffic_spike", score, final_score, **kwargs)
    return final_score


def grade_database_overload(state, **kwargs):
    """Grade how well a database overload was resolved."""
    database_latency = state.get("database_latency", 200)
    network_errors = state.get("network_errors", 10)
    error_rate = state.get("error_rate", 10)

    score = 0.05  # non-zero baseline

    if database_latency < 50:
        score += 0.4
    elif database_latency < 100:
        score += 0.25
    else:
        score += 0.05

    if network_errors == 0:
        score += 0.3
    elif network_errors < 3:
        score += 0.15
    else:
        score += 0.05

    if error_rate < 2:
        score += 0.2
    elif error_rate < 5:
        score += 0.1
    else:
        score += 0.05

    final_score = _clamp(score)
    _log_score("database_overload", score, final_score, **kwargs)
    return final_score


def grade_failed_deployment(state, **kwargs):
    """Grade how well a failed deployment was resolved."""
    error_rate = state.get("error_rate", 10)
    memory_usage = state.get("memory_usage", 100)
    cpu_usage = state.get("cpu_usage", 100)

    score = 0.05  # non-zero baseline

    if error_rate == 0:
        score += 0.45
    elif error_rate < 3:
        score += 0.3
    else:
        score += 0.05

    if memory_usage < 60:
        score += 0.3
    elif memory_usage < 80:
        score += 0.15
    else:
        score += 0.05

    if cpu_usage < 60:
        score += 0.15
    elif cpu_usage < 80:
        score += 0.08
    else:
        score += 0.05

    final_score = _clamp(score)
    _log_score("failed_deployment", score, final_score, **kwargs)
    return final_score

def grade_incident(state, **kwargs):
    """
    Route grading to the correct incident grader.
    Handles cascading incidents safely.
    """

    incident = state.get("incident", "traffic_spike")

    if incident == "traffic_spike":
        result = grade_traffic_spike(state, **kwargs)
        _log_score("grade_incident:traffic_spike", result, result, **kwargs)
        return result

    if incident == "database_overload":
        result = grade_database_overload(state, **kwargs)
        _log_score("grade_incident:database_overload", result, result, **kwargs)
        return result

    if incident == "failed_deployment":
        result = grade_failed_deployment(state, **kwargs)
        _log_score("grade_incident:failed_deployment", result, result, **kwargs)
        return result

    # cascading incidents fallback
    if incident == "service_instability":
        result = grade_database_overload(state, **kwargs)
        _log_score("grade_incident:service_instability", result, result, **kwargs)
        return result

    if incident == "system_instability":
        result = grade_failed_deployment(state, **kwargs)
        _log_score("grade_incident:system_instability", result, result, **kwargs)
        return result

    # final safety fallback
    result = grade_traffic_spike(state, **kwargs)
    _log_score("grade_incident:fallback_traffic_spike", result, result, **kwargs)
    return result