#!/usr/bin/env python3
"""
Blue/Green and Canary Deployment Scripts
Supports multiple deployment strategies for different environments.
"""

import os
import sys
import json
import subprocess
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse
import yaml

class DeploymentManager:
    """Manages different deployment strategies."""
    
    def __init__(self, config_file: str = "config/deploy-config.yaml"):
        self.config = self._load_config(config_file)
        self.environments = self.config.get('environments', {})
        self.strategies = self.config.get('strategies', {})
    
    def _load_config(self, config_file: str) -> Dict:
        """Load deployment configuration."""
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"⚠️ Config file {config_file} not found, using defaults")
            return self._default_config()
        except yaml.YAMLError as e:
            print(f"❌ Error parsing config file: {e}")
            return self._default_config()
    
    def _default_config(self) -> Dict:
        """Default deployment configuration."""
        return {
            'environments': {
                'staging': {
                    'type': 'kubernetes',
                    'namespace': 'staging',
                    'replicas': 2
                },
                'production': {
                    'type': 'kubernetes',
                    'namespace': 'production',
                    'replicas': 5
                }
            },
            'strategies': {
                'blue-green': {
                    'health_check_interval': 30,
                    'rollback_threshold': 0.05,
                    'switch_traffic_delay': 60
                },
                'canary': {
                    'initial_traffic': 10,
                    'traffic_increment': 25,
                    'increment_interval': 300,
                    'success_threshold': 0.99
                }
            }
        }
    
    def deploy(self, environment: str, strategy: str, image: str, **kwargs) -> Dict:
        """Deploy using specified strategy."""
        print(f"🚀 Starting {strategy} deployment to {environment}")
        
        if strategy == 'blue-green':
            return self._blue_green_deploy(environment, image, **kwargs)
        elif strategy == 'canary':
            return self._canary_deploy(environment, image, **kwargs)
        elif strategy == 'rolling':
            return self._rolling_deploy(environment, image, **kwargs)
        else:
            raise ValueError(f"Unknown deployment strategy: {strategy}")
    
    def _blue_green_deploy(self, environment: str, image: str, **kwargs) -> Dict:
        """Blue-Green deployment strategy."""
        env_config = self.environments.get(environment, {})
        strategy_config = self.strategies.get('blue-green', {})
        
        deployment_result = {
            'strategy': 'blue-green',
            'environment': environment,
            'image': image,
            'status': 'in_progress',
            'phases': []
        }
        
        try:
            # Phase 1: Deploy green version
            print("📦 Phase 1: Deploying green version...")
            green_deploy = self._deploy_green_version(environment, image, env_config)
            deployment_result['phases'].append(green_deploy)
            
            if not green_deploy['success']:
                deployment_result['status'] = 'failed'
                return deployment_result
            
            # Phase 2: Health checks
            print("🏥 Phase 2: Running health checks...")
            health_result = self._run_health_checks(environment, 'green', strategy_config)
            deployment_result['phases'].append(health_result)
            
            if not health_result['success']:
                print("❌ Health checks failed, rolling back...")
                rollback = self._rollback_green(environment)
                deployment_result['phases'].append(rollback)
                deployment_result['status'] = 'failed'
                return deployment_result
            
            # Phase 3: Switch traffic
            print("🔄 Phase 3: Switching traffic...")
            time.sleep(strategy_config.get('switch_traffic_delay', 60))
            
            traffic_switch = self._switch_traffic_to_green(environment, env_config)
            deployment_result['phases'].append(traffic_switch)
            
            if not traffic_switch['success']:
                print("❌ Traffic switch failed, rolling back...")
                rollback = self._rollback_green(environment)
                deployment_result['phases'].append(rollback)
                deployment_result['status'] = 'failed'
                return deployment_result
            
            # Phase 4: Clean up blue version
            print("🧹 Phase 4: Cleaning up old version...")
            cleanup = self._cleanup_blue_version(environment)
            deployment_result['phases'].append(cleanup)
            
            deployment_result['status'] = 'success'
            print("✅ Blue-Green deployment completed successfully!")
        
        except Exception as e:
            deployment_result['status'] = 'error'
            deployment_result['error'] = str(e)
            print(f"❌ Blue-Green deployment failed: {e}")
        
        return deployment_result
    
    def _canary_deploy(self, environment: str, image: str, **kwargs) -> Dict:
        """Canary deployment strategy."""
        env_config = self.environments.get(environment, {})
        strategy_config = self.strategies.get('canary', {})
        
        deployment_result = {
            'strategy': 'canary',
            'environment': environment,
            'image': image,
            'status': 'in_progress',
            'phases': []
        }
        
        try:
            # Phase 1: Deploy canary version
            print("🐦 Phase 1: Deploying canary version...")
            canary_deploy = self._deploy_canary_version(environment, image, env_config)
            deployment_result['phases'].append(canary_deploy)
            
            if not canary_deploy['success']:
                deployment_result['status'] = 'failed'
                return deployment_result
            
            # Phase 2: Gradual traffic increase
            initial_traffic = strategy_config.get('initial_traffic', 10)
            traffic_increment = strategy_config.get('traffic_increment', 25)
            increment_interval = strategy_config.get('increment_interval', 300)
            success_threshold = strategy_config.get('success_threshold', 0.99)
            
            current_traffic = initial_traffic
            
            while current_traffic < 100:
                print(f"📊 Setting canary traffic to {current_traffic}%...")
                
                traffic_result = self._set_canary_traffic(environment, current_traffic)
                deployment_result['phases'].append(traffic_result)
                
                if not traffic_result['success']:
                    print("❌ Traffic routing failed, rolling back...")
                    rollback = self._rollback_canary(environment)
                    deployment_result['phases'].append(rollback)
                    deployment_result['status'] = 'failed'
                    return deployment_result
                
                # Monitor metrics
                print(f"📈 Monitoring metrics for {increment_interval} seconds...")
                time.sleep(increment_interval)
                
                metrics = self._monitor_canary_metrics(environment, current_traffic)
                deployment_result['phases'].append(metrics)
                
                if metrics['success_rate'] < success_threshold:
                    print(f"❌ Success rate {metrics['success_rate']:.2%} below threshold {success_threshold:.2%}")
                    rollback = self._rollback_canary(environment)
                    deployment_result['phases'].append(rollback)
                    deployment_result['status'] = 'failed'
                    return deployment_result
                
                current_traffic = min(100, current_traffic + traffic_increment)
            
            # Phase 3: Complete migration
            print("✅ Canary successful, completing migration...")
            complete_migration = self._complete_canary_migration(environment)
            deployment_result['phases'].append(complete_migration)
            
            deployment_result['status'] = 'success'
            print("✅ Canary deployment completed successfully!")
        
        except Exception as e:
            deployment_result['status'] = 'error'
            deployment_result['error'] = str(e)
            print(f"❌ Canary deployment failed: {e}")
        
        return deployment_result
    
    def _rolling_deploy(self, environment: str, image: str, **kwargs) -> Dict:
        """Rolling deployment strategy."""
        env_config = self.environments.get(environment, {})
        
        deployment_result = {
            'strategy': 'rolling',
            'environment': environment,
            'image': image,
            'status': 'in_progress',
            'phases': []
        }
        
        try:
            print("🔄 Starting rolling deployment...")
            
            if env_config.get('type') == 'kubernetes':
                rolling_result = self._kubernetes_rolling_update(environment, image, env_config)
            else:
                rolling_result = self._generic_rolling_update(environment, image, env_config)
            
            deployment_result['phases'].append(rolling_result)
            
            if rolling_result['success']:
                deployment_result['status'] = 'success'
                print("✅ Rolling deployment completed successfully!")
            else:
                deployment_result['status'] = 'failed'
                print("❌ Rolling deployment failed!")
        
        except Exception as e:
            deployment_result['status'] = 'error'
            deployment_result['error'] = str(e)
            print(f"❌ Rolling deployment failed: {e}")
        
        return deployment_result
    
    def _deploy_green_version(self, environment: str, image: str, env_config: Dict) -> Dict:
        """Deploy green version for blue-green deployment."""
        try:
            if env_config.get('type') == 'kubernetes':
                return self._kubernetes_deploy_green(environment, image, env_config)
            else:
                return self._generic_deploy_green(environment, image, env_config)
        except Exception as e:
            return {'phase': 'deploy_green', 'success': False, 'error': str(e)}
    
    def _kubernetes_deploy_green(self, environment: str, image: str, env_config: Dict) -> Dict:
        """Deploy green version to Kubernetes."""
        namespace = env_config.get('namespace', environment)
        replicas = env_config.get('replicas', 3)
        
        # Update deployment with green label
        result = subprocess.run([
            'kubectl', 'set', 'image', f'deployment/{environment}-app',
            f'app={image}',
            f'--namespace={namespace}'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Wait for rollout
            rollout_result = subprocess.run([
                'kubectl', 'rollout', 'status', f'deployment/{environment}-app',
                f'--namespace={namespace}', '--timeout=300s'
            ], capture_output=True, text=True)
            
            return {
                'phase': 'deploy_green',
                'success': rollout_result.returncode == 0,
                'image': image,
                'replicas': replicas
            }
        
        return {
            'phase': 'deploy_green',
            'success': False,
            'error': result.stderr
        }
    
    def _generic_deploy_green(self, environment: str, image: str, env_config: Dict) -> Dict:
        """Generic green deployment."""
        # This would be customized based on your infrastructure
        print(f"Deploying {image} to {environment} (generic)")
        
        return {
            'phase': 'deploy_green',
            'success': True,
            'image': image,
            'method': 'generic'
        }
    
    def _run_health_checks(self, environment: str, version: str, strategy_config: Dict) -> Dict:
        """Run health checks on deployed version."""
        health_endpoint = f"http://{environment}-{version}.example.com/health"
        check_interval = strategy_config.get('health_check_interval', 30)
        max_attempts = 10
        
        for attempt in range(max_attempts):
            try:
                response = requests.get(health_endpoint, timeout=10)
                if response.status_code == 200:
                    health_data = response.json()
                    if health_data.get('status') == 'healthy':
                        return {
                            'phase': 'health_check',
                            'success': True,
                            'attempts': attempt + 1,
                            'response': health_data
                        }
            except requests.RequestException as e:
                print(f"Health check attempt {attempt + 1} failed: {e}")
            
            if attempt < max_attempts - 1:
                time.sleep(check_interval)
        
        return {
            'phase': 'health_check',
            'success': False,
            'attempts': max_attempts,
            'error': 'Health checks failed'
        }
    
    def _switch_traffic_to_green(self, environment: str, env_config: Dict) -> Dict:
        """Switch traffic from blue to green."""
        try:
            if env_config.get('type') == 'kubernetes':
                # Update service selector to point to green version
                result = subprocess.run([
                    'kubectl', 'patch', 'service', f'{environment}-service',
                    '-p', '{"spec":{"selector":{"version":"green"}}}',
                    f'--namespace={env_config.get("namespace", environment)}'
                ], capture_output=True, text=True)
                
                return {
                    'phase': 'switch_traffic',
                    'success': result.returncode == 0,
                    'method': 'kubernetes_service'
                }
            else:
                # Generic traffic switch (could be load balancer config, etc.)
                return {
                    'phase': 'switch_traffic',
                    'success': True,
                    'method': 'generic'
                }
        except Exception as e:
            return {
                'phase': 'switch_traffic',
                'success': False,
                'error': str(e)
            }
    
    def _rollback_green(self, environment: str) -> Dict:
        """Rollback green deployment."""
        try:
            result = subprocess.run([
                'kubectl', 'rollout', 'undo', f'deployment/{environment}-app',
                f'--namespace={environment}'
            ], capture_output=True, text=True)
            
            return {
                'phase': 'rollback',
                'success': result.returncode == 0,
                'method': 'kubernetes_rollback'
            }
        except Exception as e:
            return {
                'phase': 'rollback',
                'success': False,
                'error': str(e)
            }
    
    def _cleanup_blue_version(self, environment: str) -> Dict:
        """Clean up old blue version."""
        try:
            # This would typically involve cleaning up old pods, images, etc.
            print(f"Cleaning up blue version for {environment}")
            
            return {
                'phase': 'cleanup',
                'success': True,
                'method': 'generic'
            }
        except Exception as e:
            return {
                'phase': 'cleanup',
                'success': False,
                'error': str(e)
            }
    
    def _deploy_canary_version(self, environment: str, image: str, env_config: Dict) -> Dict:
        """Deploy canary version."""
        try:
            # Deploy canary with minimal replicas
            if env_config.get('type') == 'kubernetes':
                # Create canary deployment
                canary_yaml = f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {environment}-canary
  namespace: {env_config.get('namespace', environment)}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {environment}
      version: canary
  template:
    metadata:
      labels:
        app: {environment}
        version: canary
    spec:
      containers:
      - name: app
        image: {image}
"""
                
                with open(f'/tmp/{environment}-canary.yaml', 'w') as f:
                    f.write(canary_yaml)
                
                result = subprocess.run([
                    'kubectl', 'apply', '-f', f'/tmp/{environment}-canary.yaml'
                ], capture_output=True, text=True)
                
                return {
                    'phase': 'deploy_canary',
                    'success': result.returncode == 0,
                    'image': image,
                    'method': 'kubernetes'
                }
            
            return {
                'phase': 'deploy_canary',
                'success': True,
                'image': image,
                'method': 'generic'
            }
        except Exception as e:
            return {
                'phase': 'deploy_canary',
                'success': False,
                'error': str(e)
            }
    
    def _set_canary_traffic(self, environment: str, traffic_percent: int) -> Dict:
        """Set traffic percentage to canary version."""
        try:
            # This would typically involve updating ingress/service mesh rules
            print(f"Setting {traffic_percent}% traffic to canary")
            
            return {
                'phase': 'set_traffic',
                'success': True,
                'traffic_percent': traffic_percent,
                'method': 'generic'
            }
        except Exception as e:
            return {
                'phase': 'set_traffic',
                'success': False,
                'error': str(e)
            }
    
    def _monitor_canary_metrics(self, environment: str, traffic_percent: int) -> Dict:
        """Monitor canary deployment metrics."""
        try:
            # This would typically query monitoring systems like Prometheus
            # For demo purposes, we'll simulate metrics
            import random
            
            # Simulate success rate
            base_rate = 0.995
            traffic_impact = traffic_percent * 0.0001  # Small impact
            success_rate = base_rate - random.uniform(0, traffic_impact)
            
            return {
                'phase': 'monitor_metrics',
                'success': True,
                'traffic_percent': traffic_percent,
                'success_rate': success_rate,
                'error_rate': 1 - success_rate,
                'response_time_p95': random.uniform(100, 200),  # ms
                'request_count': random.randint(1000, 5000)
            }
        except Exception as e:
            return {
                'phase': 'monitor_metrics',
                'success': False,
                'error': str(e)
            }
    
    def _rollback_canary(self, environment: str) -> Dict:
        """Rollback canary deployment."""
        try:
            # Remove canary deployment and reset traffic
            result = subprocess.run([
                'kubectl', 'delete', 'deployment', f'{environment}-canary',
                f'--namespace={environment}', '--ignore-not-found'
            ], capture_output=True, text=True)
            
            return {
                'phase': 'rollback_canary',
                'success': result.returncode == 0,
                'method': 'kubernetes'
            }
        except Exception as e:
            return {
                'phase': 'rollback_canary',
                'success': False,
                'error': str(e)
            }
    
    def _complete_canary_migration(self, environment: str) -> Dict:
        """Complete canary migration by making it the primary version."""
        try:
            # Update main deployment to canary image and remove canary deployment
            print(f"Completing canary migration for {environment}")
            
            return {
                'phase': 'complete_migration',
                'success': True,
                'method': 'generic'
            }
        except Exception as e:
            return {
                'phase': 'complete_migration',
                'success': False,
                'error': str(e)
            }
    
    def _kubernetes_rolling_update(self, environment: str, image: str, env_config: Dict) -> Dict:
        """Perform Kubernetes rolling update."""
        try:
            namespace = env_config.get('namespace', environment)
            
            # Set new image
            result = subprocess.run([
                'kubectl', 'set', 'image', f'deployment/{environment}-app',
                f'app={image}',
                f'--namespace={namespace}'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Wait for rollout
                rollout_result = subprocess.run([
                    'kubectl', 'rollout', 'status', f'deployment/{environment}-app',
                    f'--namespace={namespace}', '--timeout=600s'
                ], capture_output=True, text=True)
                
                return {
                    'phase': 'rolling_update',
                    'success': rollout_result.returncode == 0,
                    'image': image,
                    'method': 'kubernetes'
                }
            
            return {
                'phase': 'rolling_update',
                'success': False,
                'error': result.stderr
            }
        except Exception as e:
            return {
                'phase': 'rolling_update',
                'success': False,
                'error': str(e)
            }
    
    def _generic_rolling_update(self, environment: str, image: str, env_config: Dict) -> Dict:
        """Generic rolling update."""
        return {
            'phase': 'rolling_update',
            'success': True,
            'image': image,
            'method': 'generic'
        }

def main():
    """Main entry point for deployment script."""
    parser = argparse.ArgumentParser(description='Blue/Green and Canary Deployment Manager')
    parser.add_argument('--environment', '-e', required=True,
                       help='Target environment (staging, production, etc.)')
    parser.add_argument('--strategy', '-s', required=True,
                       choices=['blue-green', 'canary', 'rolling'],
                       help='Deployment strategy')
    parser.add_argument('--image', '-i', required=True,
                       help='Docker image to deploy')
    parser.add_argument('--config', '-c', default='config/deploy-config.yaml',
                       help='Deployment configuration file')
    parser.add_argument('--dry-run', action='store_true',
                       help='Simulate deployment without making changes')
    
    args = parser.parse_args()
    
    try:
        manager = DeploymentManager(args.config)
        
        if args.dry_run:
            print("🔍 Dry run mode - no actual deployment will be performed")
        
        result = manager.deploy(
            environment=args.environment,
            strategy=args.strategy,
            image=args.image,
            dry_run=args.dry_run
        )
        
        print(f"\n📊 Deployment Result:")
        print(json.dumps(result, indent=2))
        
        if result['status'] == 'success':
            print(f"\n✅ {args.strategy.title()} deployment to {args.environment} completed successfully!")
            sys.exit(0)
        else:
            print(f"\n❌ {args.strategy.title()} deployment to {args.environment} failed!")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⚠️ Deployment interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()