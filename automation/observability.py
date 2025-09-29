#!/usr/bin/env python3
"""
Observability and Metrics Integration
Integrates with Prometheus, DataDog, OpenTelemetry for build and deployment monitoring.
"""

import os
import sys
import json
import time
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Metric:
    """Represents a metric to be sent."""
    name: str
    value: float
    timestamp: float
    tags: Dict[str, str]
    metric_type: str = "gauge"  # gauge, counter, histogram

@dataclass
class BuildEvent:
    """Represents a build event."""
    project_name: str
    language: str
    status: str
    duration: float
    timestamp: float
    metadata: Dict[str, Any]

class PrometheusClient:
    """Client for Prometheus metrics."""
    
    def __init__(self, gateway_url: str = None):
        self.gateway_url = gateway_url or os.getenv('PROMETHEUS_PUSHGATEWAY_URL', 'http://localhost:9091')
        self.job_name = 'universal-builder'
    
    def push_metric(self, metric: Metric) -> bool:
        """Push a metric to Prometheus pushgateway."""
        try:
            # Format metric for Prometheus
            metric_line = f'{metric.name} {metric.value}\n'
            
            # Create URL with job and instance labels
            url = f'{self.gateway_url}/metrics/job/{self.job_name}'
            
            # Add tags as instance labels
            for key, value in metric.tags.items():
                url += f'/{key}/{value}'
            
            response = requests.post(
                url,
                data=metric_line,
                headers={'Content-Type': 'text/plain'},
                timeout=10
            )
            
            return response.status_code == 200
        
        except Exception as e:
            logger.error(f"Failed to push metric to Prometheus: {e}")
            return False
    
    def push_build_metrics(self, build_result: Dict) -> bool:
        """Push build-specific metrics."""
        try:
            timestamp = time.time()
            success = True
            
            # Overall build metrics
            build_status = 1 if build_result.get('status') == 'success' else 0
            
            metric = Metric(
                name='build_status',
                value=build_status,
                timestamp=timestamp,
                tags={
                    'build_id': str(build_result.get('build_id', 'unknown')),
                    'status': build_result.get('status', 'unknown')
                }
            )
            success &= self.push_metric(metric)
            
            # Project-level metrics
            for project in build_result.get('projects', []):
                project_status = 1 if project.get('status') == 'success' else 0
                
                # Project build status
                metric = Metric(
                    name='project_build_status',
                    value=project_status,
                    timestamp=timestamp,
                    tags={
                        'project': project.get('name', 'unknown'),
                        'language': project.get('language', 'unknown'),
                        'status': project.get('status', 'unknown')
                    }
                )
                success &= self.push_metric(metric)
                
                # Project build duration
                if 'duration' in project:
                    metric = Metric(
                        name='project_build_duration_seconds',
                        value=project['duration'],
                        timestamp=timestamp,
                        tags={
                            'project': project.get('name', 'unknown'),
                            'language': project.get('language', 'unknown')
                        }
                    )
                    success &= self.push_metric(metric)
                
                # Operation-level metrics
                for operation, result in project.get('operations', {}).items():
                    if isinstance(result, dict) and 'success' in result:
                        op_status = 1 if result['success'] else 0
                        
                        metric = Metric(
                            name='operation_status',
                            value=op_status,
                            timestamp=timestamp,
                            tags={
                                'project': project.get('name', 'unknown'),
                                'language': project.get('language', 'unknown'),
                                'operation': operation,
                                'status': 'success' if result['success'] else 'failed'
                            }
                        )
                        success &= self.push_metric(metric)
            
            return success
        
        except Exception as e:
            logger.error(f"Failed to push build metrics: {e}")
            return False

class DataDogClient:
    """Client for DataDog metrics."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('DATADOG_API_KEY')
        self.api_url = 'https://api.datadoghq.com/api/v1/series'
        self.enabled = bool(self.api_key)
    
    def send_metric(self, metric: Metric) -> bool:
        """Send a metric to DataDog."""
        if not self.enabled:
            return False
        
        try:
            payload = {
                'series': [{
                    'metric': f'universal_builder.{metric.name}',
                    'points': [[metric.timestamp, metric.value]],
                    'type': metric.metric_type,
                    'tags': [f'{k}:{v}' for k, v in metric.tags.items()]
                }]
            }
            
            headers = {
                'Content-Type': 'application/json',
                'DD-API-KEY': self.api_key
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 202
        
        except Exception as e:
            logger.error(f"Failed to send metric to DataDog: {e}")
            return False
    
    def send_build_event(self, build_event: BuildEvent) -> bool:
        """Send a build event to DataDog."""
        if not self.enabled:
            return False
        
        try:
            event_url = 'https://api.datadoghq.com/api/v1/events'
            
            payload = {
                'title': f'Build {build_event.status}: {build_event.project_name}',
                'text': f'Project {build_event.project_name} ({build_event.language}) build {build_event.status} in {build_event.duration:.2f}s',
                'date_happened': int(build_event.timestamp),
                'priority': 'normal',
                'tags': [
                    f'project:{build_event.project_name}',
                    f'language:{build_event.language}',
                    f'status:{build_event.status}'
                ],
                'alert_type': 'success' if build_event.status == 'success' else 'error'
            }
            
            headers = {
                'Content-Type': 'application/json',
                'DD-API-KEY': self.api_key
            }
            
            response = requests.post(
                event_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 202
        
        except Exception as e:
            logger.error(f"Failed to send event to DataDog: {e}")
            return False

class OpenTelemetryClient:
    """Client for OpenTelemetry traces and metrics."""
    
    def __init__(self, endpoint: str = None):
        self.endpoint = endpoint or os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://localhost:4317')
        self.enabled = bool(self.endpoint)
        
        if self.enabled:
            try:
                from opentelemetry import trace, metrics
                from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
                from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
                from opentelemetry.sdk.trace import TracerProvider
                from opentelemetry.sdk.trace.export import BatchSpanProcessor
                from opentelemetry.sdk.metrics import MeterProvider
                from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
                
                # Set up tracing
                trace.set_tracer_provider(TracerProvider())
                tracer = trace.get_tracer(__name__)
                
                otlp_exporter = OTLPSpanExporter(endpoint=self.endpoint, insecure=True)
                span_processor = BatchSpanProcessor(otlp_exporter)
                trace.get_tracer_provider().add_span_processor(span_processor)
                
                # Set up metrics
                metric_reader = PeriodicExportingMetricReader(
                    OTLPMetricExporter(endpoint=self.endpoint, insecure=True),
                    export_interval_millis=5000,
                )
                metrics.set_meter_provider(MeterProvider(metric_readers=[metric_reader]))
                
                self.tracer = tracer
                self.meter = metrics.get_meter(__name__)
                
                # Create instruments
                self.build_duration_histogram = self.meter.create_histogram(
                    name="build_duration_seconds",
                    description="Build duration in seconds",
                )
                
                self.build_counter = self.meter.create_counter(
                    name="builds_total",
                    description="Total number of builds",
                )
                
            except ImportError:
                logger.warning("OpenTelemetry not available - install opentelemetry-api and opentelemetry-sdk")
                self.enabled = False
    
    def trace_build(self, build_result: Dict):
        """Create traces for build process."""
        if not self.enabled:
            return
        
        try:
            with self.tracer.start_as_current_span("universal_build") as span:
                span.set_attribute("build.id", str(build_result.get('build_id', 'unknown')))
                span.set_attribute("build.status", build_result.get('status', 'unknown'))
                span.set_attribute("build.project_count", len(build_result.get('projects', [])))
                
                # Add project spans
                for project in build_result.get('projects', []):
                    with self.tracer.start_as_current_span(f"build_project_{project.get('name', 'unknown')}") as project_span:
                        project_span.set_attribute("project.name", project.get('name', 'unknown'))
                        project_span.set_attribute("project.language", project.get('language', 'unknown'))
                        project_span.set_attribute("project.status", project.get('status', 'unknown'))
                        
                        if 'duration' in project:
                            project_span.set_attribute("project.duration", project['duration'])
                        
                        # Add operation spans
                        for operation, result in project.get('operations', {}).items():
                            with self.tracer.start_as_current_span(f"operation_{operation}") as op_span:
                                op_span.set_attribute("operation.name", operation)
                                if isinstance(result, dict):
                                    op_span.set_attribute("operation.success", result.get('success', False))
                                    if 'command' in result:
                                        op_span.set_attribute("operation.command", result['command'])
        
        except Exception as e:
            logger.error(f"Failed to create traces: {e}")
    
    def record_metrics(self, build_result: Dict):
        """Record metrics for build process."""
        if not self.enabled:
            return
        
        try:
            # Record build count
            self.build_counter.add(
                1,
                {
                    "status": build_result.get('status', 'unknown'),
                    "project_count": str(len(build_result.get('projects', [])))
                }
            )
            
            # Record project metrics
            for project in build_result.get('projects', []):
                if 'duration' in project:
                    self.build_duration_histogram.record(
                        project['duration'],
                        {
                            "project": project.get('name', 'unknown'),
                            "language": project.get('language', 'unknown'),
                            "status": project.get('status', 'unknown')
                        }
                    )
        
        except Exception as e:
            logger.error(f"Failed to record metrics: {e}")

class ObservabilityManager:
    """Manages all observability integrations."""
    
    def __init__(self):
        self.prometheus = PrometheusClient()
        self.datadog = DataDogClient()
        self.opentelemetry = OpenTelemetryClient()
        
        self.enabled_clients = []
        if self.prometheus.gateway_url:
            self.enabled_clients.append(('Prometheus', self.prometheus))
        if self.datadog.enabled:
            self.enabled_clients.append(('DataDog', self.datadog))
        if self.opentelemetry.enabled:
            self.enabled_clients.append(('OpenTelemetry', self.opentelemetry))
        
        logger.info(f"Observability enabled for: {[name for name, _ in self.enabled_clients]}")
    
    def record_build_results(self, build_result: Dict) -> Dict:
        """Record build results across all enabled observability platforms."""
        results = {}
        
        try:
            # Prometheus metrics
            if self.prometheus.gateway_url:
                success = self.prometheus.push_build_metrics(build_result)
                results['prometheus'] = {'success': success}
                logger.info(f"Prometheus metrics: {'✅' if success else '❌'}")
            
            # DataDog metrics and events
            if self.datadog.enabled:
                # Send project events
                events_sent = 0
                for project in build_result.get('projects', []):
                    build_event = BuildEvent(
                        project_name=project.get('name', 'unknown'),
                        language=project.get('language', 'unknown'),
                        status=project.get('status', 'unknown'),
                        duration=project.get('duration', 0),
                        timestamp=time.time(),
                        metadata=project
                    )
                    
                    if self.datadog.send_build_event(build_event):
                        events_sent += 1
                
                results['datadog'] = {'events_sent': events_sent}
                logger.info(f"DataDog events sent: {events_sent}")
            
            # OpenTelemetry traces and metrics
            if self.opentelemetry.enabled:
                self.opentelemetry.trace_build(build_result)
                self.opentelemetry.record_metrics(build_result)
                results['opentelemetry'] = {'success': True}
                logger.info("OpenTelemetry traces and metrics recorded ✅")
        
        except Exception as e:
            logger.error(f"Error recording build results: {e}")
            results['error'] = str(e)
        
        return results
    
    def record_deployment_metrics(self, deployment_result: Dict) -> Dict:
        """Record deployment-specific metrics."""
        results = {}
        timestamp = time.time()
        
        try:
            # Common deployment metrics
            deployment_status = 1 if deployment_result.get('status') == 'success' else 0
            
            # Prometheus
            if self.prometheus.gateway_url:
                metric = Metric(
                    name='deployment_status',
                    value=deployment_status,
                    timestamp=timestamp,
                    tags={
                        'environment': deployment_result.get('environment', 'unknown'),
                        'strategy': deployment_result.get('strategy', 'unknown'),
                        'status': deployment_result.get('status', 'unknown')
                    }
                )
                success = self.prometheus.push_metric(metric)
                results['prometheus'] = {'success': success}
            
            # DataDog deployment event
            if self.datadog.enabled:
                event_url = 'https://api.datadoghq.com/api/v1/events'
                
                payload = {
                    'title': f'Deployment {deployment_result.get("status", "unknown")}: {deployment_result.get("environment", "unknown")}',
                    'text': f'{deployment_result.get("strategy", "unknown")} deployment to {deployment_result.get("environment", "unknown")} {deployment_result.get("status", "unknown")}',
                    'date_happened': int(timestamp),
                    'priority': 'normal',
                    'tags': [
                        f'environment:{deployment_result.get("environment", "unknown")}',
                        f'strategy:{deployment_result.get("strategy", "unknown")}',
                        f'status:{deployment_result.get("status", "unknown")}'
                    ],
                    'alert_type': 'success' if deployment_result.get('status') == 'success' else 'error'
                }
                
                headers = {
                    'Content-Type': 'application/json',
                    'DD-API-KEY': self.datadog.api_key
                }
                
                response = requests.post(event_url, json=payload, headers=headers, timeout=10)
                results['datadog'] = {'event_sent': response.status_code == 202}
        
        except Exception as e:
            logger.error(f"Error recording deployment metrics: {e}")
            results['error'] = str(e)
        
        return results
    
    def create_dashboard_config(self) -> Dict:
        """Generate configuration for monitoring dashboards."""
        return {
            'grafana_dashboard': {
                'title': 'Universal Build System',
                'panels': [
                    {
                        'title': 'Build Success Rate',
                        'type': 'stat',
                        'targets': [
                            'rate(builds_total{status="success"}[5m]) / rate(builds_total[5m])'
                        ]
                    },
                    {
                        'title': 'Build Duration',
                        'type': 'graph',
                        'targets': [
                            'histogram_quantile(0.95, build_duration_seconds)'
                        ]
                    },
                    {
                        'title': 'Builds by Language',
                        'type': 'pie',
                        'targets': [
                            'sum by (language) (builds_total)'
                        ]
                    },
                    {
                        'title': 'Project Build Status',
                        'type': 'table',
                        'targets': [
                            'project_build_status'
                        ]
                    }
                ]
            },
            'datadog_dashboard': {
                'title': 'Universal Build System',
                'widgets': [
                    {
                        'definition': {
                            'type': 'timeseries',
                            'title': 'Build Success Rate',
                            'requests': [
                                {
                                    'q': 'sum:universal_builder.builds_total{status:success}.as_rate() / sum:universal_builder.builds_total.as_rate()'
                                }
                            ]
                        }
                    }
                ]
            }
        }

def main():
    """CLI interface for observability testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Observability Manager')
    parser.add_argument('--test', action='store_true', help='Send test metrics')
    parser.add_argument('--build-result', help='JSON file with build results to process')
    
    args = parser.parse_args()
    
    manager = ObservabilityManager()
    
    if args.test:
        # Send test metrics
        test_build_result = {
            'build_id': 'test-123',
            'status': 'success',
            'projects': [
                {
                    'name': 'test-project',
                    'language': 'python',
                    'status': 'success',
                    'duration': 45.2,
                    'operations': {
                        'install': {'success': True},
                        'test': {'success': True},
                        'build': {'success': True}
                    }
                }
            ]
        }
        
        results = manager.record_build_results(test_build_result)
        print(f"Test metrics sent: {json.dumps(results, indent=2)}")
    
    elif args.build_result:
        # Process build result file
        with open(args.build_result, 'r') as f:
            build_result = json.load(f)
        
        results = manager.record_build_results(build_result)
        print(f"Build metrics processed: {json.dumps(results, indent=2)}")
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()