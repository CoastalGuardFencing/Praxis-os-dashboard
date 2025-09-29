#!/usr/bin/env python3
"""
Post-build hooks for artifact processing, cloud deployment, and notifications.
Executed after the main build process completes.
"""

import os
import sys
import json
import subprocess
import boto3
from pathlib import Path
from typing import Dict, List, Optional
import shutil
import hashlib
import time

class PostBuildHooks:
    """Post-build hooks for artifact processing and deployment."""
    
    def __init__(self, project_info: Dict, build_results: Dict):
        self.project_info = project_info
        self.build_results = build_results
        self.language = project_info.get('language', '')
        self.project_path = project_info.get('path', '.')
        self.project_name = project_info.get('name', 'unknown')
    
    def execute(self) -> Dict:
        """Execute post-build hooks."""
        print(f"📦 Running post-build hooks for {self.language}...")
        
        results = {
            'status': 'success',
            'artifacts': [],
            'deployments': [],
            'notifications': [],
            'errors': []
        }
        
        try:
            # Collect artifacts
            artifacts = self._collect_artifacts()
            results['artifacts'] = artifacts
            
            # Generate SBOM
            sbom = self._generate_sbom()
            if sbom:
                results['artifacts'].append(sbom)
            
            # Upload artifacts
            uploads = self._upload_artifacts(artifacts)
            results['deployments'].extend(uploads)
            
            # Deploy to cloud if configured
            deployments = self._deploy_to_cloud()
            results['deployments'].extend(deployments)
            
            # Send notifications
            notifications = self._send_notifications()
            results['notifications'] = notifications
            
        except Exception as e:
            results['status'] = 'error'
            results['errors'].append(str(e))
            print(f"❌ Post-build hooks failed: {e}")
        
        return results
    
    def _collect_artifacts(self) -> List[Dict]:
        """Collect build artifacts based on language."""
        artifacts = []
        project_path = Path(self.project_path)
        
        # Language-specific artifact collection
        if self.language == 'javascript':
            artifacts.extend(self._collect_javascript_artifacts(project_path))
        elif self.language == 'python':
            artifacts.extend(self._collect_python_artifacts(project_path))
        elif self.language == 'go':
            artifacts.extend(self._collect_go_artifacts(project_path))
        elif self.language == 'rust':
            artifacts.extend(self._collect_rust_artifacts(project_path))
        elif self.language == 'java':
            artifacts.extend(self._collect_java_artifacts(project_path))
        elif self.language == 'csharp':
            artifacts.extend(self._collect_csharp_artifacts(project_path))
        else:
            artifacts.extend(self._collect_generic_artifacts(project_path))
        
        # Calculate checksums
        for artifact in artifacts:
            if Path(artifact['path']).exists():
                artifact['checksum'] = self._calculate_checksum(artifact['path'])
                artifact['size'] = Path(artifact['path']).stat().st_size
        
        return artifacts
    
    def _collect_javascript_artifacts(self, project_path: Path) -> List[Dict]:
        """Collect JavaScript/Node.js artifacts."""
        artifacts = []
        
        # Built assets
        for build_dir in ['dist', 'build', 'public']:
            build_path = project_path / build_dir
            if build_path.exists():
                artifacts.append({
                    'type': 'build_output',
                    'path': str(build_path),
                    'name': f"{self.project_name}-{build_dir}",
                    'language': 'javascript'
                })
        
        # Package files
        if (project_path / 'package.json').exists():
            # Look for packed tarball
            tgz_files = list(project_path.glob('*.tgz'))
            for tgz in tgz_files:
                artifacts.append({
                    'type': 'package',
                    'path': str(tgz),
                    'name': tgz.name,
                    'language': 'javascript',
                    'registry': 'npm'
                })
        
        return artifacts
    
    def _collect_python_artifacts(self, project_path: Path) -> List[Dict]:
        """Collect Python artifacts."""
        artifacts = []
        
        # Wheel and source distributions
        dist_dir = project_path / 'dist'
        if dist_dir.exists():
            for wheel in dist_dir.glob('*.whl'):
                artifacts.append({
                    'type': 'wheel',
                    'path': str(wheel),
                    'name': wheel.name,
                    'language': 'python',
                    'registry': 'pypi'
                })
            
            for sdist in dist_dir.glob('*.tar.gz'):
                artifacts.append({
                    'type': 'source_distribution',
                    'path': str(sdist),
                    'name': sdist.name,
                    'language': 'python',
                    'registry': 'pypi'
                })
        
        return artifacts
    
    def _collect_go_artifacts(self, project_path: Path) -> List[Dict]:
        """Collect Go artifacts."""
        artifacts = []
        
        # Binary executables
        bin_dirs = [project_path / 'bin', project_path]
        for bin_dir in bin_dirs:
            if bin_dir.exists():
                for binary in bin_dir.iterdir():
                    if binary.is_file() and os.access(binary, os.X_OK):
                        # Check if it's likely a Go binary
                        if binary.suffix in ['', '.exe'] and not binary.name.startswith('.'):
                            artifacts.append({
                                'type': 'binary',
                                'path': str(binary),
                                'name': binary.name,
                                'language': 'go'
                            })
        
        return artifacts
    
    def _collect_rust_artifacts(self, project_path: Path) -> List[Dict]:
        """Collect Rust artifacts."""
        artifacts = []
        
        # Target directory
        target_dir = project_path / 'target' / 'release'
        if target_dir.exists():
            for binary in target_dir.iterdir():
                if binary.is_file() and os.access(binary, os.X_OK):
                    # Skip debug files and other non-binaries
                    if not binary.name.endswith('.d') and not binary.suffix in ['.so', '.dylib', '.dll']:
                        artifacts.append({
                            'type': 'binary',
                            'path': str(binary),
                            'name': binary.name,
                            'language': 'rust'
                        })
        
        # Crate packages
        for crate in project_path.glob('*.crate'):
            artifacts.append({
                'type': 'crate',
                'path': str(crate),
                'name': crate.name,
                'language': 'rust',
                'registry': 'crates.io'
            })
        
        return artifacts
    
    def _collect_java_artifacts(self, project_path: Path) -> List[Dict]:
        """Collect Java artifacts."""
        artifacts = []
        
        # JAR files
        for jar_dir in [project_path / 'target', project_path / 'build' / 'libs', project_path]:
            if jar_dir.exists():
                for jar in jar_dir.glob('*.jar'):
                    artifacts.append({
                        'type': 'jar',
                        'path': str(jar),
                        'name': jar.name,
                        'language': 'java',
                        'registry': 'maven'
                    })
        
        # WAR files
        for war in project_path.rglob('*.war'):
            artifacts.append({
                'type': 'war',
                'path': str(war),
                'name': war.name,
                'language': 'java',
                'registry': 'maven'
            })
        
        return artifacts
    
    def _collect_csharp_artifacts(self, project_path: Path) -> List[Dict]:
        """Collect .NET artifacts."""
        artifacts = []
        
        # NuGet packages
        for nupkg in project_path.rglob('*.nupkg'):
            artifacts.append({
                'type': 'nuget_package',
                'path': str(nupkg),
                'name': nupkg.name,
                'language': 'csharp',
                'registry': 'nuget'
            })
        
        # Executables and DLLs
        for bin_dir in project_path.rglob('bin'):
            if bin_dir.is_dir():
                for exe in bin_dir.glob('*.exe'):
                    artifacts.append({
                        'type': 'executable',
                        'path': str(exe),
                        'name': exe.name,
                        'language': 'csharp'
                    })
                
                for dll in bin_dir.glob('*.dll'):
                    artifacts.append({
                        'type': 'library',
                        'path': str(dll),
                        'name': dll.name,
                        'language': 'csharp'
                    })
        
        return artifacts
    
    def _collect_generic_artifacts(self, project_path: Path) -> List[Dict]:
        """Collect generic build artifacts."""
        artifacts = []
        
        # Look for common build outputs
        common_artifacts = [
            '*.tar.gz', '*.zip', '*.tar.bz2', '*.tar.xz',
            '*.deb', '*.rpm', '*.pkg', '*.msi'
        ]
        
        for pattern in common_artifacts:
            for artifact in project_path.glob(pattern):
                artifacts.append({
                    'type': 'archive',
                    'path': str(artifact),
                    'name': artifact.name,
                    'language': self.language
                })
        
        return artifacts
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _generate_sbom(self) -> Optional[Dict]:
        """Generate Software Bill of Materials using Syft."""
        try:
            # Check if syft is available
            result = subprocess.run(['syft', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                print("⚠️ Syft not available, skipping SBOM generation")
                return None
            
            sbom_file = f"sbom-{self.project_name}-{int(time.time())}.spdx.json"
            
            # Generate SBOM
            result = subprocess.run([
                'syft', self.project_path,
                '-o', f'spdx-json={sbom_file}'
            ], capture_output=True, text=True)
            
            if result.returncode == 0 and Path(sbom_file).exists():
                return {
                    'type': 'sbom',
                    'path': sbom_file,
                    'name': sbom_file,
                    'language': self.language,
                    'format': 'spdx-json'
                }
        
        except FileNotFoundError:
            print("⚠️ Syft not installed, skipping SBOM generation")
        except Exception as e:
            print(f"⚠️ SBOM generation failed: {e}")
        
        return None
    
    def _upload_artifacts(self, artifacts: List[Dict]) -> List[Dict]:
        """Upload artifacts to configured storage."""
        uploads = []
        
        # Check for AWS configuration
        if os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY'):
            s3_uploads = self._upload_to_s3(artifacts)
            uploads.extend(s3_uploads)
        
        # Check for other cloud providers
        if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            gcs_uploads = self._upload_to_gcs(artifacts)
            uploads.extend(gcs_uploads)
        
        if os.getenv('AZURE_STORAGE_CONNECTION_STRING'):
            azure_uploads = self._upload_to_azure(artifacts)
            uploads.extend(azure_uploads)
        
        return uploads
    
    def _upload_to_s3(self, artifacts: List[Dict]) -> List[Dict]:
        """Upload artifacts to AWS S3."""
        uploads = []
        bucket_name = os.getenv('S3_BUCKET_NAME', 'build-artifacts')
        
        try:
            s3_client = boto3.client('s3')
            
            for artifact in artifacts:
                if not Path(artifact['path']).exists():
                    continue
                
                key = f"{self.project_name}/{artifact['language']}/{artifact['name']}"
                
                try:
                    s3_client.upload_file(artifact['path'], bucket_name, key)
                    uploads.append({
                        'type': 's3',
                        'bucket': bucket_name,
                        'key': key,
                        'artifact': artifact['name'],
                        'status': 'success'
                    })
                    print(f"✅ Uploaded {artifact['name']} to S3")
                
                except Exception as e:
                    uploads.append({
                        'type': 's3',
                        'artifact': artifact['name'],
                        'status': 'failed',
                        'error': str(e)
                    })
                    print(f"❌ Failed to upload {artifact['name']} to S3: {e}")
        
        except Exception as e:
            print(f"❌ S3 upload setup failed: {e}")
        
        return uploads
    
    def _upload_to_gcs(self, artifacts: List[Dict]) -> List[Dict]:
        """Upload artifacts to Google Cloud Storage."""
        # Placeholder for GCS upload
        print("📦 GCS upload not implemented yet")
        return []
    
    def _upload_to_azure(self, artifacts: List[Dict]) -> List[Dict]:
        """Upload artifacts to Azure Blob Storage."""
        # Placeholder for Azure upload
        print("📦 Azure upload not implemented yet")
        return []
    
    def _deploy_to_cloud(self) -> List[Dict]:
        """Deploy to cloud platforms."""
        deployments = []
        
        # Docker deployment
        if Path(self.project_path, 'Dockerfile').exists():
            docker_deploy = self._deploy_docker()
            if docker_deploy:
                deployments.append(docker_deploy)
        
        # Kubernetes deployment
        k8s_files = list(Path(self.project_path).glob('k8s/*.yaml'))
        if k8s_files:
            k8s_deploy = self._deploy_kubernetes()
            if k8s_deploy:
                deployments.append(k8s_deploy)
        
        return deployments
    
    def _deploy_docker(self) -> Optional[Dict]:
        """Build and push Docker image."""
        try:
            image_name = f"{self.project_name}:{int(time.time())}"
            
            # Build image
            result = subprocess.run([
                'docker', 'build', '-t', image_name, self.project_path
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Docker image built: {image_name}")
                
                # Push to registry if configured
                registry = os.getenv('DOCKER_REGISTRY')
                if registry:
                    full_name = f"{registry}/{image_name}"
                    
                    # Tag for registry
                    subprocess.run(['docker', 'tag', image_name, full_name])
                    
                    # Push
                    push_result = subprocess.run([
                        'docker', 'push', full_name
                    ], capture_output=True, text=True)
                    
                    if push_result.returncode == 0:
                        print(f"✅ Docker image pushed: {full_name}")
                        return {
                            'type': 'docker',
                            'image': full_name,
                            'status': 'success'
                        }
                    else:
                        print(f"❌ Docker push failed: {push_result.stderr}")
                
                return {
                    'type': 'docker',
                    'image': image_name,
                    'status': 'built'
                }
            else:
                print(f"❌ Docker build failed: {result.stderr}")
        
        except Exception as e:
            print(f"❌ Docker deployment failed: {e}")
        
        return None
    
    def _deploy_kubernetes(self) -> Optional[Dict]:
        """Deploy to Kubernetes."""
        try:
            k8s_dir = Path(self.project_path) / 'k8s'
            
            result = subprocess.run([
                'kubectl', 'apply', '-f', str(k8s_dir), '--dry-run=client'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Kubernetes deployment validated")
                
                # Actual deployment would be conditional
                if os.getenv('DEPLOY_TO_K8S') == 'true':
                    deploy_result = subprocess.run([
                        'kubectl', 'apply', '-f', str(k8s_dir)
                    ], capture_output=True, text=True)
                    
                    if deploy_result.returncode == 0:
                        return {
                            'type': 'kubernetes',
                            'status': 'deployed'
                        }
                
                return {
                    'type': 'kubernetes',
                    'status': 'validated'
                }
        
        except Exception as e:
            print(f"❌ Kubernetes deployment failed: {e}")
        
        return None
    
    def _send_notifications(self) -> List[Dict]:
        """Send build notifications."""
        notifications = []
        
        # Slack notification
        slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        if slack_webhook:
            slack_notif = self._send_slack_notification(slack_webhook)
            if slack_notif:
                notifications.append(slack_notif)
        
        # Discord notification
        discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
        if discord_webhook:
            discord_notif = self._send_discord_notification(discord_webhook)
            if discord_notif:
                notifications.append(discord_notif)
        
        return notifications
    
    def _send_slack_notification(self, webhook_url: str) -> Optional[Dict]:
        """Send Slack notification."""
        try:
            import requests
            
            status = self.build_results.get('status', 'unknown')
            emoji = '✅' if status == 'success' else '❌'
            
            payload = {
                'text': f'{emoji} Build {status} for {self.project_name} ({self.language})',
                'attachments': [{
                    'color': 'good' if status == 'success' else 'danger',
                    'fields': [
                        {'title': 'Project', 'value': self.project_name, 'short': True},
                        {'title': 'Language', 'value': self.language, 'short': True},
                        {'title': 'Status', 'value': status, 'short': True}
                    ]
                }]
            }
            
            response = requests.post(webhook_url, json=payload)
            if response.status_code == 200:
                return {'type': 'slack', 'status': 'sent'}
        
        except Exception as e:
            print(f"❌ Slack notification failed: {e}")
        
        return None
    
    def _send_discord_notification(self, webhook_url: str) -> Optional[Dict]:
        """Send Discord notification."""
        try:
            import requests
            
            status = self.build_results.get('status', 'unknown')
            
            payload = {
                'content': f'Build {status} for **{self.project_name}** ({self.language})',
                'embeds': [{
                    'title': f'Build Report',
                    'color': 0x00ff00 if status == 'success' else 0xff0000,
                    'fields': [
                        {'name': 'Project', 'value': self.project_name, 'inline': True},
                        {'name': 'Language', 'value': self.language, 'inline': True},
                        {'name': 'Status', 'value': status, 'inline': True}
                    ]
                }]
            }
            
            response = requests.post(webhook_url, json=payload)
            if response.status_code in [200, 204]:
                return {'type': 'discord', 'status': 'sent'}
        
        except Exception as e:
            print(f"❌ Discord notification failed: {e}")
        
        return None

def main():
    """Main entry point for post-build hooks."""
    if len(sys.argv) < 3:
        print("Usage: python post-build.py <project_info_json> <build_results_json>")
        sys.exit(1)
    
    try:
        project_info = json.loads(sys.argv[1])
        build_results = json.loads(sys.argv[2])
        
        hooks = PostBuildHooks(project_info, build_results)
        result = hooks.execute()
        
        print(json.dumps(result, indent=2))
        
        if result['status'] != 'success':
            sys.exit(1)
    
    except Exception as e:
        print(f"Error running post-build hooks: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()