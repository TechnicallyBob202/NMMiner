# Contributing to NMMiner Integration

Thank you for your interest in contributing to the NMMiner Home Assistant integration!

## Development Setup

1. Fork the repository
2. Clone your fork locally
3. Create a new branch for your feature/fix
4. Make your changes
5. Test thoroughly
6. Submit a pull request

## Testing Locally

### Manual Testing

1. Copy `custom_components/nmminer` to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant
3. Add the integration via UI
4. Verify all sensors work correctly
5. Test block hit notifications
6. Check logs for errors

### Automated Testing

Run validation locally:

```bash
# HACS validation
docker run --rm -v $(pwd):/github/workspace ghcr.io/hacs/action:latest

# Hassfest validation
docker run --rm -v $(pwd):/github/workspace ghcr.io/home-assistant/hassfest:latest
```

## Code Style

This project follows Home Assistant's code style:

- Use `ruff` for linting
- Follow async/await patterns
- Use type hints
- Add docstrings to all functions
- Keep lines under 88 characters (ruff default)

Run linting:
```bash
pip install ruff
ruff check custom_components/nmminer/
```

## Pull Request Guidelines

- **Title**: Clear, descriptive title
- **Description**: Explain what changes you made and why
- **Testing**: Describe how you tested the changes
- **Breaking Changes**: Note if this breaks existing setups
- **Documentation**: Update README if needed

## Feature Requests

Have an idea? Open an issue with:
- Clear description of the feature
- Use case / why it's needed
- How it might work

## Bug Reports

Found a bug? Open an issue with:
- Home Assistant version
- Integration version
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs

## Code of Conduct

- Be respectful and constructive
- Help others learn
- Focus on the technical merit of ideas
- Keep discussions on-topic

## Questions?

- Open a discussion issue
- Join the NMMiner Telegram: https://t.me/NMMiner
- Check existing issues/PRs first

Thank you for contributing! 🎉
