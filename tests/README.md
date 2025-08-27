# 🧪 Test Suite - Biomedical Text Agent

This directory contains the complete test suite for the Biomedical Text Agent, organized by test type and scope.

## 📁 Directory Structure

```
tests/
├── unit/           # Individual component tests
├── integration/    # Component interaction tests
├── e2e/           # End-to-end system tests
├── conftest.py    # Pytest configuration and fixtures
├── run_tests.py   # Test runner script
└── README.md      # This file
```

## 🎯 Test Categories

### **Unit Tests** (`unit/`)
- **Purpose**: Test individual components in isolation
- **Scope**: Single functions, classes, or modules
- **Speed**: Fast execution
- **Examples**: 
  - Database operations
  - API endpoint logic
  - Utility functions

### **Integration Tests** (`integration/`)
- **Purpose**: Test component interactions
- **Scope**: Multiple components working together
- **Speed**: Medium execution
- **Examples**:
  - API router integration
  - Database + API integration
  - Service orchestration

### **End-to-End Tests** (`e2e/`)
- **Purpose**: Test complete system workflows
- **Scope**: Full system from frontend to backend
- **Speed**: Slow execution
- **Examples**:
  - Complete document processing pipeline
  - User workflows
  - System startup and shutdown

## 🚀 Running Tests

### **Option 1: Run All Tests**
```bash
# From project root
python tests/run_tests.py
```

### **Option 2: Run Specific Test Categories**
```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# E2E tests only
pytest tests/e2e/ -v
```

### **Option 3: Run Individual Test Files**
```bash
# Specific test file
pytest tests/unit/test_enhanced_orchestrator.py -v

# With coverage
pytest tests/unit/test_enhanced_orchestrator.py --cov=src --cov-report=html
```

## ⚙️ Test Configuration

### **Pytest Configuration** (`conftest.py`)
- **Python Path**: Automatically adds `src/` to Python path
- **Fixtures**: Common test data and resources
- **Test Data**: Sample PDFs, test databases, etc.

### **Environment Variables**
Tests use the same environment configuration as the main application:
- `.env` file for local development
- `.env.example` for reference

## 📊 Test Reports

### **Coverage Reports**
```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# Generate XML coverage report (for CI/CD)
pytest --cov=src --cov-report=xml
```

### **Test Results**
- **Console Output**: Real-time test progress
- **JUnit XML**: For CI/CD integration
- **HTML Reports**: Detailed coverage and results

## 🔧 Writing New Tests

### **Test File Naming**
- **Unit Tests**: `test_<component_name>.py`
- **Integration Tests**: `test_<feature>_integration.py`
- **E2E Tests**: `test_<workflow>_e2e.py`

### **Test Function Naming**
```python
def test_function_name_should_do_something():
    """Test description."""
    # Arrange
    # Act
    # Assert
```

### **Using Fixtures**
```python
def test_with_fixture(sample_pdf_path, test_db_path):
    """Test using common fixtures."""
    assert sample_pdf_path.exists()
    assert test_db_path.parent.exists()
```

## 🚨 Troubleshooting

### **Common Issues**
1. **Import Errors**: Ensure `src/` is in Python path
2. **Database Issues**: Tests use separate test database
3. **File Paths**: Use relative paths from test file location

### **Debug Mode**
```bash
# Run with debug output
pytest -v -s --tb=long

# Run single test with debug
pytest tests/unit/test_file.py::test_function -v -s
```

## 📈 Continuous Integration

Tests are automatically run in CI/CD pipelines:
- **Pre-commit**: Unit tests
- **Pull Request**: All tests
- **Deployment**: Full test suite + coverage

## 🤝 Contributing

When adding new tests:
1. **Follow naming conventions**
2. **Use appropriate test category**
3. **Add fixtures if needed**
4. **Update this README if adding new test types**
5. **Ensure tests pass before committing**

---

**Happy Testing! 🧪✨**
