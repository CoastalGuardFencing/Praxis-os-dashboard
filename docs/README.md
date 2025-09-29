# Universal Code Builder and Automation Platform

A comprehensive, multi-language build automation platform that detects, builds, tests, and deploys projects across various programming languages and frameworks.

## 🚀 Features

### Core Capabilities
- **Universal Project Detection**: Automatically detects projects in 20+ programming languages
- **Centralized Configuration**: Single YAML configuration for all language build processes
- **Parallel Builds**: Efficient parallel execution across multiple projects
- **Build Hooks**: Pre/post-build hooks for custom automation
- **Deployment Strategies**: Blue/green, canary, and rolling deployments
- **Self-Updating**: Automatic updates from repository
- **CLI Wizard**: Interactive command-line interface
- **Dashboard Integration**: Real-time build status and results display
- **Observability**: Integration with Prometheus, DataDog, OpenTelemetry

### Supported Languages & Frameworks
- **JavaScript/TypeScript**: Node.js, React, Vue, Angular
- **Python**: Django, Flask, FastAPI, setuptools, poetry
- **Go**: Standard Go toolchain, modules
- **Rust**: Cargo ecosystem
- **Java**: Maven, Gradle
- **C#/.NET**: .NET Core, .NET Framework
- **Ruby**: Bundler, RubyGems
- **PHP**: Composer
- **Swift**: Package Manager, Xcode
- **Kotlin**: Gradle, Maven
- **C/C++**: Make, CMake
- **Scala**: SBT, Maven
- **Dart/Flutter**: Pub package manager
- **Elixir**: Mix
- **Shell Scripts**: Bash, Zsh
- **R**: CRAN packages
- **Perl**: CPAN
- **Haskell**: Stack, Cabal
- **Julia**: Package manager
- **Clojure**: Leiningen, tools.deps

## 📁 Project Structure

```
├── config/
│   ├── lang-config.yaml      # Language configurations
│   └── deploy-config.yaml    # Deployment configurations
├── scripts/
│   ├── universal-builder.py  # Main build orchestrator
│   ├── cli-wizard.py         # Interactive CLI
│   └── self-update.py        # Self-updating system
├── hooks/
│   ├── pre-build.py          # Pre-build hooks
│   └── post-build.py         # Post-build hooks
├── automation/
│   ├── deploy.py             # Deployment automation
│   └── observability.py     # Monitoring integration
├── .github/workflows/
│   └── universal-build.yml   # GitHub Actions workflow
└── docs/
    └── README.md             # This file
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.9+
- Git
- Language-specific tools (Node.js, Python, Go, etc.)

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/CoastalGuardFencing/Praxis-os-dashboard.git
   cd Praxis-os-dashboard
   ```

2. **Install dependencies**:
   ```bash
   pip install pyyaml requests boto3
   ```

3. **Make scripts executable**:
   ```bash
   chmod +x scripts/*.py hooks/*.py automation/*.py
   ```

4. **Detect projects**:
   ```bash
   python scripts/universal-builder.py --detect-only
   ```

5. **Run interactive wizard**:
   ```bash
   python scripts/cli-wizard.py
   ```

## 🎯 Usage

### Command Line Interface

#### Universal Builder
```bash
# Detect all projects
python scripts/universal-builder.py --detect-only

# Build all projects
python scripts/universal-builder.py

# Build with specific operations
python scripts/universal-builder.py --operations install lint test build

# Build specific path
python scripts/universal-builder.py --path /path/to/projects
```

#### CLI Wizard (Interactive)
```bash
# Start interactive wizard
python scripts/cli-wizard.py

# Quick commands
python scripts/cli-wizard.py --build
python scripts/cli-wizard.py --test
python scripts/cli-wizard.py --lint
python scripts/cli-wizard.py --format
```

#### Deployment
```bash
# Blue-green deployment
python automation/deploy.py --environment production --strategy blue-green --image myapp:v1.2.0

# Canary deployment
python automation/deploy.py --environment staging --strategy canary --image myapp:v1.2.0

# Rolling deployment
python automation/deploy.py --environment development --strategy rolling --image myapp:v1.2.0
```

#### Self-Update
```bash
# Check for updates
python scripts/self-update.py --check

# Update system
python scripts/self-update.py --update

# Force update
python scripts/self-update.py --update --force
```

### GitHub Actions Integration

The system includes a comprehensive GitHub Actions workflow that:
- Automatically detects projects in your repository
- Builds across multiple operating systems (Ubuntu, Windows, macOS)
- Runs security scans with Trivy
- Generates Software Bill of Materials (SBOM)
- Performs compliance checks
- Generates and deploys documentation

### Configuration

#### Language Configuration (`config/lang-config.yaml`)
Defines build commands, file patterns, and settings for each supported language:

```yaml
languages:
  python:
    name: "Python"
    file_patterns: ["*.py"]
    project_files: ["requirements.txt", "pyproject.toml", "setup.py"]
    commands:
      install: "pip install -r requirements.txt"
      test: "python -m pytest"
      lint: "flake8 ."
      build: "python setup.py build"
    docker_base: "python:3.11-slim"
```

#### Deployment Configuration (`config/deploy-config.yaml`)
Defines environments, deployment strategies, and infrastructure settings:

```yaml
environments:
  production:
    type: "kubernetes"
    namespace: "production"
    replicas: 5
    health_check:
      path: "/health"
      port: 8080

strategies:
  blue-green:
    health_check_interval: 30
    rollback_threshold: 0.05
    switch_traffic_delay: 60
```

## 🔧 Advanced Features

### Build Hooks

#### Pre-Build Hooks
Execute custom logic before builds:
```python
python hooks/pre-build.py '{"language": "python", "path": "."}'
```

#### Post-Build Hooks
Handle artifacts, deployments, and notifications after builds:
```python
python hooks/post-build.py '{"language": "python", "path": "."}' '{"status": "success"}'
```

### Observability Integration

The system integrates with multiple monitoring platforms:

#### Prometheus
- Build success/failure rates
- Build duration metrics
- Project-specific metrics
- Operation-level metrics

#### DataDog
- Build events and metrics
- Deployment tracking
- Custom dashboards

#### OpenTelemetry
- Distributed tracing
- Custom metrics
- Performance monitoring

### Security & Compliance

- **Vulnerability Scanning**: Trivy integration for container and filesystem scanning
- **SBOM Generation**: Automatic Software Bill of Materials creation with Syft
- **Secret Scanning**: GitLeaks integration for credential detection
- **License Compliance**: FOSSA integration for license scanning
- **Dependency Updates**: Dependabot and Renovate support

### Cloud Integrations

#### AWS
- ECR for container registry
- S3 for artifact storage
- EKS for Kubernetes deployments
- Secrets Manager for credential management

#### Google Cloud Platform
- GCR for container registry
- Cloud Storage for artifacts
- GKE for Kubernetes deployments

#### Microsoft Azure
- ACR for container registry
- Blob Storage for artifacts
- AKS for Kubernetes deployments

## 📊 Monitoring & Dashboards

### Grafana Dashboard
Pre-configured dashboard showing:
- Build success rates
- Build duration trends
- Language distribution
- Project health status

### DataDog Dashboard
Comprehensive monitoring with:
- Real-time build metrics
- Deployment tracking
- Performance insights
- Alert management

## 🔄 Deployment Strategies

### Blue-Green Deployment
- Deploy new version alongside current (green)
- Run health checks on new version
- Switch traffic atomically
- Keep old version for instant rollback

### Canary Deployment
- Gradually increase traffic to new version
- Monitor metrics at each stage
- Automatic rollback on issues
- Configurable traffic percentages

### Rolling Deployment
- Replace instances gradually
- Maintain service availability
- Built-in health checks
- Configurable update pace

## 🤖 LLM Integration (Future)

Planned AI-powered features:
- **Code Review**: Automated code quality analysis
- **Test Suggestions**: AI-generated test recommendations  
- **PR Labeling**: Intelligent pull request categorization
- **Natural Language CLI**: Chat-based build automation
- **Documentation Generation**: AI-powered docs and changelogs

## 🌐 Multi-Language Support

The system supports internationalization:
- Localized error messages
- Multi-language documentation
- Regional deployment configurations
- Cultural adaptation for different markets

## 🔧 Troubleshooting

### Common Issues

1. **Project Not Detected**
   - Check file patterns in `config/lang-config.yaml`
   - Ensure project files exist (package.json, requirements.txt, etc.)
   - Verify directory structure

2. **Build Failures**
   - Check language-specific dependencies
   - Review build logs in `build.log`
   - Verify command configurations

3. **Deployment Issues**
   - Check environment configurations
   - Verify credentials and permissions
   - Review deployment logs

### Debug Mode
Enable verbose logging:
```bash
export DEBUG=1
python scripts/universal-builder.py --detect-only
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

### Adding Language Support

1. Update `config/lang-config.yaml` with new language configuration
2. Add detection patterns and build commands
3. Test with sample projects
4. Update documentation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: [docs/](docs/)
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: support@example.com

## 🗺️ Roadmap

- [ ] LLM-powered code analysis
- [ ] Visual dashboard interface
- [ ] Mobile app for monitoring
- [ ] Marketplace for build plugins
- [ ] Multi-cloud deployment automation
- [ ] Advanced security scanning
- [ ] Performance optimization suggestions
- [ ] Integration with more CI/CD platforms