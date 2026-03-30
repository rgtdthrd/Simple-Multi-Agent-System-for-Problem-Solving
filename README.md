# Product Strategy Generator

A simple multi-agent system that turns a raw product idea into a structured product strategy.

## Overview

This project demonstrates a clean multi-agent workflow with three specialized AI agents:

1. `Idea Analyst`
   Turns a rough idea into a crisp product brief.
2. `Market Strategist`
   Expands the brief into market, user, positioning, and go-to-market strategy.
3. `Strategy Writer`
   Converts all upstream outputs into a polished final product strategy document.

The agents do not work in parallel. Instead, they collaborate by passing text outputs from one stage to the next through a coordinator.

## Project Structure

```text
.
|-- config/
|   |-- config.py            # local only, ignored by git
|   `-- mock_config.py       # safe template for GitHub
|-- outputs/                 # generated pipeline outputs, ignored by git
|-- src/
|   `-- product_strategy_generator/
|       |-- agents/
|       |   |-- base_agent.py
|       |   |-- idea_analyst.py
|       |   |-- market_strategist.py
|       |   `-- strategy_writer.py
|       |-- coordinator.py
|       |-- llm.py
|       |-- main.py
|       `-- schemas.py
|-- LICENSE
|-- README.md
`-- requirements.txt
```

## Workflow

```text
User Idea
   |
   v
Idea Analyst
   |
   v
Market Strategist
   |
   v
Strategy Writer
   |
   v
Final Product Strategy
```

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Copy the example config:

```bash
copy config\\mock_config.py config\\config.py
```

3. Edit `config/config.py` and add your API key.

## Run

```bash
python -m src.product_strategy_generator.main --idea "An AI tool that helps small cafes plan seasonal menus based on customer trends."
```

## Output

Each run creates an output folder inside `outputs/` containing:

- `01_idea_brief.md`
- `02_market_strategy.md`
- `03_final_product_strategy.md`
- `pipeline_summary.json`


