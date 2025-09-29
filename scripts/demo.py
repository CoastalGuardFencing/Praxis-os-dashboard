#!/usr/bin/env python3
"""
Demo script showcasing the Universal Build System capabilities.
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print(f"{'='*60}")

def print_step(step, description):
    """Print a formatted step."""
    print(f"\n📋 Step {step}: {description}")
    print("-" * 40)

def run_command(cmd, description=""):
    """Run a command and display results."""
    if description:
        print(f"💻 {description}")
    print(f"   Command: {cmd}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(f"✅ Output:\n{result.stdout}")
    if result.stderr and result.returncode != 0:
        print(f"❌ Error:\n{result.stderr}")
    
    return result.returncode == 0

def demo_project_detection():
    """Demo project detection capabilities."""
    print_header("Universal Project Detection")
    
    print("""
This demo shows how the Universal Build System automatically detects
projects across multiple programming languages in your repository.
    """)
    
    run_command(
        "python scripts/universal-builder.py --detect-only",
        "Detecting all projects in current directory"
    )

def demo_cli_wizard():
    """Demo CLI wizard capabilities."""
    print_header("Interactive CLI Wizard")
    
    print("""
The CLI wizard provides an interactive interface for common build operations.
Here's the help output showing available commands:
    """)
    
    run_command(
        "python scripts/cli-wizard.py --help",
        "Showing CLI wizard help"
    )

def demo_language_config():
    """Demo language configuration."""
    print_header("Language Configuration System")
    
    print("""
The system uses a centralized YAML configuration that defines build
commands for 20+ programming languages. Here's a sample:
    """)
    
    # Show a snippet of the language config
    try:
        with open("config/lang-config.yaml", "r") as f:
            lines = f.readlines()
            # Show first 30 lines
            print("".join(lines[:30]))
            print("... (truncated - see config/lang-config.yaml for full configuration)")
    except FileNotFoundError:
        print("❌ Language configuration file not found")

def demo_build_process():
    """Demo the build process."""
    print_header("Universal Build Process")
    
    print("""
The universal builder can run different operations across all detected projects.
Let's run install and lint operations:
    """)
    
    success = run_command(
        "python scripts/universal-builder.py --operations install lint",
        "Running install and lint operations across all projects"
    )
    
    if success:
        # Show build results
        try:
            with open("build-results-latest.json", "r") as f:
                results = json.load(f)
            
            print("\n📊 Build Results Summary:")
            summary = results.get("summary", {})
            print(f"   Total Projects: {summary.get('total_projects', 0)}")
            print(f"   Successful: {summary.get('successful_projects', 0)}")
            print(f"   Failed: {summary.get('failed_projects', 0)}")
            print(f"   Success Rate: {summary.get('success_rate', 0):.1%}")
            print(f"   Duration: {summary.get('total_duration', 0):.2f}s")
            
        except FileNotFoundError:
            print("❌ Build results file not found")

def demo_deployment_strategies():
    """Demo deployment strategies."""
    print_header("Deployment Strategies")
    
    print("""
The system supports multiple deployment strategies:
- Blue-Green: Zero-downtime deployments with instant rollback
- Canary: Gradual traffic shifting with monitoring
- Rolling: Progressive instance replacement

Here's the deployment help:
    """)
    
    run_command(
        "python automation/deploy.py --help",
        "Showing deployment options"
    )

def demo_self_update():
    """Demo self-update capabilities."""
    print_header("Self-Update System")
    
    print("""
The build system can automatically update itself from the repository.
Here's how to check for updates:
    """)
    
    run_command(
        "python scripts/self-update.py --check",
        "Checking for system updates"
    )

def demo_github_actions():
    """Demo GitHub Actions integration."""
    print_header("GitHub Actions Integration")
    
    print("""
The system includes a comprehensive GitHub Actions workflow that:
- Automatically detects projects
- Builds across multiple OS (Ubuntu, Windows, macOS)  
- Runs security scans
- Generates SBOM
- Deploys documentation

Here's the workflow file structure:
    """)
    
    try:
        with open(".github/workflows/universal-build.yml", "r") as f:
            lines = f.readlines()
            # Show first 20 lines to give an idea
            print("".join(lines[:20]))
            print("... (see .github/workflows/universal-build.yml for complete workflow)")
    except FileNotFoundError:
        print("❌ GitHub Actions workflow file not found")

def demo_observability():
    """Demo observability features."""
    print_header("Observability & Monitoring")
    
    print("""
The system integrates with multiple monitoring platforms:
- Prometheus: Build metrics and success rates
- DataDog: Events, dashboards, alerting
- OpenTelemetry: Distributed tracing

Here's the observability help:
    """)
    
    run_command(
        "python automation/observability.py --help",
        "Showing observability options"
    )

def demo_file_structure():
    """Show the project file structure."""
    print_header("Project Architecture")
    
    print("""
The Universal Build System is organized into several key components:

📁 Project Structure:
    """)
    
    structure = """
├── 🎛️ config/                  # Centralized configurations
│   ├── lang-config.yaml         # Language build definitions  
│   └── deploy-config.yaml       # Deployment strategies
├── 🤖 scripts/                 # Core automation scripts
│   ├── universal-builder.py     # Main build orchestrator
│   ├── cli-wizard.py           # Interactive CLI
│   ├── self-update.py          # Auto-update system
│   └── demo.py                 # This demo script
├── 🔗 hooks/                   # Build lifecycle hooks
│   ├── pre-build.py            # Pre-build automation
│   └── post-build.py           # Post-build processing
├── 🚀 automation/              # Deployment & observability
│   ├── deploy.py               # Multi-strategy deployment
│   └── observability.py        # Monitoring integration
├── 📚 docs/                    # Documentation
│   └── README.md               # Comprehensive guide
└── 🔧 .github/workflows/       # CI/CD pipelines
    └── universal-build.yml     # GitHub Actions workflow
    """
    
    print(structure)

def show_statistics():
    """Show project statistics."""
    print_header("Project Statistics")
    
    print("""
📊 Universal Build System Statistics:
    """)
    
    # Count lines of code
    total_lines = 0
    file_count = 0
    
    for pattern in ["scripts/*.py", "hooks/*.py", "automation/*.py", "config/*.yaml", ".github/workflows/*.yml"]:
        import glob
        for file_path in glob.glob(pattern):
            try:
                with open(file_path, 'r') as f:
                    lines = len(f.readlines())
                    total_lines += lines
                    file_count += 1
            except:
                pass
    
    print(f"   📝 Total Files: {file_count}")
    print(f"   📏 Total Lines of Code: {total_lines:,}")
    print(f"   🌐 Supported Languages: 20+")
    print(f"   🚀 Deployment Strategies: 3")
    print(f"   📊 Monitoring Integrations: 3")
    print(f"   ☁️ Cloud Providers: 3")
    print(f"   🛡️ Security Tools: 4+")

def main():
    """Run the complete demo."""
    print("""
🎉 Welcome to the Universal Code Builder & Automation Platform Demo!

This demonstration will showcase the key features and capabilities
of our comprehensive multi-language build system.
    """)
    
    print("\n⏰ Starting demo in 3 seconds...")
    time.sleep(3)
    
    # Run all demo sections
    demo_file_structure()
    demo_project_detection()
    demo_language_config()
    demo_cli_wizard()
    demo_build_process()
    demo_deployment_strategies()
    demo_self_update()
    demo_github_actions()
    demo_observability()
    show_statistics()
    
    print_header("Demo Complete!")
    
    print("""
🎊 Congratulations! You've seen the Universal Build System in action.

Key Takeaways:
✅ Detects projects in 20+ programming languages automatically
✅ Centralized configuration for all build processes
✅ Interactive CLI for easy operation
✅ Multiple deployment strategies (blue-green, canary, rolling)
✅ Comprehensive observability and monitoring
✅ Self-updating capabilities
✅ GitHub Actions integration
✅ Security and compliance features
✅ Cloud-native with multi-provider support

Next Steps:
1. Explore the configuration files in config/
2. Try the interactive CLI: python scripts/cli-wizard.py
3. Run builds on your projects: python scripts/universal-builder.py
4. Set up deployments with automation/deploy.py
5. Configure monitoring with automation/observability.py

For more information, see:
📖 docs/README.md - Complete documentation
🔧 config/ - Configuration examples
🚀 automation/ - Deployment and monitoring tools

Happy building! 🚀
    """)

if __name__ == "__main__":
    main()