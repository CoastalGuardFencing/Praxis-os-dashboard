#!/usr/bin/env python3
"""
Universal Code Builder and Automation Platform
Detects projects in all languages and runs appropriate build/test/lint/package operations.
"""

import os
import sys
import json
import yaml
import subprocess
import concurrent.futures
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('build.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ProjectDetector:
    """Detects and classifies projects by language/framework."""
    
    def __init__(self, config_path: str = "config/lang-config.yaml"):
        self.config = self._load_config(config_path)
        self.languages = self.config.get('languages', {})
    
    def _load_config(self, config_path: str) -> Dict:
        """Load language configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {config_path}")
            return {}
        except yaml.YAMLError as e:
            logger.error(f"Error parsing config file: {e}")
            return {}
    
    def detect_projects(self, root_path: str = ".") -> List[Dict]:
        """Detect all projects in the given directory tree."""
        projects = []
        root = Path(root_path)
        
        # Walk through directory tree
        for current_dir in root.rglob("*"):
            if not current_dir.is_dir():
                continue
                
            # Skip common non-project directories
            if any(skip in str(current_dir) for skip in [
                'node_modules', '__pycache__', '.git', 
                'target', 'build', 'dist', '.venv', 'venv'
            ]):
                continue
            
            project_info = self._analyze_directory(current_dir)
            if project_info:
                projects.append(project_info)
        
        return projects
    
    def _analyze_directory(self, directory: Path) -> Optional[Dict]:
        """Analyze a directory to determine if it contains a project."""
        files = list(directory.iterdir())
        file_names = [f.name for f in files if f.is_file()]
        
        detected_languages = []
        
        # Check for project files (definitive indicators)
        for lang_name, lang_config in self.languages.items():
            project_files = lang_config.get('project_files', [])
            if any(pf in file_names for pf in project_files):
                detected_languages.append({
                    'language': lang_name,
                    'confidence': 0.9,
                    'reason': f"Found project files: {[pf for pf in project_files if pf in file_names]}"
                })
        
        # Check for source files (weaker indicators)
        for lang_name, lang_config in self.languages.items():
            patterns = lang_config.get('file_patterns', [])
            matching_files = []
            for pattern in patterns:
                pattern = pattern.replace('*', '')
                matching_files.extend([f for f in file_names if f.endswith(pattern)])
            
            if matching_files and len(matching_files) > 2:  # Need multiple files
                detected_languages.append({
                    'language': lang_name,
                    'confidence': 0.6,
                    'reason': f"Found {len(matching_files)} source files"
                })
        
        if not detected_languages:
            return None
        
        # Sort by confidence and take the highest
        detected_languages.sort(key=lambda x: x['confidence'], reverse=True)
        primary_language = detected_languages[0]
        
        return {
            'path': str(directory),
            'name': directory.name,
            'language': primary_language['language'],
            'confidence': primary_language['confidence'],
            'detected_languages': detected_languages,
            'files': file_names
        }

class UniversalBuilder:
    """Main builder class that orchestrates the build process."""
    
    def __init__(self, config_path: str = "config/lang-config.yaml"):
        self.detector = ProjectDetector(config_path)
        self.config = self.detector.config
        self.results = {
            'build_id': self._generate_build_id(),
            'timestamp': datetime.now().isoformat(),
            'projects': [],
            'summary': {},
            'errors': []
        }
    
    def _generate_build_id(self) -> str:
        """Generate unique build ID."""
        return f"build-{int(time.time())}"
    
    def build_all(self, root_path: str = ".", operations: List[str] = None) -> Dict:
        """Build all detected projects."""
        if operations is None:
            operations = ['install', 'lint', 'test', 'build', 'package']
        
        logger.info(f"Starting universal build process...")
        logger.info(f"Build ID: {self.results['build_id']}")
        
        # Detect projects
        projects = self.detector.detect_projects(root_path)
        logger.info(f"Detected {len(projects)} projects")
        
        # Filter out low-confidence detections (lowered threshold for development)
        high_confidence_projects = [p for p in projects if p['confidence'] > 0.5]
        logger.info(f"Building {len(high_confidence_projects)} high-confidence projects")
        
        # Build projects
        if self.config.get('global', {}).get('parallel_builds', True):
            self._build_parallel(high_confidence_projects, operations)
        else:
            self._build_sequential(high_confidence_projects, operations)
        
        # Generate summary
        self._generate_summary()
        
        # Save results
        self._save_results()
        
        return self.results
    
    def _build_parallel(self, projects: List[Dict], operations: List[str]):
        """Build projects in parallel."""
        max_workers = self.config.get('global', {}).get('max_parallel', 4)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self._build_project, project, operations): project 
                for project in projects
            }
            
            for future in concurrent.futures.as_completed(futures):
                project = futures[future]
                try:
                    result = future.result()
                    self.results['projects'].append(result)
                except Exception as e:
                    logger.error(f"Failed to build {project['name']}: {e}")
                    self.results['errors'].append({
                        'project': project['name'],
                        'error': str(e)
                    })
    
    def _build_sequential(self, projects: List[Dict], operations: List[str]):
        """Build projects sequentially."""
        for project in projects:
            try:
                result = self._build_project(project, operations)
                self.results['projects'].append(result)
            except Exception as e:
                logger.error(f"Failed to build {project['name']}: {e}")
                self.results['errors'].append({
                    'project': project['name'],
                    'error': str(e)
                })
    
    def _build_project(self, project: Dict, operations: List[str]) -> Dict:
        """Build a single project."""
        logger.info(f"Building project: {project['name']} ({project['language']})")
        
        language = project['language']
        lang_config = self.config['languages'].get(language, {})
        commands = lang_config.get('commands', {})
        
        project_result = {
            'name': project['name'],
            'path': project['path'],
            'language': language,
            'operations': {},
            'status': 'success',
            'duration': 0,
            'artifacts': []
        }
        
        start_time = time.time()
        
        # Change to project directory
        original_cwd = os.getcwd()
        os.chdir(project['path'])
        
        try:
            for operation in operations:
                if operation in commands:
                    command = commands[operation]
                    if command and command.strip():
                        result = self._run_command(command, operation)
                        project_result['operations'][operation] = result
                        
                        if not result['success']:
                            project_result['status'] = 'failed'
                            logger.warning(f"Operation {operation} failed for {project['name']}")
                    else:
                        logger.info(f"Skipping {operation} for {project['name']} (no command defined)")
                        project_result['operations'][operation] = {
                            'success': True,
                            'skipped': True,
                            'message': 'No command defined'
                        }
        
        except Exception as e:
            project_result['status'] = 'error'
            project_result['error'] = str(e)
            logger.error(f"Error building {project['name']}: {e}")
        
        finally:
            os.chdir(original_cwd)
            project_result['duration'] = time.time() - start_time
        
        return project_result
    
    def _run_command(self, command: str, operation: str) -> Dict:
        """Run a shell command and return result."""
        logger.info(f"Running {operation}: {command}")
        
        try:
            # Handle command chains (||)
            if '||' in command:
                commands = [cmd.strip() for cmd in command.split('||')]
                for cmd in commands:
                    result = subprocess.run(
                        cmd, shell=True, capture_output=True, text=True, timeout=300
                    )
                    if result.returncode == 0:
                        return {
                            'success': True,
                            'command': cmd,
                            'stdout': result.stdout,
                            'stderr': result.stderr,
                            'return_code': result.returncode
                        }
                
                # If all commands failed
                return {
                    'success': False,
                    'command': command,
                    'stdout': result.stdout if 'result' in locals() else '',
                    'stderr': result.stderr if 'result' in locals() else 'All alternatives failed',
                    'return_code': result.returncode if 'result' in locals() else 1
                }
            else:
                result = subprocess.run(
                    command, shell=True, capture_output=True, text=True, timeout=300
                )
                return {
                    'success': result.returncode == 0,
                    'command': command,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'return_code': result.returncode
                }
        
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'command': command,
                'error': 'Command timed out',
                'return_code': -1
            }
        except Exception as e:
            return {
                'success': False,
                'command': command,
                'error': str(e),
                'return_code': -1
            }
    
    def _generate_summary(self):
        """Generate build summary."""
        total_projects = len(self.results['projects'])
        successful_projects = len([p for p in self.results['projects'] if p['status'] == 'success'])
        failed_projects = len([p for p in self.results['projects'] if p['status'] == 'failed'])
        error_projects = len([p for p in self.results['projects'] if p['status'] == 'error'])
        
        # Language breakdown
        language_stats = {}
        for project in self.results['projects']:
            lang = project['language']
            if lang not in language_stats:
                language_stats[lang] = {'total': 0, 'success': 0, 'failed': 0}
            
            language_stats[lang]['total'] += 1
            if project['status'] == 'success':
                language_stats[lang]['success'] += 1
            else:
                language_stats[lang]['failed'] += 1
        
        self.results['summary'] = {
            'total_projects': total_projects,
            'successful_projects': successful_projects,
            'failed_projects': failed_projects,
            'error_projects': error_projects,
            'success_rate': successful_projects / total_projects if total_projects > 0 else 0,
            'language_stats': language_stats,
            'total_duration': sum(p.get('duration', 0) for p in self.results['projects'])
        }
    
    def _save_results(self):
        """Save build results to file."""
        results_file = f"build-results-{self.results['build_id']}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Also save latest results
        with open('build-results-latest.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"Results saved to {results_file}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Universal Code Builder')
    parser.add_argument('--path', default='.', help='Root path to scan for projects')
    parser.add_argument('--operations', nargs='+', 
                       default=['install', 'lint', 'test', 'build', 'package'],
                       help='Operations to perform')
    parser.add_argument('--config', default='config/lang-config.yaml',
                       help='Path to language configuration file')
    parser.add_argument('--detect-only', action='store_true',
                       help='Only detect projects, don\'t build')
    
    args = parser.parse_args()
    
    try:
        builder = UniversalBuilder(args.config)
        
        if args.detect_only:
            projects = builder.detector.detect_projects(args.path)
            print(f"Detected {len(projects)} projects:")
            for project in projects:
                print(f"  - {project['name']} ({project['language']}) - {project['confidence']:.1%} confidence")
        else:
            results = builder.build_all(args.path, args.operations)
            
            # Print summary
            summary = results['summary']
            print(f"\n=== Build Summary ===")
            print(f"Total Projects: {summary['total_projects']}")
            print(f"Successful: {summary['successful_projects']}")
            print(f"Failed: {summary['failed_projects']}")
            print(f"Errors: {summary['error_projects']}")
            print(f"Success Rate: {summary['success_rate']:.1%}")
            print(f"Total Duration: {summary['total_duration']:.2f}s")
            
            # Language breakdown
            print(f"\n=== Language Breakdown ===")
            for lang, stats in summary['language_stats'].items():
                print(f"{lang}: {stats['success']}/{stats['total']} successful")
            
            # Exit with error code if any builds failed
            if summary['failed_projects'] > 0 or summary['error_projects'] > 0:
                sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("Build interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Build failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()