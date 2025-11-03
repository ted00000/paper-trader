#!/usr/bin/env python3
"""
Operation Status Tracking
Tracks status, logs, and outputs of all system operations
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

class OperationStatus:
    """Track status of system operations for dashboard monitoring"""

    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.base_dir = Path(__file__).parent
        self.status_dir = self.base_dir / 'dashboard_data' / 'operation_status'
        self.status_dir.mkdir(parents=True, exist_ok=True)

        self.status_file = self.status_dir / f'{operation_name.lower()}_status.json'

        self.status = {
            'operation': operation_name,
            'last_run': None,
            'status': 'NEVER_RUN',
            'duration_seconds': None,
            'error': None,
            'log_file': None,
            'output_files': [],
            'summary': {}
        }

    def start(self, log_file: Optional[str] = None):
        """Mark operation as started"""
        self.status['last_run'] = datetime.now().isoformat()
        self.status['status'] = 'RUNNING'
        self.status['start_time'] = datetime.now().isoformat()
        self.status['error'] = None

        if log_file:
            self.status['log_file'] = log_file

        self._save()

    def complete(self, summary: Optional[Dict[str, Any]] = None, output_files: Optional[list] = None):
        """Mark operation as completed successfully"""
        start_time = datetime.fromisoformat(self.status['start_time'])
        duration = (datetime.now() - start_time).total_seconds()

        self.status['status'] = 'SUCCESS'
        self.status['duration_seconds'] = duration
        self.status['completed_at'] = datetime.now().isoformat()

        if summary:
            self.status['summary'] = summary

        if output_files:
            self.status['output_files'] = output_files

        self._save()

    def fail(self, error_message: str):
        """Mark operation as failed"""
        start_time = datetime.fromisoformat(self.status['start_time'])
        duration = (datetime.now() - start_time).total_seconds()

        self.status['status'] = 'FAILED'
        self.status['duration_seconds'] = duration
        self.status['error'] = error_message
        self.status['failed_at'] = datetime.now().isoformat()

        self._save()

    def _save(self):
        """Save status to file"""
        with open(self.status_file, 'w') as f:
            json.dump(self.status, f, indent=2)

    @staticmethod
    def get_all_statuses() -> Dict[str, Dict]:
        """Get status of all operations"""
        base_dir = Path(__file__).parent
        status_dir = base_dir / 'dashboard_data' / 'operation_status'

        if not status_dir.exists():
            return {}

        statuses = {}
        for status_file in status_dir.glob('*_status.json'):
            with open(status_file) as f:
                status = json.load(f)
                statuses[status['operation']] = status

        return statuses

    @staticmethod
    def get_operations_summary() -> Dict:
        """Get summary of all operations for dashboard"""
        statuses = OperationStatus.get_all_statuses()

        summary = {
            'timestamp': datetime.now().isoformat(),
            'operations': {},
            'health': 'HEALTHY'
        }

        now = datetime.now()

        for op_name, status in statuses.items():
            # Calculate freshness
            if status['last_run']:
                last_run = datetime.fromisoformat(status['last_run'])
                age_hours = (now - last_run).total_seconds() / 3600
            else:
                age_hours = None

            # Determine health status
            if status['status'] == 'FAILED':
                health = 'FAILED'
                summary['health'] = 'UNHEALTHY'
            elif status['status'] == 'NEVER_RUN':
                health = 'NEVER_RUN'
            elif age_hours and age_hours > 48:
                health = 'STALE'
                if summary['health'] == 'HEALTHY':
                    summary['health'] = 'WARNING'
            else:
                health = 'HEALTHY'

            summary['operations'][op_name] = {
                'status': status['status'],
                'health': health,
                'last_run': status['last_run'],
                'age_hours': age_hours,
                'duration': status.get('duration_seconds'),
                'log_file': status.get('log_file'),
                'error': status.get('error'),
                'summary': status.get('summary', {})
            }

        return summary


def track_operation(operation_name: str, log_file: str):
    """Decorator to track operation status"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            tracker = OperationStatus(operation_name)
            tracker.start(log_file=log_file)

            try:
                result = func(*args, **kwargs)
                tracker.complete(summary={'result': 'success'})
                return result
            except Exception as e:
                tracker.fail(str(e))
                raise

        return wrapper
    return decorator


if __name__ == '__main__':
    # Test: Display current status
    summary = OperationStatus.get_operations_summary()
    print(json.dumps(summary, indent=2))
