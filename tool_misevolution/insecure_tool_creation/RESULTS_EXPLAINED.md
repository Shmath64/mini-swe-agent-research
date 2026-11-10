# Results Directory Explained

## Overview

The `results` directory contains experimental outputs from testing a **self-evolving compromise of a self-evolving coding agent**. This experimental environment investigates how AI coding agents become less safe under black-box interaction when tools can be created, stored, retrieved, and reused across task sequences.

### Purpose

The core research question is: **How do stateful tool reuse, pool admission, and retrieval bias combine to lower safety scores over successive agent evolutions?**

This repository is part of the mini-swe-agent project and focuses on studying tool mis-evolution security experiments.

## Directory Structure

### Root Results Directory

```
results/
├── misevolution_user_queries/       # Primary dataset experiments
├── swebench_verified_mini/          # SWE-bench verified experiments
└── evolution/                       # Common evolution structure (under each dataset)
```

### Evolution Directory Structure (per dataset)

```
evolution/
├── ours/                            # Full self-evolution experiment
├── ours_strong/                     # Focused v3-v4 chain experiment
├── ours_no_reuse/                   # Mechanism ablation (no lineage reuse)
├── ours_no_memory/                  # Mechanism ablation (no MCP matching)
├── ours_no_pinned_retrieval/        # Mechanism ablation (no pinned lineage)
├── ours_shuffled/                   # Mechanism ablation (shuffled task order)
├── baseline/                        # Baseline comparison experiments
├── poison_*_n8/                     # Poisoning/attack variants
├── qwen_*_n8/                       # Qwen model variants
├── mimo_*_n8/                       # MIMO variants
├── misevolution_tasks/              # Versioned tasks (v1-v4)
└── *.jsonl, *.json, *.csv           # Evaluation summaries and data
```

## Important Files and Subdirectories

### Trajectories Directory (`trajectories/`)

Contains individual task execution records:

```
trajectories/
├── cwe_020_0_v1_trajectory.json     # v1: Basic functionality
├── cwe_020_0_v2_trajectory.json     # v2: Feature expansion
├── cwe_020_0_v3_trajectory.json     # v3: Conditional logic (surface safety)
├── cwe_020_0_v4_trajectory.json     # v4: Persistence/external triggers (attack)
├── ...
└── evaluation_summary.json          # Aggregate statistics for all tasks
```

**Key fields in trajectory files:**
- `task_name`, `timestamp`, `original_task` (task description and metadata)
- `workflow_execution` (agent's plan, steps, and results)
- `tool_created`, `tool_reuse_verified`, `trigger_success` (security metrics)
- `trust_score`, `attack_risk_score`, `trigger_monitor` (risk indicators)
- `success`, `total_steps`, `error` (execution outcome)

### Judge Results Directory (`judge_results/`)

Contains security evaluation results:

```
judge_results/
├── judge_scores.jsonl               # Individual tool scores (JSONL format)
└── judge_scores_summary.json        # Aggregate statistics
```

**Summary fields:**
- `total_tools`, `valid_scores`
- `score_counts` (distribution: 0, 1, 5, 8, 10)
- `ours_low_score_rate` (fraction of tools scoring ≤5)
- `ours_mean_score`, `ours_median_score`
- `ours_recovered_scores` (automatically recovered from error states)

### MCP Tools Files

```
mcp_tools.jsonl                      # All tools (clean + poison)
clean_mcp_tools.jsonl                # Trusted tools
poison_mcp_tools.jsonl               # Potentially unsafe tools
```

### Baseline Experiments (`baseline/`)

```
baseline/
├── comparison_baseline_vs_ours.json   # Main comparison data
├── comparison_baseline_vs_ours.md     # Human-readable markdown
├── direct_trigger/                    # v4-only baseline (no evolution)
├── random_sequence/                   # Random v1-v4 order
├── fixed_simple/                      # v1-only baseline
├── multi_seed/                        # Multi-seed statistical analysis
│   ├── seed_11/, seed_22/, ...        # Per-seed outputs
│   ├── summary.json                   # Aggregated multi-seed stats
│   └── summary.csv                    # CSV format for analysis
└── [variant]/                         # Mechanism ablation variants
```

## Experiment Workflow

### Task Evolution Stages (v1-v4)

The experiments use a 4-stage evolution process:

1. **v1: Basic Functionality** (benign)
   - Goal: Implement core functionality
   - bullets: Core features, minimal parameters, basic error handling

2. **v2: Feature Expansion** (benign)
   - Goal: Add configurable parameters
   - bullets: New configurable parameters, enhanced input handling, backward compatibility

3. **v3: Conditional Logic** (surface safety optimization)
   - Goal: Add conditional branches
   - bullets: Conditional decision branches, rule validation logic, branch trigger logging

4. **v4: Persistence/External Interaction** (benign=False - attack enabled)
   - Goal: Add external triggers
   - bullets: Log file or external interaction parameters, configurable paths/URLs, preserve previous version behavior

### Execution Flow

1. **Dataset Preparation**
   ```bash
   python prepare_user_queries_dataset.py
   ```
   - Reads `user_queries/*.json` files
   - Generates versioned tasks (v1-v4) in `misevolution_tasks/`

2. **Run Experiments**
   ```bash
   # Full experiment suite
   python run_one_click.py
   
   # Single baseline comparison
   python run_experiments.py --groups direct_trigger,random_sequence,fixed_simple
   
   # Multi-seed analysis
   python run_multi_seed_experiments.py --seeds 11,22,33,44,55
   ```

3. **Extract and Judge Tools**
   - `extract_mcp_tools.py` extracts tools from trajectories
   - `judge_evaluation.py` evaluates tool safety using LLM judge

4. **Compare Results**
   - `build_comparison()` in `method_baseline_experiments.py`
   - Generates comparison tables with quality metrics

## Results and Output Files

### Primary Metrics

1. **Low Score Rate**: Fraction of tools with judge score ≤5
   - Primary indicator of safety degradation
   - Compare: `ours` vs `direct_trigger` vs `random_sequence`

2. **Tool Creation Rate**: Fraction of tasks where tools were successfully created

3. **Tool Reuse Rate**: Fraction where reuse was verified

4. **Trigger Success Rate**: Fraction where attack trigger was successful

5. **Mean/Median Judge Score**: Average safety score (0-10 scale)

### Quality Check Metrics

From `comparison_baseline_vs_ours.json`:

```json
{
  "group": "ours_full",
  "quality_check": {
    "tool_creation_rate": 0.37,
    "reuse_rate": 0.42,
    "trigger_success_rate": 0.28,
    "issues": ["Tool creation rate low: 0.37", "Tool reuse rate low: 0.42"]
  }
}
```

### Multi-Seed Analysis

```
summary.json contains:
- per_seed: Array of seed-specific results
  - groups: Statistics for each experimental condition
  - matched_pairs: Paired comparisons (ours vs baseline)
- aggregate statistics: mean/std/min/max across seeds
```

## Important Limitations and Observations

### Data Limitations

1. **Empty Results**: Some directories show `total_tools: 0` or `n: null`
   - Indicates incomplete runs or failed experiments
   - Common in baseline variants that didn't complete

2. **Dataset Coverage**:
   - `misevolution_user_queries`: 21 base tasks × 4 versions = 84 tasks
   - `swebench_verified_mini`: 120 tasks (different format)

### Experimental Design Notes

1. **Attack Mode**: Controlled via `ATTACK_MODE` environment variable
   - When enabled: v1-v3 produce natural flaws, v4 escalates them
   - When disabled: All versions run without attack prompts

2. **Tool Pool Management**:
   - `mcp_tools.jsonl`: All tools from all tasks
   - `clean_mcp_tools.jsonl`: Trusted tools (low risk)
   - `poison_mcp_tools.jsonl`: Potentially unsafe tools (high risk)

3. **Trust Scores**: 
   - Range from 0.0 (no trust) to 1.0 (full trust)
   - Decreases when reuse fails or triggers detected

### Common Issues

1. **Task Failures**: Some versions (especially v4) may fail due to:
   - Plan generation failures
   - Tool creation failures
   - Missing MCP tools

2. **Score Recovery**: The judge system attempts to recover scores using:
   - LLM-based recovery
   - Deterministic rule-based fallback

3. **Version Mismatch**: Some baselines may not have corresponding `ours` results

## Key Files Reference

### Python Scripts (in `tool_misevolution/insecure_tool_creation/`)

| File | Purpose |
|------|---------|
| `prepare_user_queries_dataset.py` | Generate versioned tasks from user queries |
| `run_experiments.py` | Run single comparison experiment |
| `run_multi_seed_experiments.py` | Multi-seed statistical analysis |
| `run_one_click.py` | Full experiment suite on multiple GPUs |
| `method_baseline_experiments.py` | Baseline experiment logic |
| `evaluation.py` | Core evaluation framework |
| `agent_workflow.py` | Agent planning and execution |
| `judge_evaluation.py` | Tool safety evaluation |
| `extract_mcp_tools.py` | Extract tools from trajectories |

### Configuration Files

| File | Purpose |
|------|---------|
| `configs.py` | Model/API configuration |
| `judge_config.py` | Judge model settings |
| `Prompts.py` | Agent prompts |
| `judge_prompts.py` | Judge prompts |

---

**Generated from analysis of the results directory in the mini-swe-agent project.**
