#!/usr/bin/env python3
"""Client for interacting with the Incident Response Environment."""

import json
import requests
import argparse
from typing import Dict, Any, Optional


class IncidentResponseClient:
    """Client for the Incident Response Environment."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health(self) -> Dict[str, Any]:
        """Check if the environment is healthy."""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def reset(self, task: Optional[str] = None, difficulty: Optional[str] = None) -> Dict[str, Any]:
        """Reset the environment with a specific task."""
        payload = {}
        if task:
            payload["task"] = task
        if difficulty:
            payload["difficulty"] = difficulty
        
        response = self.session.post(f"{self.base_url}/reset", json=payload)
        response.raise_for_status()
        return response.json()
    
    def step(self, action: str, debug: bool = False) -> Dict[str, Any]:
        """Take an action in the environment."""
        response = self.session.post(
            f"{self.base_url}/step",
            json={"action": action, "debug": debug}
        )
        response.raise_for_status()
        return response.json()
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state."""
        response = self.session.get(f"{self.base_url}/state")
        response.raise_for_status()
        return response.json()


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Incident Response Environment Client")
    parser.add_argument("--url", default="http://localhost:8000", help="Environment URL")
    parser.add_argument("--task", default="traffic_spike", help="Task to run")
    parser.add_argument("--action", help="Single action to execute")
    
    args = parser.parse_args()
    
    client = IncidentResponseClient(args.url)
    
    # Check health
    print("Checking health...")
    print(client.health())
    
    # Reset environment
    print(f"\nResetting with task: {args.task}")
    result = client.reset(task=args.task)
    print(f"Initial state: {json.dumps(result['state'], indent=2)}")
    
    if args.action:
        print(f"\nTaking action: {args.action}")
        result = client.step(args.action)
        print(f"Result: {json.dumps(result, indent=2)}")


if __name__ == "__main__":
    main()