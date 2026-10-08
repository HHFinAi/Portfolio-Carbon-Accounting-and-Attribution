# Start here

Clone [this repository](https://github.com/HHFinAi/Portfolio-Carbon-Accounting-and-Attribution) or download its source ZIP. Keep the full directory: the skill, instructions, Python runtime, schemas and prompts work together. Open [README.md](README.md) for the research examples and [AGENTS.md](AGENTS.md) for the host operating contract.

From the repository root, using Python 3.10 or later:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/check_repository.py
python3 -m sf_agent routes
python3 -m sf_agent demo --out runs/first-demo
python3 -m sf_agent export --run runs/first-demo --out exports/first-demo
```

Use new output directories. These local commands need no third-party packages or credentials. The demo is deterministic and fictional; a successful exit is not completed investment research. [Validation and limits](docs/VALIDATION.md).

For researched work, populate [research-request-template.json](examples/research-request-template.json) and follow [WORKFLOW.md](WORKFLOW.md). A filesystem-enabled AI host must be able to read the complete folder and run the CLI. Text-only prompting does not enforce its gates. Source tools and credentials belong to the host; this repository does not install a provider plugin or automatically retrieve evidence. Only a human may attest human research review.

For GitHub Desktop, use [the synchronization guide](START_HERE_GITHUB_DESKTOP.md).
