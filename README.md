# Kata with RDF Twist

This repository contains the Gilded Rose Refactoring Kata exercise with a unique twist.

Based on: https://github.com/emilybache/GildedRose-Refactoring-Kata

## Prerequisites

Before you begin, ensure you have the following installed:

### Windows Users
1. **WSL (Windows Subsystem for Linux)**
   - Follow the official guide: https://docs.microsoft.com/en-us/windows/wsl/install
   - Recommended: Ubuntu 22.04 LTS or later
   - Open PowerShell as Administrator and run:
     ```powershell
     wsl --install
     ```

### All Users (Linux/macOS/WSL)

2. **Git**
   - Ubuntu/Debian:
     ```bash
     sudo apt-get update && sudo apt-get install git
     ```
   - macOS:
     ```bash
     xcode-select --install
     ```
   - Verify installation:
     ```bash
     git --version
     ```

3. **Make**
   - Ubuntu/Debian:
     ```bash
     sudo apt-get update && sudo apt-get install build-essential
     ```
   - macOS: (if you installed this for git above, skip this step)
     ```bash
     xcode-select --install
     ```
   - Verify installation:
     ```bash
     make --version
     ```

4. **uv (Python package installer)**
   - Install via the official installer:
     ```bash
     curl -LsSf https://astral.sh/uv/install.sh | sh
     ```
   - Or via pip:
     ```bash
     pip install uv
     ```
   - Verify installation:
     ```bash
     uv --version
     ```

5. **VSCode (Recommended IDE)**
   - Download and install from: https://code.visualstudio.com/
   - Follow the installer for your operating system
   - Once installed, you can open VSCode in any directory with:
     ```bash
     code .
     ```

## Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/ESaive/kata-with-rdf-twist.git
   cd kata-with-rdf-twist
   ```

2. **Set up the virtual environment**
   ```bash
   make
   ```
   This will create a Python virtual environment and install all required dependencies.

3. **Activate the virtual environment** (optional, but recommended)
   ```bash
   source .venv/bin/activate
   ```

## The Exercise

Read the requirements in [GildedRoseRequirements.md](GildedRoseRequirements.md) for the full specification of the Gilded Rose kata.

### The Twist: RDF Data Processing

**All processing and storage of data must be handled as RDF (Resource Description Framework).**

This means:
- Item data should be represented as RDF triples
- Quality updates and business logic should operate on RDF graphs
- Storage and retrieval of inventory must use RDF formats (e.g., Turtle, RDF/XML, JSON-LD)
- You may use RDF libraries and SPARQL queries as needed

### Your Tasks

1. **Refactor the existing code** in `python/gilded_rose.py` to improve its maintainability
2. **Implement RDF-based data handling** for all item processing and storage
3. **Add the new "Conjured" items feature** as specified in the requirements
4. **Ensure all tests pass** - both unit tests and approval tests
5. **Do not modify the `Item` class** (as per the original kata rules)

### Provided Scaffolding

To help you get started with RDF, we've provided some initial scaffolding:

- **`python/schema.ttl`**: An RDF schema (ontology) defining the Gilded Rose domain model
  - Defines classes: `Item`, `ItemType`
  - Defines properties: `name`, `sellIn`, `quality`, `itemType`
  - Includes example item types: `NormalItem`, `AgedBrie`, `Sulfuras`, `BackstagePass`
  - You may need to extend this for Conjured items and business rules

- **`python/rdf_store.py`**: A skeleton RDF store implementation
  - `RDFItemStore` class with TODO methods to implement
  - `item_to_rdf()`: Convert Item objects to RDF triples
  - `rdf_to_item()`: Sync RDF data back to Item objects
  - `update_quality()`: Implement business logic using RDF/SPARQL
  - Helper methods for item type determination

- **`rdflib` dependency**: Already included in `pyproject.toml`

**Your job is to complete the TODO sections** and integrate the RDF store with the existing `GildedRose` class.

### Approach Suggestions

You can choose different strategies:

1. **Wrapper Approach**: Keep `gilded_rose.py` mostly intact, use `RDFItemStore` as a backend
2. **Full Integration**: Refactor `GildedRose.update_quality()` to use RDF operations directly
3. **SPARQL-Heavy**: Implement all business logic as SPARQL UPDATE queries
4. **Hybrid**: Use Python for logic, RDF for storage and querying

There's no single "correct" approach - we're interested in your design decisions and reasoning.

## Using AI Technologies & Coding Assistants

**We encourage the use of AI technologies and coding assistants!** Tools like GitHub Copilot, ChatGPT, Claude, Cody, and similar assistants are part of today's and tomorrow's development world.

However, we value **transparency and learning** within our team. Therefore:

- **Please provide the dialogue/conversation history** with any AI assistant you use during this exercise
- Share your prompts and the AI's responses (you can include them as a separate file or document)
- This helps us understand your problem-solving approach and learn from each other
- We're interested in how you collaborate with AI tools to improve our collective way of working

This is not about evaluation - it's about fostering a culture of openness where we can all learn and improve together.

## Running Tests

```bash
make test
```

This will run all tests in `python/tests/`:
- `test_gilded_rose.py`: Unit tests (currently has a failing placeholder test)
- `test_gilded_rose_approvals.py`: Approval tests that verify behavior over 30 days

The approval test is particularly important - it captures the expected output and will help ensure your refactoring doesn't break existing behavior.

## Linting

```bash
make lint
```

Configure your preferred linting tools. The project supports multiple linters with PEP8 standards and 120 character line length. See `pyproject.toml` for available configurations:
- `black` - Code formatter
- `ruff` - Fast Python linter
- `isort` - Import sorter
- `pylint` - Code analysis
- `flake8` - Style guide enforcement
- `autopep8` - Auto-formatter

## Brownie Points: CI/CD & Development Best Practices

While not required, we'd love to see you demonstrate clean and efficient development practices! Here are some areas where you can earn extra recognition:

### Automated Quality Checks
- **Pre-commit hooks**: Set up automated linting/formatting before commits
- **Git hooks**: Prevent commits that break tests
- **Code coverage**: Track and report test coverage metrics
- **Type checking**: Add type hints and use `mypy` or similar tools

### CI/CD Pipeline
- **GitLab CI/CD**: Create a `.gitlab-ci.yml` that runs tests and linting
- **GitHub Actions**: Alternative CI configuration
- **Automated testing**: Run tests on every push/merge request
- **Quality gates**: Enforce minimum coverage, no linting errors, etc.

### Development Workflow
- **Make targets**: Add helpful targets to the Makefile for common tasks (format, coverage, clean, etc.)
- **Documentation**: Clear docstrings, type hints, README updates
- **Clean commits**: Meaningful commit messages, logical commit structure
- **Branch strategy**: Feature branches, clean merge history

**These are suggestions, not requirements!** We value quality over quantity. A well-implemented solution with one or two thoughtful CI/CD practices is better than a rushed implementation with many half-baked features.

Show us how you'd set up a project for efficient, collaborative development!

## Project Structure

```
.
├── python/
│   ├── gilded_rose.py              # Main implementation (to be refactored)
│   ├── rdf_store.py                # RDF store skeleton (TODO: implement)
│   ├── schema.ttl                  # RDF schema/ontology
│   ├── texttest_fixture.py         # Test fixture for approval tests
│   └── tests/
│       ├── test_gilded_rose.py     # Unit tests
│       └── test_gilded_rose_approvals.py  # Approval tests
├── GildedRoseRequirements.md       # Full requirements specification
├── pyproject.toml                  # Python dependencies and tool configuration
├── Makefile                        # Build and test automation
└── README.md                       # This file
```

## Tips

- Start by understanding the existing code and running the tests
- Review the provided `schema.ttl` to understand the RDF domain model
- Implement the `RDFItemStore` methods one at a time, testing as you go
- Consider using SPARQL queries for complex updates
- The approval tests will help ensure your refactoring doesn't break existing behavior
- You can serialize the RDF graph to files (Turtle, JSON-LD) for debugging
- Use `rdflib` documentation: https://rdflib.readthedocs.io/

## RDF Resources

If you're new to RDF:
- **RDF Primer**: https://www.w3.org/TR/rdf11-primer/
- **SPARQL Tutorial**: https://www.w3.org/TR/sparql11-query/
- **rdflib Documentation**: https://rdflib.readthedocs.io/
- **Turtle Format**: https://www.w3.org/TR/turtle/

## Questions?

If you have any questions about the exercise or setup, please reach out to repository owner.

Good luck! 🚀
