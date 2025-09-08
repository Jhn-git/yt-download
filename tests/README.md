# Testing Documentation

This directory contains comprehensive tests for the yt-download project, designed to ensure code quality and reliability through the dependency injection architecture.

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── README.md               # This file
├── test_config.py          # ConfigService tests
├── test_logger.py          # LoggerService tests  
├── test_downloader.py      # DownloaderService tests
├── test_cli.py             # CLIService tests
├── test_integration.py     # End-to-end integration tests
└── fixtures/               # Test data and mock responses
    ├── __init__.py
    ├── sample_config.json   # Sample configuration for tests
    └── mock_responses.py    # Mock data for yt-dlp responses
```

## Running Tests

### Quick Start

```bash
# Run all tests
python tools/run_tests.py

# Run all tests with verbose output
python tools/run_tests.py -v

# Run specific test module
python tools/run_tests.py config
python tools/run_tests.py downloader
python tools/run_tests.py cli

# Stop on first failure
python tools/run_tests.py --failfast
```

### Using Python unittest directly

```bash
# Run all tests
python -m unittest discover tests/

# Run specific test file
python -m unittest tests.test_config

# Run with verbose output
python -m unittest discover tests/ -v

# Run specific test class
python -m unittest tests.test_config.TestConfigService

# Run specific test method
python -m unittest tests.test_config.TestConfigService.test_init_with_existing_config_file
```

### Test Runner Options

The included `tools/run_tests.py` script provides additional conveniences:

```bash
# List all available test modules
python tools/run_tests.py --list

# Check test environment
python tools/run_tests.py --check

# Quiet output (minimal)
python tools/run_tests.py -q

# Help
python tools/run_tests.py --help
```

## Test Categories

### Unit Tests

Each service has comprehensive unit tests that mock external dependencies:

- **ConfigService** (`test_config.py`): Configuration loading, validation, persistence
- **LoggerService** (`test_logger.py`): Logging setup, handlers, message formatting  
- **DownloaderService** (`test_downloader.py`): Subprocess mocking, download flows, command building
- **CLIService** (`test_cli.py`): Argument parsing, interactive mode, user input handling

### Integration Tests

Integration tests (`test_integration.py`) verify:
- Complete service dependency chain
- End-to-end download workflows
- Configuration propagation
- Error handling across services
- Real file operations with temporary files

## Test Architecture

### Dependency Injection Testing

Tests leverage the project's dependency injection architecture for easy mocking:

```python
# Example: Testing DownloaderService in isolation
mock_config = Mock()
mock_output = Mock(spec=OutputHandler)
downloader = DownloaderService(mock_config, mock_output)
```

### Protocol-Based Mocking

The `OutputHandler` protocol enables clean interface mocking:

```python
mock_output = Mock(spec=OutputHandler)
mock_output.info.assert_called_with("Expected message")
```

### External Dependency Mocking

Critical external dependencies are mocked:

```python
@patch('subprocess.Popen')  # Mock yt-dlp binary calls
@patch('builtins.input')    # Mock user input for interactive mode
@patch('os.makedirs')       # Mock file system operations
```

## Mock Data and Fixtures

### Test Fixtures (`fixtures/`)

- **`sample_config.json`**: Sample configuration for testing config loading
- **`mock_responses.py`**: Mock yt-dlp responses, progress output, and test data

### Common Mock Patterns

```python
# Mock successful download with progress output
mock_process = Mock()
mock_process.stdout = iter(MOCK_PROGRESS_OUTPUT)
mock_process.wait.return_value = 0

# Mock video info retrieval
mock_result.stdout = json.dumps(MOCK_VIDEO_INFO)
mock_result.returncode = 0
```

## Best Practices

### Test Organization

- Each service has its own test file mirroring the `core/` structure
- Test methods follow naming convention: `test_<method>_<scenario>`
- Test classes follow naming convention: `Test<ServiceName>`

### Mocking Guidelines

- Mock at the import level where dependencies are used
- Use `spec` parameter for protocol-based mocks
- Verify mock calls with `assert_called_with()` for critical operations
- Clean up mocks between tests using `setUp()` and `tearDown()`

### Error Testing

Every test suite includes error scenarios:
- Invalid input handling
- File system errors (permissions, missing files)
- Network/subprocess failures
- Edge cases (empty input, malformed data)

## Coverage Goals

Tests aim for comprehensive coverage of:

- ✅ **Happy path scenarios** - Normal operation flows
- ✅ **Error conditions** - Exception handling and edge cases  
- ✅ **Configuration variations** - Different config combinations
- ✅ **User interaction** - CLI arguments, interactive mode
- ✅ **External dependencies** - Subprocess calls, file operations
- ✅ **Service integration** - Cross-service communication

## Adding New Tests

When adding new features:

1. **Add unit tests** for individual service methods
2. **Mock external dependencies** appropriately
3. **Test error conditions** and edge cases
4. **Add integration tests** for cross-service features
5. **Update mock data** if needed in `fixtures/mock_responses.py`
6. **Run full test suite** to ensure no regressions

### Example Test Addition

```python
def test_new_feature_success(self):
    """Test new feature with successful operation."""
    # Setup
    self.mock_config.new_setting = "test_value"
    
    # Execute
    result = self.service.new_method("test_input")
    
    # Verify
    self.assertTrue(result)
    self.mock_output.info.assert_called_with("Expected message")

def test_new_feature_failure(self):
    """Test new feature error handling."""
    # Setup error condition
    self.mock_dependency.side_effect = Exception("Test error")
    
    # Execute and verify
    result = self.service.new_method("test_input")
    self.assertFalse(result)
    self.mock_output.error.assert_called_with("Error during operation: Test error")
```

## Continuous Integration

Tests are designed to run reliably in CI environments:
- No external network dependencies
- All file operations use temporary files
- Deterministic mock responses
- Clean setup/teardown between tests

## Troubleshooting

### Common Issues

**Import Errors**: Ensure you're running tests from the project root directory.

**Mock Failures**: Check that you're patching at the right level (where imported, not where defined).

**Flaky Tests**: Usually caused by shared state - ensure proper cleanup in `tearDown()`.

**Permission Errors**: Tests should use temporary files, not real system paths.

### Debug Mode

For debugging test failures:

```bash
# Run specific failing test with verbose output
python -m unittest tests.test_module.TestClass.test_method -v

# Add print statements or use pdb in test code
import pdb; pdb.set_trace()
```

This testing infrastructure provides a solid foundation for maintaining code quality and confidence in the yt-download project.