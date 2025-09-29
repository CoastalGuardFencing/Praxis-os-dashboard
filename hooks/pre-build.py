#!/usr/bin/env python3
"""
Pre-build hooks for different languages and frameworks.
Executed before the main build process starts.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

class PreBuildHooks:
    """Pre-build hooks for various languages."""
    
    def __init__(self, project_info: Dict):
        self.project_info = project_info
        self.language = project_info.get('language', '')
        self.project_path = project_info.get('path', '.')
    
    def execute(self) -> Dict:
        """Execute appropriate pre-build hooks."""
        print(f"🔧 Running pre-build hooks for {self.language}...")
        
        hook_method = f"_hook_{self.language}"
        if hasattr(self, hook_method):
            return getattr(self, hook_method)()
        else:
            return self._hook_generic()
    
    def _hook_javascript(self) -> Dict:
        """JavaScript/Node.js pre-build hooks."""
        results = {'status': 'success', 'actions': []}
        
        # Check Node.js version
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                results['actions'].append(f"Node.js version: {result.stdout.strip()}")
            else:
                results['actions'].append("Warning: Node.js not found")
        except FileNotFoundError:
            results['actions'].append("Warning: Node.js not installed")
        
        # Check for package.json and install dependencies
        package_json = Path(self.project_path) / 'package.json'
        if package_json.exists():
            # Check if node_modules exists and is up to date
            node_modules = Path(self.project_path) / 'node_modules'
            if not node_modules.exists():
                results['actions'].append("node_modules directory missing - will install dependencies")
            
            # Check for security vulnerabilities
            try:
                result = subprocess.run(['npm', 'audit', '--audit-level=moderate'], 
                                      cwd=self.project_path, capture_output=True, text=True)
                if result.returncode != 0:
                    results['actions'].append("Warning: npm audit found vulnerabilities")
            except FileNotFoundError:
                pass
        
        return results
    
    def _hook_python(self) -> Dict:
        """Python pre-build hooks."""
        results = {'status': 'success', 'actions': []}
        
        # Check Python version
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        results['actions'].append(f"Python version: {python_version}")
        
        # Check for virtual environment
        if hasattr(sys, 'prefix') and hasattr(sys, 'base_prefix'):
            if sys.prefix != sys.base_prefix:
                results['actions'].append("Virtual environment detected")
            else:
                results['actions'].append("Warning: No virtual environment detected")
        
        # Check for requirements files
        req_files = ['requirements.txt', 'pyproject.toml', 'Pipfile', 'poetry.lock']
        project_path = Path(self.project_path)
        
        found_req_files = [f for f in req_files if (project_path / f).exists()]
        if found_req_files:
            results['actions'].append(f"Found dependency files: {', '.join(found_req_files)}")
        else:
            results['actions'].append("Warning: No dependency files found")
        
        # Check for __pycache__ directories
        pycache_dirs = list(project_path.rglob('__pycache__'))
        if pycache_dirs:
            results['actions'].append(f"Found {len(pycache_dirs)} __pycache__ directories")
        
        return results
    
    def _hook_go(self) -> Dict:
        """Go pre-build hooks."""
        results = {'status': 'success', 'actions': []}
        
        # Check Go version
        try:
            result = subprocess.run(['go', 'version'], capture_output=True, text=True)
            if result.returncode == 0:
                results['actions'].append(f"Go version: {result.stdout.strip()}")
            else:
                results['status'] = 'error'
                results['actions'].append("Error: Go not found")
                return results
        except FileNotFoundError:
            results['status'] = 'error'
            results['actions'].append("Error: Go not installed")
            return results
        
        # Check for go.mod
        go_mod = Path(self.project_path) / 'go.mod'
        if go_mod.exists():
            results['actions'].append("Found go.mod file")
            
            # Check for indirect dependencies
            try:
                result = subprocess.run(['go', 'list', '-m', 'all'], 
                                      cwd=self.project_path, capture_output=True, text=True)
                if result.returncode == 0:
                    deps = result.stdout.strip().split('\n')
                    results['actions'].append(f"Found {len(deps)} dependencies")
            except Exception:
                pass
        else:
            results['actions'].append("Warning: No go.mod file found")
        
        return results
    
    def _hook_rust(self) -> Dict:
        """Rust pre-build hooks."""
        results = {'status': 'success', 'actions': []}
        
        # Check Rust version
        try:
            result = subprocess.run(['rustc', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                results['actions'].append(f"Rust version: {result.stdout.strip()}")
        except FileNotFoundError:
            results['status'] = 'error'
            results['actions'].append("Error: Rust not installed")
            return results
        
        # Check for Cargo.toml
        cargo_toml = Path(self.project_path) / 'Cargo.toml'
        if cargo_toml.exists():
            results['actions'].append("Found Cargo.toml file")
            
            # Check for target directory
            target_dir = Path(self.project_path) / 'target'
            if target_dir.exists():
                # Get size of target directory
                try:
                    size = sum(f.stat().st_size for f in target_dir.rglob('*') if f.is_file())
                    size_mb = size / (1024 * 1024)
                    results['actions'].append(f"Target directory size: {size_mb:.1f} MB")
                    
                    if size_mb > 500:  # More than 500MB
                        results['actions'].append("Warning: Large target directory - consider cleaning")
                except Exception:
                    pass
        else:
            results['actions'].append("Warning: No Cargo.toml file found")
        
        return results
    
    def _hook_java(self) -> Dict:
        """Java pre-build hooks."""
        results = {'status': 'success', 'actions': []}
        
        # Check Java version
        try:
            result = subprocess.run(['java', '-version'], capture_output=True, text=True)
            if result.returncode == 0:
                # Java prints version to stderr
                version_info = result.stderr.split('\n')[0]
                results['actions'].append(f"Java version: {version_info}")
        except FileNotFoundError:
            results['status'] = 'error'
            results['actions'].append("Error: Java not installed")
            return results
        
        # Check for build files
        project_path = Path(self.project_path)
        if (project_path / 'pom.xml').exists():
            results['actions'].append("Found Maven project (pom.xml)")
            
            # Check for Maven
            try:
                result = subprocess.run(['mvn', '--version'], capture_output=True, text=True)
                if result.returncode == 0:
                    results['actions'].append("Maven available")
            except FileNotFoundError:
                results['actions'].append("Warning: Maven not found")
        
        elif (project_path / 'build.gradle').exists() or (project_path / 'build.gradle.kts').exists():
            results['actions'].append("Found Gradle project")
            
            # Check for Gradle wrapper
            if (project_path / 'gradlew').exists():
                results['actions'].append("Gradle wrapper found")
            else:
                results['actions'].append("Warning: No Gradle wrapper found")
        
        return results
    
    def _hook_csharp(self) -> Dict:
        """C#/.NET pre-build hooks."""
        results = {'status': 'success', 'actions': []}
        
        # Check .NET version
        try:
            result = subprocess.run(['dotnet', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                results['actions'].append(f".NET version: {result.stdout.strip()}")
        except FileNotFoundError:
            results['status'] = 'error'
            results['actions'].append("Error: .NET not installed")
            return results
        
        # Check for project files
        project_path = Path(self.project_path)
        csproj_files = list(project_path.glob('*.csproj'))
        sln_files = list(project_path.glob('*.sln'))
        
        if csproj_files:
            results['actions'].append(f"Found {len(csproj_files)} .csproj file(s)")
        if sln_files:
            results['actions'].append(f"Found {len(sln_files)} solution file(s)")
        
        if not csproj_files and not sln_files:
            results['actions'].append("Warning: No .NET project files found")
        
        return results
    
    def _hook_generic(self) -> Dict:
        """Generic pre-build hooks for unknown languages."""
        results = {'status': 'success', 'actions': []}
        
        # Check for common build files
        project_path = Path(self.project_path)
        build_files = [
            'Makefile', 'makefile', 'CMakeLists.txt', 'configure',
            'build.sh', 'build.py', 'build.js'
        ]
        
        found_files = [f for f in build_files if (project_path / f).exists()]
        if found_files:
            results['actions'].append(f"Found build files: {', '.join(found_files)}")
        else:
            results['actions'].append("No standard build files detected")
        
        # Check directory size
        try:
            total_size = sum(f.stat().st_size for f in project_path.rglob('*') if f.is_file())
            size_mb = total_size / (1024 * 1024)
            results['actions'].append(f"Project size: {size_mb:.1f} MB")
        except Exception:
            pass
        
        return results

def main():
    """Main entry point for pre-build hooks."""
    if len(sys.argv) < 2:
        print("Usage: python pre-build.py <project_info_json>")
        sys.exit(1)
    
    try:
        project_info = json.loads(sys.argv[1])
        hooks = PreBuildHooks(project_info)
        result = hooks.execute()
        
        print(json.dumps(result, indent=2))
        
        if result['status'] != 'success':
            sys.exit(1)
    
    except Exception as e:
        print(f"Error running pre-build hooks: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()