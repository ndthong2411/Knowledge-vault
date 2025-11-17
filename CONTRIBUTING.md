# Contributing to Knowledge Vault

Thank you for your interest in contributing to Knowledge Vault! This document provides guidelines and instructions for contributing.

## Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Knowledge-vault.git
   cd Knowledge-vault
   ```

3. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Guidelines

### Code Style

- Follow PEP 8 style guide
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Maximum line length: 127 characters

**Format your code**:
```bash
black src/ tests/ app.py config.py
```

**Check linting**:
```bash
flake8 src/ tests/ app.py config.py --max-line-length=127
```

### Testing

- Write tests for all new features
- Maintain test coverage above 80%
- Run tests before submitting PR

**Run tests**:
```bash
pytest tests/ -v
pytest --cov=src --cov-report=html
```

### Commit Messages

Use clear, descriptive commit messages:

```
feat: Add semantic search feature
fix: Resolve tag duplication issue
docs: Update README with installation steps
test: Add tests for storage module
refactor: Optimize database queries
```

## Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new features
3. **Ensure all tests pass**
4. **Update CHANGELOG.md** with your changes
5. **Submit PR** with clear description

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
- [ ] All tests pass
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings generated
```

## Questions?

Feel free to open an issue for discussion!
