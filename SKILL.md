---
name: portfolio-carbon-accounting-agent
description: What emissions are financed by the scoped holdings, how complete is the data, and why did the measured inventory change? Institutional buy-side research workflow with auditable evidence, calculations and human review; no autonomous trading.
license: MIT
metadata:
  author: HHFinAi
  version: "0.2.0"
---
# Portfolio Carbon Accounting and Attribution Agent

Use for carbon accounting under a specified investment mandate. Read `AGENTS.md`, then select a route from `agent.json`. Follow `WORKFLOW.md` and the CLI research loop. Copy the entire repository, not just this file: scripts, prompts, schemas and references are required.

A compatible filesystem-enabled agent host may discover this skill; activation has not been certified for specific products. Text-only use applies the methodology manually and does not enforce the Python controls.

Executable accounting is limited to long-only listed-company equity and corporate-debt EVIC inputs, not all PCAF asset classes. No short-netting, derivatives, sovereign GDP denominator, nature credits, or avoided-emissions offsets. Methodology changes and scope restatements require manual reconciliation.

Do not run a synthetic fixture as live research. Start with `examples/research-request-template.json`, replace every placeholder and register permitted evidence. Inspect `docs/INSTITUTIONAL_QUALITY.md` and `docs/AUDIT.md` before relying on outputs.
