# Praxis OS Dashboard - Universal Code Builder Platform

[![Universal Build Matrix](https://github.com/CoastalGuardFencing/Praxis-os-dashboard/actions/workflows/universal-build.yml/badge.svg)](https://github.com/CoastalGuardFencing/Praxis-os-dashboard/actions/workflows/universal-build.yml)

A comprehensive universal code builder and automation platform that detects, builds, tests, and deploys projects across 20+ programming languages and frameworks.

## 🚀 Quick Start

```bash
# Detect all projects in current directory
python scripts/universal-builder.py --detect-only

# Run interactive CLI wizard
python scripts/cli-wizard.py

# Build all detected projects
python scripts/universal-builder.py

# Deploy with blue-green strategy
python automation/deploy.py --environment staging --strategy blue-green --image myapp:latest
```

## ✨ Features

- 🔍 **Universal Project Detection** - Automatically detects projects in 20+ languages
- 🏗️ **Parallel Build System** - Efficient concurrent builds across multiple projects  
- 🎯 **Interactive CLI Wizard** - User-friendly command-line interface
- 🚀 **Multi-Strategy Deployment** - Blue/green, canary, and rolling deployments
- 📊 **Observability Integration** - Prometheus, DataDog, OpenTelemetry support
- 🔄 **Self-Updating System** - Automatic updates from repository
- 🛡️ **Security & Compliance** - SBOM generation, vulnerability scanning, license checks
- ☁️ **Cloud Native** - AWS, GCP, Azure integrations with Kubernetes support

## 🛠️ Supported Languages

| Language | Framework Support | Build Tools | Package Managers |
|----------|------------------|-------------|------------------|
| JavaScript/TypeScript | React, Vue, Angular, Node.js | npm, yarn, webpack | npm, yarn |
| Python | Django, Flask, FastAPI | setuptools, poetry, pip | pip, poetry, pipenv |
| Go | Standard library, Gin, Echo | go build, go mod | go modules |
| Rust | Actix, Rocket, Tokio | cargo | crates.io |
| Java | Spring, Maven, Gradle | javac, maven, gradle | maven, gradle |
| C#/.NET | ASP.NET, Entity Framework | dotnet, msbuild | nuget |
| Ruby | Rails, Sinatra | bundler, rake | rubygems |
| PHP | Laravel, Symfony | composer | packagist |
| Swift | iOS, macOS, Vapor | xcodebuild, swift pm | swift pm |
| Kotlin | Spring, Ktor | kotlinc, gradle, maven | maven, gradle |

*And 10+ more languages including C/C++, Scala, Dart, Elixir, Haskell, Julia, Clojure, R, Perl, Shell*

## 📁 Architecture

```
├── 🎛️ config/           # Centralized configurations
│   ├── lang-config.yaml    # Language build definitions
│   └── deploy-config.yaml  # Deployment strategies
├── 🤖 scripts/          # Core automation scripts  
│   ├── universal-builder.py # Main build orchestrator
│   ├── cli-wizard.py       # Interactive CLI
│   └── self-update.py      # Auto-update system
├── 🔗 hooks/            # Build lifecycle hooks
│   ├── pre-build.py        # Pre-build automation
│   └── post-build.py       # Post-build processing
├── 🚀 automation/       # Deployment & observability
│   ├── deploy.py           # Multi-strategy deployment
│   └── observability.py    # Monitoring integration
└── 🔧 .github/workflows/ # CI/CD pipelines
    └── universal-build.yml # GitHub Actions workflow
```

## 🎯 Use Cases

### For Development Teams
- **Monorepo Management**: Build multiple projects with different languages
- **CI/CD Standardization**: Consistent build processes across all projects  
- **Developer Onboarding**: Automated setup and build for new team members
- **Code Quality**: Integrated linting, testing, and security scanning

### For DevOps Engineers  
- **Infrastructure as Code**: Version-controlled deployment configurations
- **Multi-Environment Deployments**: Staging, production with different strategies
- **Monitoring & Observability**: Built-in metrics and tracing
- **Compliance & Security**: Automated vulnerability and license scanning

### For Platform Teams
- **Self-Service Deployments**: Developers can deploy independently
- **Standardized Tooling**: Consistent build and deploy patterns
- **Cost Optimization**: Efficient resource usage with parallel builds
- **Audit & Compliance**: Complete build and deployment history

## 🔧 Installation

### Prerequisites
- Python 3.9+
- Git
- Docker (for container builds)
- kubectl (for Kubernetes deployments)

### Setup
```bash
git clone https://github.com/CoastalGuardFencing/Praxis-os-dashboard.git
cd Praxis-os-dashboard
pip install pyyaml requests boto3
chmod +x scripts/*.py hooks/*.py automation/*.py
```

## 📊 Example Build Results

```json
{
  "build_id": "build-1703123456",
  "timestamp": "2024-01-01T12:00:00Z",
  "summary": {
    "total_projects": 5,
    "successful_projects": 4,
    "failed_projects": 1,
    "success_rate": 0.8,
    "total_duration": 125.4,
    "language_stats": {
      "javascript": {"total": 2, "success": 2},
      "python": {"total": 2, "success": 1}, 
      "go": {"total": 1, "success": 1}
    }
  }
}
```

## 🚀 Deployment Strategies

### Blue-Green Deployment
```bash
python automation/deploy.py \
  --environment production \
  --strategy blue-green \
  --image myapp:v2.0.0
```

### Canary Deployment  
```bash
python automation/deploy.py \
  --environment production \
  --strategy canary \
  --image myapp:v2.0.0
```

### Rolling Update
```bash
python automation/deploy.py \
  --environment production \
  --strategy rolling \
  --image myapp:v2.0.0
```

## 📈 Monitoring & Observability

### Prometheus Integration
- Build success/failure rates
- Build duration metrics
- Resource utilization
- Custom business metrics

### DataDog Integration  
- Real-time dashboards
- Alert management
- Event correlation
- Performance monitoring

### OpenTelemetry Integration
- Distributed tracing
- Custom spans and metrics
- Service topology mapping
- Performance profiling

## 🛡️ Security & Compliance

### Automated Security Scanning
- **Container Scanning**: Trivy integration for vulnerability detection
- **Secret Scanning**: GitLeaks for credential leak prevention  
- **License Compliance**: FOSSA for open source license management
- **SBOM Generation**: Syft for Software Bill of Materials

### Compliance Features
- Audit logging for all builds and deployments
- Role-based access control integration
- Compliance reporting and attestation
- Regulatory framework support (SOC2, PCI-DSS, HIPAA)

## 🌐 Cloud Integrations

| Provider | Container Registry | Artifact Storage | Kubernetes | Secrets |
|----------|-------------------|------------------|------------|---------|
| **AWS** | ECR | S3 | EKS | Secrets Manager |
| **GCP** | GCR/Artifact Registry | Cloud Storage | GKE | Secret Manager |
| **Azure** | ACR | Blob Storage | AKS | Key Vault |

## 🔄 Self-Updating System

The platform can automatically update itself:

```bash
# Check for updates
python scripts/self-update.py --check

# Update to latest version
python scripts/self-update.py --update

# Rollback if needed
python scripts/self-update.py --rollback
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for details.

### Development Setup
```bash
git clone https://github.com/CoastalGuardFencing/Praxis-os-dashboard.git
cd Praxis-os-dashboard
pip install -e .
pytest tests/
```

### Adding Language Support
1. Update `config/lang-config.yaml` with language configuration
2. Add tests in `tests/languages/`
3. Update documentation
4. Submit pull request

## 📄 Documentation

- **[Full Documentation](docs/README.md)** - Complete guide and API reference
- **[Configuration Guide](docs/configuration.md)** - Detailed configuration options
- **[Deployment Guide](docs/deployment.md)** - Deployment strategies and best practices
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions

## 🗺️ Roadmap

### Short Term (Q1 2024)
- [ ] LLM-powered code review integration
- [ ] Visual web dashboard
- [ ] Enhanced security scanning
- [ ] Performance optimization

### Medium Term (Q2-Q3 2024)  
- [ ] Multi-cloud deployment automation
- [ ] Advanced analytics and insights
- [ ] Plugin marketplace
- [ ] Mobile monitoring app

### Long Term (Q4 2024+)
- [ ] AI-powered build optimization
- [ ] Advanced compliance frameworks
- [ ] Edge deployment capabilities
- [ ] Enterprise features

## 📞 Support

- **📚 Documentation**: [docs/](docs/)
- **🐛 Bug Reports**: [GitHub Issues](https://github.com/CoastalGuardFencing/Praxis-os-dashboard/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/CoastalGuardFencing/Praxis-os-dashboard/discussions)
- **📧 Email**: support@coastalguardfencing.com

## 📊 Project Stats

![Languages](https://img.shields.io/github/languages/count/CoastalGuardFencing/Praxis-os-dashboard)
![Top Language](https://img.shields.io/github/languages/top/CoastalGuardFencing/Praxis-os-dashboard)
![Code Size](https://img.shields.io/github/languages/code-size/CoastalGuardFencing/Praxis-os-dashboard)
![Last Commit](https://img.shields.io/github/last-commit/CoastalGuardFencing/Praxis-os-dashboard)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <strong>Built with ❤️ by the Coastal Guard Fencing Team</strong>
  <br>
  <em>Simplifying build automation across all languages and platforms</em>
</div>