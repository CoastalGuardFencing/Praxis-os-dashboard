#!/usr/bin/env python3
"""
CLI Wizard for Universal Build System
Interactive command-line interface for build/run/format/test/package workflows.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import argparse

class CLIWizard:
    """Interactive CLI wizard for build operations."""
    
    def __init__(self):
        self.builder_script = Path(__file__).parent / "universal-builder.py"
        self.available_operations = [
            'detect', 'install', 'build', 'test', 'lint', 
            'format', 'package', 'clean', 'run', 'deploy'
        ]
    
    def run_interactive(self):
        """Run interactive wizard."""
        print("🚀 Universal Code Builder - CLI Wizard")
        print("=" * 50)
        
        # Get project path
        path = self._get_project_path()
        
        # Detect projects first
        projects = self._detect_projects(path)
        if not projects:
            print("❌ No projects detected in the specified path.")
            return
        
        # Show detected projects
        self._show_detected_projects(projects)
        
        # Get operations to perform
        operations = self._get_operations()
        
        # Confirm and run
        if self._confirm_execution(path, operations):
            self._run_builder(path, operations)
        else:
            print("❌ Operation cancelled.")
    
    def _get_project_path(self) -> str:
        """Get project path from user."""
        while True:
            path = input(f"📁 Enter project path (default: current directory): ").strip()
            if not path:
                path = "."
            
            if os.path.exists(path):
                return os.path.abspath(path)
            else:
                print(f"❌ Path '{path}' does not exist. Please try again.")
    
    def _detect_projects(self, path: str) -> List[Dict]:
        """Detect projects in the given path."""
        print(f"🔍 Detecting projects in {path}...")
        
        try:
            result = subprocess.run([
                sys.executable, str(self.builder_script),
                "--path", path, "--detect-only"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Parse output to extract project info
                # This is a simplified parsing - in real implementation,
                # we'd return structured data from the builder
                lines = result.stdout.strip().split('\n')
                projects = []
                for line in lines:
                    if ' - ' in line and '(' in line and ')' in line:
                        # Parse format: "  - name (language) - confidence"
                        parts = line.strip().split(' - ')
                        if len(parts) >= 2:
                            name_lang = parts[1]
                            if '(' in name_lang and ')' in name_lang:
                                name = name_lang.split('(')[0].strip()
                                lang = name_lang.split('(')[1].split(')')[0]
                                projects.append({'name': name, 'language': lang})
                
                return projects
            else:
                print(f"❌ Failed to detect projects: {result.stderr}")
                return []
        
        except subprocess.TimeoutExpired:
            print("❌ Project detection timed out.")
            return []
        except Exception as e:
            print(f"❌ Error detecting projects: {e}")
            return []
    
    def _show_detected_projects(self, projects: List[Dict]):
        """Show detected projects to user."""
        print(f"\n✅ Detected {len(projects)} project(s):")
        for i, project in enumerate(projects, 1):
            print(f"  {i}. {project['name']} ({project['language']})")
        print()
    
    def _get_operations(self) -> List[str]:
        """Get operations to perform from user."""
        print("🔧 Available operations:")
        for i, op in enumerate(self.available_operations, 1):
            print(f"  {i}. {op}")
        
        print("\nSelect operations to perform:")
        print("  - Enter numbers separated by commas (e.g., 1,3,4)")
        print("  - Enter 'all' for all operations")
        print("  - Enter 'quick' for install,lint,test,build")
        
        while True:
            choice = input("📝 Operations: ").strip().lower()
            
            if choice == 'all':
                return self.available_operations[1:]  # Skip 'detect'
            elif choice == 'quick':
                return ['install', 'lint', 'test', 'build']
            elif choice:
                try:
                    # Parse comma-separated numbers
                    indices = [int(x.strip()) - 1 for x in choice.split(',')]
                    operations = [self.available_operations[i] for i in indices 
                                 if 0 <= i < len(self.available_operations)]
                    if operations:
                        return operations
                    else:
                        print("❌ Invalid selection. Please try again.")
                except (ValueError, IndexError):
                    print("❌ Invalid input. Please enter numbers or 'all'/'quick'.")
            else:
                print("❌ Please enter a selection.")
    
    def _confirm_execution(self, path: str, operations: List[str]) -> bool:
        """Confirm execution with user."""
        print(f"\n📋 Summary:")
        print(f"  Path: {path}")
        print(f"  Operations: {', '.join(operations)}")
        
        while True:
            confirm = input(f"\n🚀 Proceed with build? (y/n): ").strip().lower()
            if confirm in ('y', 'yes'):
                return True
            elif confirm in ('n', 'no'):
                return False
            else:
                print("❌ Please enter 'y' or 'n'.")
    
    def _run_builder(self, path: str, operations: List[str]):
        """Run the universal builder."""
        print(f"\n🔨 Starting build process...")
        
        cmd = [
            sys.executable, str(self.builder_script),
            "--path", path,
            "--operations"
        ] + operations
        
        try:
            # Run with real-time output
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                universal_newlines=True, bufsize=1
            )
            
            # Stream output
            for line in process.stdout:
                print(line.rstrip())
            
            process.wait()
            
            if process.returncode == 0:
                print(f"\n✅ Build completed successfully!")
            else:
                print(f"\n❌ Build failed with exit code {process.returncode}")
        
        except KeyboardInterrupt:
            print(f"\n⚠️ Build interrupted by user")
            if process:
                process.terminate()
        except Exception as e:
            print(f"\n❌ Error running build: {e}")

class QuickCommands:
    """Quick command utilities."""
    
    @staticmethod
    def format_code(path: str = "."):
        """Quick format code."""
        print("🎨 Formatting code...")
        subprocess.run([
            sys.executable, 
            Path(__file__).parent / "universal-builder.py",
            "--path", path, "--operations", "format"
        ])
    
    @staticmethod
    def run_tests(path: str = "."):
        """Quick test run."""
        print("🧪 Running tests...")
        subprocess.run([
            sys.executable,
            Path(__file__).parent / "universal-builder.py", 
            "--path", path, "--operations", "test"
        ])
    
    @staticmethod
    def lint_code(path: str = "."):
        """Quick lint check."""
        print("🔍 Linting code...")
        subprocess.run([
            sys.executable,
            Path(__file__).parent / "universal-builder.py",
            "--path", path, "--operations", "lint"
        ])
    
    @staticmethod
    def build_all(path: str = "."):
        """Quick build all."""
        print("🔨 Building all projects...")
        subprocess.run([
            sys.executable,
            Path(__file__).parent / "universal-builder.py",
            "--path", path, "--operations", "install", "build", "test"
        ])

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='CLI Wizard for Universal Build System')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Run interactive wizard')
    parser.add_argument('--format', action='store_true',
                       help='Quick format code')
    parser.add_argument('--test', action='store_true', 
                       help='Quick run tests')
    parser.add_argument('--lint', action='store_true',
                       help='Quick lint code')
    parser.add_argument('--build', action='store_true',
                       help='Quick build all')
    parser.add_argument('--path', default='.',
                       help='Project path')
    
    args = parser.parse_args()
    
    if args.interactive or len(sys.argv) == 1:
        # Run interactive wizard if no specific command or --interactive flag
        wizard = CLIWizard()
        wizard.run_interactive()
    elif args.format:
        QuickCommands.format_code(args.path)
    elif args.test:
        QuickCommands.run_tests(args.path)
    elif args.lint:
        QuickCommands.lint_code(args.path)
    elif args.build:
        QuickCommands.build_all(args.path)
    else:
        # Show help if no valid option
        parser.print_help()

if __name__ == '__main__':
    main()