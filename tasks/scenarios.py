# tasks/scenarios.py

def get_tasks():
    return [
        {
            "id": "traffic_spike",
            "name": "traffic_spike",
            "difficulty": "easy",
            "grader": grade_incident,   # ✅ DIRECT FUNCTION (NO STRING)
            "initial_state": {
                "incident": "traffic_spike",
                "cpu_usage": 95,
                "memory_usage": 80,
                "database_latency": 100,
                "network_errors": 5,
                "error_rate": 8,
                "servers": 3
            }
        },
        {
            "id": "database_overload",
            "name": "database_overload",
            "difficulty": "medium",
            "grader": grade_incident,
            "initial_state": {
                "incident": "database_overload",
                "cpu_usage": 85,
                "memory_usage": 75,
                "database_latency": 200,
                "network_errors": 8,
                "error_rate": 12,
                "servers": 3
            }
        },
        {
            "id": "failed_deployment",
            "name": "failed_deployment",
            "difficulty": "hard",
            "grader": grade_incident,
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
    ]


# IMPORTANT: import at bottom to avoid circular issues
from tasks.graders import grade_incident