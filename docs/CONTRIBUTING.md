# Contributing to YT-Download

Thank you for your interest in contributing to YT-Download! This document provides guidelines for contributing to this project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Architecture Overview](#architecture-overview)
5. [Testing](#testing)
6. [Code Style](#code-style)
7. [Pull Request Process](#pull-request-process)
8. [Issue Reporting](#issue-reporting)

## Code of Conduct

This project follows a simple code of conduct: be respectful, constructive, and helpful to other contributors and users.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- ffmpeg installed on your system
- Git for version control

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
```bash
git clone https://github.com/YOUR_USERNAME/yt-download.git
cd yt-download
```

## Development Setup

### Environment Setup

1. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install development dependencies:
```bash
pip install -r requirements.txt
# Add development dependencies as needed
```

3. Make the script executable:
```bash
chmod +x ytdl.py
```

### Verify Setup

Test that everything works:
```bash
ytdl --help
```

## Architecture Overview

YT-Download uses dependency injection for clean, testable code:

### Core Components

- **ConfigService** (`src/ytdl/core/config.py`): Configuration management
- **DownloaderService** (`src/ytdl/core/downloader.py`): yt-dlp integration
- **CLIService** (`src/ytdl/core/cli.py`): Command-line interface
- **GUIService** (`src/ytdl/core/gui.py`): Graphical interface
- **LoggerService** (`src/ytdl/core/logger.py`): Logging functionality

### Design Principles

1. **Dependency Injection**: All services accept dependencies via constructor
2. **Protocol-based Interfaces**: Use Python protocols for type safety
3. **Single Responsibility**: Each service has one clear purpose
4. **Testability**: Easy to mock and test individual components

### Adding New Features

When adding features:

1. **Follow the existing pattern**: Use dependency injection
2. **Create interfaces**: Use protocols for new abstractions
3. **Maintain separation**: Don't mix concerns between services
4. **Add configuration**: Use ConfigService for new settings

## Testing

### Test Structure

```
tests/
├── unit/
│   ├── test_config.py
│   ├── test_downloader.py
│   ├── test_cli.py
│   └── test_logger.py
├── integration/
│   └── test_full_workflow.py
└── fixtures/
    └── test_config.json
```

### Writing Tests

Example test pattern:
```python
import unittest
from unittest.mock import Mock
from ytdl.core.downloader import DownloaderService

class TestDownloaderService(unittest.TestCase):
    def setUp(self):
        self.mock_config = Mock()
        self.mock_output = Mock()
        self.service = DownloaderService(self.mock_config, self.mock_output)
    
    def test_download_success(self):
        # Test implementation
        pass
```

### Running Tests

```bash
# Run all tests
python tools/run_tests.py

# Run specific test module
python tools/run_tests.py config

# Run with verbose output
python tools/run_tests.py -v
```

## Code Style

### Python Style Guidelines

- Follow PEP 8
- Use type hints
- Write descriptive variable names
- Keep functions focused and small

### Example Style

```python
from typing import Optional, Protocol

class OutputHandler(Protocol):
    def info(self, message: str) -> None: ...
    def error(self, message: str) -> None: ...

class MyService:
    def __init__(self, config: ConfigService, output: OutputHandler):
        self.config = config
        self.output = output
    
    def process_url(self, url: str, quality: Optional[str] = None) -> bool:
        """Process a video URL with optional quality setting."""
        try:
            # Implementation here
            return True
        except Exception as e:
            self.output.error(f"Failed to process URL: {e}")
            return False
```

### Documentation

- Add docstrings to public methods
- Use type hints consistently
- Comment complex logic
- Update README.md and USAGE.md for new features

## Pull Request Process

### Before Submitting

1. **Test your changes**: Ensure all tests pass
2. **Update documentation**: Modify relevant docs
3. **Check code style**: Follow the project conventions
4. **Verify functionality**: Test with real URLs

### PR Guidelines

1. **Clear title**: Describe what the PR does
2. **Detailed description**: Explain the changes and why
3. **Link issues**: Reference related issue numbers
4. **Small, focused changes**: Easier to review

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass
```

## Issue Reporting

### Bug Reports

Use this template:

```markdown
## Bug Description
Clear description of the bug

## To Reproduce
Steps to reproduce:
1. Run command '...'
2. See error

## Expected Behavior
What should happen

## Environment
- OS: [e.g., Ubuntu 20.04]
- Python version: [e.g., 3.9.2]
- yt-dlp version: [check with ./yt-dlp_linux --version]

## Additional Context
Any other relevant information
```

### Feature Requests

```markdown
## Feature Description
Clear description of the proposed feature

## Use Case
Why is this feature needed?

## Proposed Solution
How should this work?

## Alternatives Considered
Other approaches you've thought about
```

## Development Workflow

### Typical Workflow

1. **Create branch**: `git checkout -b feature/your-feature`
2. **Make changes**: Implement your feature
3. **Add tests**: Write comprehensive tests
4. **Test locally**: Ensure everything works
5. **Update docs**: Modify documentation
6. **Commit changes**: Use clear commit messages
7. **Push branch**: `git push origin feature/your-feature`
8. **Create PR**: Submit pull request

### Commit Messages

Use clear, descriptive commit messages:

```
Add audio-only download option

- Implement --audio-only flag in CLI
- Update DownloaderService to handle audio extraction
- Add tests for audio download functionality
- Update documentation with new option
```

## Questions?

If you have questions about contributing:

1. Check existing issues and discussions
2. Open an issue for clarification
3. Reach out to maintainers

Thank you for contributing to YT-Download!