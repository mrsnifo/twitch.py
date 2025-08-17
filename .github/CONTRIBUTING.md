# Contributing to twitch.py

Hey there! Thanks for wanting to help make twitch.py better. Whether you're fixing a bug, adding a feature, or just improving documentation, we appreciate it.

## Before You Start

Quick heads up - check out our [Community Guidelines](CODE_OF_CONDUCT.md) first. Nothing fancy, just the basics of not being a jerk to each other.

## Getting Your Code In

### The Process

1. **Fork it** - Grab your own copy of the repo
2. **Clone it locally**
   ```bash
   git clone https://github.com/mrsnifo/twitch.py.git
   ```
3. **Make a branch** - Give it a name that makes sense
   ```bash
   git checkout -b fix/eventsub-reconnection
   # or
   git checkout -b add/user-subscriptions
   ```
4. **Write your code** - Make it good, test it, don't break existing stuff
5. **Commit with a decent message**
   ```bash
   git commit -m "Fix EventSub reconnection timeout handling"
   ```
6. **Push it up**
   ```bash
   git push origin your-branch-name
   ```
7. **Open a PR** - Tell us what you did and why

### What Makes a Good PR

- **Clear description** - What problem does this solve? How does it work?
- **Tests included** - If you're adding features, add tests
- **Documentation updated** - If you change how something works, update the docs
- **No breaking changes** - Unless absolutely necessary (and you tell us why)

## Found a Bug or Have an Idea?

Check the [issues](https://github.com/mrsnifo/twitch.py/issues) first - someone might've already reported it. If not, open a new one with:
- What you expected to happen
- What actually happened  
- Code to reproduce the issue (if applicable)
- Your Python version and any relevant environment details

## Code Style

We're not super strict, but try to:
- Follow existing patterns in the codebase
- Use meaningful variable names
- Add docstrings for public methods
- Keep functions reasonably sized
- Use type hints where it makes sense

## Review Process

I'll try to review PRs within a reasonable time. Might ask for changes or have questions - it's not personal, just want to keep things solid.

Small fixes usually get merged quickly. Bigger features might need more discussion.

## License

By contributing, you're cool with your code being under the MIT License (same as the rest of the project).

## Questions?

Not sure about something? Just ask! Open an issue, send me an email at snifo@mail.com, or start a discussion.

Thanks for helping make twitch.py awesome!