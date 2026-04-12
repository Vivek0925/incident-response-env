# tasks/scenarios.py

easy_task = {
    "id": "traffic_spike",
    "name": "traffic_spike",
    "difficulty": "easy",
    "grader": "tasks.graders:grade_incident",  # ✅ FIXED
    "initial_state": {
        "incident": "traffic_spike",
        "cpu_usage": 95,
        "memory_usage": 80,
        "database_latency": 100,
        "network_errors": 5,
        "error_rate": 8,
        "servers": 3
    }
}

medium_task = {
    "id": "database_overload",
    "name": "database_overload",
    "difficulty": "medium",
    "grader": "tasks.graders:grade_incident",  # ✅ FIXED
    "initial_state": {
        "incident": "database_overload",
        "cpu_usage": 85,
        "memory_usage": 75,
        "database_latency": 200,
        "network_errors": 8,
        "error_rate": 12,
        "servers": 3
    }
}

hard_task = {
    "id": "failed_deployment",
    "name": "failed_deployment",
    "difficulty": "hard",
    "grader": "tasks.graders:grade_incident",  # ✅ FIXED
    "initial_state": {
        "incident": "failed_deployment",
        "cpu_usage": 75,
        "memory_usage": 90,
        "database_latency": 150,
        "network_errors": 10,
        "error_rate": 20,
        "servers": 2
    }
}

TASKS = [easy_task, medium_task, hard_task]

tasks = TASKS  # compatibility

def get_tasks():
    return TASKS

def load_tasks():
    return TASKS

def get_tasks():
    return TASKS

tasks = TASKS