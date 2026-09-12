# Contributing to Tech Interview Master

Thanks for wanting to contribute! This repo is community-driven and we welcome improvements.

## How to Contribute

### 1. Fix or Improve Existing Content
- Fix typos, broken links, or incorrect complexity analysis
- Improve explanations or add better examples
- Update salary data or company-specific info

### 2. Add New Content
- New DSA pattern files (follow `skeleton.md` template, `snake_case.py` naming)
- New algorithm implementations (follow existing code style)
- New system design documents (follow existing format)
- New company-specific behavioral guides

### 3. Report Issues
- Open a GitHub issue for bugs, outdated info, or suggestions

## Guidelines

### Code Style (Python files)
- Follow [PEP 8](https://peps.python.org/pep-0008/): `snake_case` for variables and functions
- `PascalCase` for classes
- Add type hints where practical (e.g. `def dijkstra(graph: dict, src: int) -> list[float]:`)
- Add an `if __name__ == "__main__":` block at the bottom with worked examples for manual testing
- Prefer the standard library (`heapq`, `collections`, `functools`) over custom implementations, except where the data structure itself is the teaching point
- Follow the `skeleton.md` template for pattern files

### Markdown Style
- Use emoji headers (consistent with existing docs)
- Include complexity tables (Time / Space) for algorithms
- Cross-link related files using relative paths

### Pull Request Process
1. Fork the repo
2. Create a branch (`git checkout -b add-fenwick-tree`)
3. Make your changes
4. Test any Python files with `python <filename>`
5. Submit a PR with a clear description of what you changed and why

### What We're Looking For
- Accuracy over quantity
- Interview-focused content (not textbook theory)
- Code that actually runs
- Clear explanations a 3 YOE engineer would understand

## What NOT to Submit
- AI-generated content dumps without review
- Copyrighted material from paid courses
- Solutions to active contest problems
- Content unrelated to tech interviews

## Questions?
Open an issue and we'll help you get started.
