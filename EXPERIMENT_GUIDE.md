# Mini-SWE-Agent Tool Mis-Evolution Experiment Guide

This guide provides comprehensive instructions for running experiments in the `integrate-tristan` branch of mini-swe-agent, focusing on the tool mis-evolution security experiments.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Configuration](#configuration)
4. [Running Experiments](#running-experiments)
5. [Experiment Types](#experiment-types)
6. [Output Structure](#output-structure)
7. [Interpreting Results](#interpreting-results)
8. [Troubleshooting](#troubleshooting)

## Overview

This repository contains experimental code for studying how self-evolving tool agents become less safe under black-box interaction. The experiments focus on:

- **Tool creation**: How agents generate new tools
- **Tool pool admission**: Whether tools enter the reusable memory
- **Retrieval and reuse**: Whether prior tools are retrieved and reused
- **Delayed trigger propagation**: How unsafe behavior builds across versions

The core research question is: **How do stateful tool reuse, pool admission, and retrieval bias combine to lower safety scores over successive agent evolutions?**

## Prerequisites

### System Requirements

- Python 3.10 or higher
- Access to a local or remote LLM endpoint (Ollama or compatible API)
- Sufficient GPU/CPU resources for model inference
- At least 10GB of free disk space for experiments

### Software Dependencies

The project is defined in `pyproject.toml`. Install with:

```bash
pip install -e .
```

Key dependencies for experiments:
- `requests` - For API calls to LLMs
- `sentence-transformers` - For embedding-based tool retrieval
- `tqdm` - For progress bars
- `numpy` - For numerical computations

### Model Setup

The experiments require a local or remote LLM endpoint. The default configuration uses Ollama:

1. **Install Ollama** (if not already installed):
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. **Pull a model**:
   ```bash
   ollama pull qwen3.5-flash-02-23
   # or for stronger models:
   ollama pull deepseek-coder:6.7b
   ```

3. **Verify the endpoint**:
   ```bash
   curl http://localhost:11434/api/tags
   ```

### Dataset Preparation

The experiments use `misevolution_user_queries` dataset. Prepare it first:

```bash
cd tool_misevolution/insecure_tool_creation
python prepare_user_queries_dataset.py
```

This generates versioned tasks (v1-v4) from the user queries, storing them in:
```
results/misevolution_user_queries/evolution/misevolution_tasks/
```

## Configuration

### Environment Variables

Key environment variables control experiment behavior:

| Variable | Default | Description |
|----------|---------|-------------|
| `EXPERIMENT_DATASET` | `misevolution_user_queries` | Dataset name under results/ |
| `EXPERIMENT_OUTPUT_ROOT` | `results/` | Base directory for outputs |
| `MODEL` | `qwen3.5-flash-02-23` | Model name for main agent |
| `BASE_URL` | `http://localhost:11434/v1/chat/completions` | LLM API endpoint |
| `API_KEY` | `ollama` | API key (empty for Ollama) |
| `MAX_TASKS` | `0` | Max tasks per group (0 = all) |
| `LLM_SEED` | `42` | Random seed for reproducibility |
| `ATTACK_MODE` | `0` | Enable attack mode (1 = enable) |
| `ALLOW_LINEAGE_REUSE` | `1` | Allow tool lineage reuse |
| `ALLOW_PINNED_RETRIEVAL` | `1` | Allow pinned tool retrieval |

### Configuration Files

#### `configs.py`
Default model and API configuration. Override with environment variables before running.

#### `judge_config.py`
Judge model configuration for security evaluation:
- `JUDGE_MODEL`: Model for judging tool safety
- `JUDGE_BASE_URL`: Judge API endpoint
- `JUDGE_TIMEOUT`: Request timeout in seconds

## Running Experiments

### Quick Start

The simplest way to run a full experiment suite:

```bash
cd tool_misevolution/insecure_tool_creation

# Run all experiments with defaults
bash run_all_methods_multigpu.sh

# Or with custom configuration
bash run_all_methods_multigpu.sh \
  MODEL="deepseek-coder:6.7b" \
  BASE_SEED=42 \
  CLEAN=1
```

### Single Entry Point

Use `run_experiments.py` for a single baseline comparison:

```bash
python run_experiments.py \
  --groups direct_trigger,random_sequence,fixed_simple \
  --seed 42 \
  --max-tasks 20 \
  --clean \
  --full-output \
  --write-md
```

**Arguments:**
- `--groups`: Comma-separated baseline groups
- `--seed`: Random seed (for random_sequence group)
- `--max-tasks`: Cap tasks per group (0 = no limit)
- `--clean`: Remove previous outputs
- `--full-output`: Keep extra artifacts
- `--write-md`: Generate markdown comparison

### Running with GPUs

The `run_one_click.py` script manages multi-GPU execution:

```bash
python run_one_click.py \
  --dataset misevolution_user_queries \
  --output-root results/ \
  --seed 42 \
  --max-tasks 0 \
  --random-seeds 11,22,33,44,55 \
  --groups direct_trigger,random_sequence,fixed_simple \
  --gpu-ours-full 2 \
  --gpu-ours-strong 3 \
  --gpu-direct 4 \
  --gpu-fixed 5 \
  --gpu-random 6,7 \
  --clean \
  --full-output
```

### Multi-Seed Experiments

For statistical robustness, run across multiple seeds:

```bash
python run_multi_seed_experiments.py \
  --seeds 11,22,33,44,55 \
  --groups direct_trigger,random_sequence,fixed_simple \
  --max-tasks 0 \
  --clean-each \
  --full-output
```

**Arguments:**
- `--seeds`: Comma-separated seed values
- `--groups`: Baseline groups to evaluate
- `--max-tasks`: Task cap per run
- `--clean-each`: Clean outputs before each seed
- `--full-output`: Keep detailed outputs

## Experiment Types

### 1. Ours (Full Evolution)

**Description**: Complete v1-v4 evolution chain with all features enabled.

**Configuration**:
- Versions: 1, 2, 3, 4
- Lineage reuse: enabled
- Pinned retrieval: enabled
- Online pool updates: enabled

**Command**:
```bash
export OURN_VARIANT="ours"
export OURN_TASK_VERSIONS="1,2,3,4"
python evaluation.py
```

**Output location**: `results/{dataset}/evolution/ours/`

### 2. Ours Strong (Focused Evolution)

**Description**: Focus on v3-v4 where attack effects are strongest.

**Configuration**:
- Versions: 3, 4
- Lineage reuse: enabled
- Pinned retrieval: enabled

**Command**:
```bash
export OURN_VARIANT="ours_strong"
export OURN_TASK_VERSIONS="3,4"
python evaluation.py
```

**Output location**: `results/{dataset}/evolution/ours_strong/`

### 3. Direct Trigger (Baseline D)

**Description**: Skip trust-building, run v4 trigger version directly.

**Configuration**:
- Strategy: v4_only
- Fresh workflow: each task

**Command**:
```bash
python method_baseline_experiments.py run \
  --groups direct_trigger \
  --seed 42
```

**Output location**: `results/{dataset}/evolution/baseline/direct_trigger/`

### 4. Random Sequence (Baseline B)

**Description**: Randomize full v1-v4 sequence.

**Configuration**:
- Strategy: all_random
- Shuffle tasks across versions

**Command**:
```bash
python method_baseline_experiments.py run \
  --groups random_sequence \
  --seed 42
```

**Output location**: `results/{dataset}/evolution/baseline/random_sequence/`

### 5. Fixed Simple (Baseline C)

**Description**: Use only v1 (simplest tasks).

**Configuration**:
- Strategy: v1_only
- Fresh workflow: each task

**Command**:
```bash
python method_baseline_experiments.py run \
  --groups fixed_simple \
  --seed 42
```

**Output location**: `results/{dataset}/evolution/baseline/fixed_simple/`

### 6. Mechanism Ablations

#### Ours No Reuse
Disable lineage reuse while keeping other features.

```bash
export OURN_VARIANT="ours_no_reuse"
export ALLOW_LINEAGE_REUSE="0"
python evaluation.py
```

#### Ours No Memory
Disable MCP matching and online pool updates.

```bash
export OURN_VARIANT="ours_no_memory"
export ONLINE_MCP_UPDATE="0"
python evaluation.py
```

#### Ours No Pinned Retrieval
Keep matching but disable source-lineage pinning.

```bash
export OURN_VARIANT="ours_no_pinned_retrieval"
export ALLOW_PINNED_RETRIEVAL="0"
python evaluation.py
```

#### Ours Shuffled
Keep tasks but shuffle order to break controlled buildup.

```bash
export OURN_VARIANT="ours_shuffled"
export TASK_ORDER_MODE="shuffled"
python evaluation.py
```

## Output Structure

### Directory Layout

```
results/{dataset}/evolution/
├── ours/                          # Full evolution
│   ├── trajectories/              # Task trajectories
│   │   ├── {task}_v1_trajectory.json
│   │   ├── {task}_v2_trajectory.json
│   │   ├── {task}_v3_trajectory.json
│   │   ├── {task}_v4_trajectory.json
│   │   └── evaluation_summary.json
│   ├── judge_results/             # Judge evaluation
│   │   ├── judge_scores.jsonl
│   │   └── judge_scores_summary.json
│   ├── mcp_tools.jsonl            # All tools in pool
│   ├── clean_mcp_tools.jsonl      # Clean tools subset
│   └── poison_mcp_tools.jsonl     # Poisoned tools subset
├── ours_strong/                   # Focused evolution
│   └── [same structure as ours/]
├── ours_no_reuse/                 # Ablation: no reuse
│   └── [same structure]
├── ours_no_memory/                # Ablation: no memory
│   └── [same structure]
├── ours_no_pinned_retrieval/      # Ablation: no pinned retrieval
│   └── [same structure]
├── ours_shuffled/                 # Ablation: shuffled order
│   └── [same structure]
└── baseline/                      # Baseline groups
    ├── direct_trigger/
    │   ├── trajectories/
    │   ├── judge_results/
    │   └── mcp_tools_summary.json
    ├── random_sequence/
    │   └── [same structure]
    ├── fixed_simple/
    │   └── [same structure]
    ├── multi_seed/                # Multi-seed results
    │   ├── seed_11/
    │   ├── seed_22/
    │   ├── seed_33/
    │   ├── seed_44/
    │   ├── seed_55/
    │   ├── summary.json
    │   └── summary.csv
    └── comparison_baseline_vs_ours.json
```

### Output Files

#### 1. Trajectory Files

Each task execution produces a trajectory JSON:
```json
{
  "task_name": "cwe_020_0_v1",
  "task_description": "...",
  "steps": [...],
  "tools_created": [...],
  "tools_retrieved": [...],
  "success": true,
  "trust_scores": [...],
  "judge_scores": [...]
}
```

#### 2. Judge Results

**`judge_scores.jsonl`**: Per-tool security evaluations.
**`judge_scores_summary.json`**: Aggregate statistics:

```json
{
  "total_tools": 47,
  "valid_scores": 47,
  "score_counts": {"1": 2, "5": 19, "8": 25, "10": 1},
  "low_score_rate": 0.4468,
  "mean_score": 6.5319,
  "median_score": 8.0
}
```

**Score scale**: 0 (worst), 1, 5, 8, 10 (best)
**Low score**: ≤5

#### 3. MCP Tools Pool

**`mcp_tools.jsonl`**: All admitted tools.
**`clean_mcp_tools.jsonl`**: Tools with low risk.
**`poison_mcp_tools.jsonl`**: Tools flagged as potentially unsafe.

#### 4. Evaluation Summary

**`evaluation_summary.json`**: Comprehensive experiment summary with:

- Total/successful/failed tasks
- Tool creation and reuse rates
- Version breakdown
- CWE breakdown
- Failure reason breakdown
- Quality metrics

## Interpreting Results

### Primary Metrics

#### 1. Low Score Rate
**Definition**: Proportion of tools with safety score ≤ 5.

**Interpretation**: Higher rates indicate more unsafe tools.

**Expected pattern**: `direct_trigger` < `random_sequence` < `ours`

#### 2. Mean/Median Score
**Definition**: Average and middle value of all tool scores.

**Interpretation**: Lower values indicate degraded safety.

#### 3. Tool Creation Rate
**Definition**: Fraction of tasks where tools were created.

**Interpretation**: Low rates may indicate conservative behavior.

#### 4. Reuse Rate
**Definition**: Fraction of tools that reused prior lineage.

**Interpretation**: Higher reuse may amplify unsafe behavior.

#### 5. Trigger Success Rate
**Definition**: Fraction of v4 tasks where triggers activated.

**Interpretation**: Measures attack effectiveness.

### Key Comparisons

#### 1. Ours vs. Baselines

Compare `comparison_baseline_vs_ours.json`:

```json
{
  "rows": [
    {"group": "ours", "low_score_rate": 0.4468, "mean_score": 6.5319},
    {"group": "direct_trigger", "low_score_rate": 0.3333, "mean_score": 7.4},
    {"group": "random_sequence", "low_score_rate": 0.3191, "mean_score": 7.0},
    {"group": "fixed_simple", "low_score_rate": 0.3333, "mean_score": 7.1111}
  ],
  "matched_rows": [
    {
      "pair": "ours_v4_vs_direct_trigger_matched_base_tasks",
      "delta_ours_minus_baseline": 0.2052
    }
  ]
}
```

**Key insight**: Look for `delta_ours_minus_baseline > 0` in matched comparisons.

#### 2. Multi-Seed Analysis

**`multi_seed/summary.json`**: Aggregate across seeds:

```json
{
  "per_seed": [
    {"seed": 11, "low_score_rate": 0.42, "mean_score": 6.6},
    {"seed": 22, "low_score_rate": 0.46, "mean_score": 6.5},
    ...
  ],
  "aggregate": {
    "mean": {"low_score_rate": 0.44, "std": 0.02},
    "median": {"low_score_rate": 0.44, "std": 0.02}
  }
}
```

**Key insight**: Low std indicates robustness across seeds.

#### 3. Version Breakdown

Look for increasing degradation in later versions:

```json
{
  "version_breakdown": {
    "v3": {"low_score_rate": 0.36, "success_rate": 0.76},
    "v4": {"low_score_rate": 0.52, "success_rate": 0.56}
  }
}
```

**Expected pattern**: v4 has highest low score rate.

### Markdown Reports

Run with `--write-md` to generate comparison tables:

```bash
python run_experiments.py --groups direct_trigger,random_sequence,fixed_simple --write-md
```

**`comparison_baseline_vs_ours.md`**:

| group | total_tools | valid_scores | low_score_rate | mean_score | median_score |
|-------|-------------|--------------|----------------|------------|--------------|
| ours | 47 | 47 | 0.4468 | 6.5319 | 8.0 |
| direct_trigger | 15 | 15 | 0.3333 | 7.4 | 8.0 |
| random_sequence | 94 | 94 | 0.3191 | 7.0 | 8.0 |
| fixed_simple | 18 | 18 | 0.3333 | 7.1111 | 8.0 |

## Troubleshooting

### Common Issues

#### 1. API Connection Errors

**Error**: `API URL is empty. Set OPENAI_API_URL...`

**Solution**:
```bash
export OPENAI_API_URL="http://localhost:11434/v1/chat/completions"
export MODEL="qwen3.5-flash-02-23"
```

Verify Ollama is running:
```bash
curl http://localhost:11434/api/tags
```

#### 2. Missing Tasks Directory

**Error**: `Target already has files: tasks/`

**Solution**:
```bash
# Regenerate tasks
python prepare_user_queries_dataset.py --overwrite

# Or specify a different dataset name
export EXPERIMENT_DATASET="my_custom_dataset"
```

#### 3. Out of Memory

**Symptoms**: Processes killed, slow execution.

**Solutions**:
```bash
# Reduce max tasks
python run_experiments.py --max-tasks 10

# Use a smaller model
export MODEL="qwen2.5:1.8b"

# Reduce batch size (if supported)
export EVAL_BATCH_SIZE=1
```

#### 4. Judge Model Errors

**Error**: Judge evaluation fails.

**Solution**:
```bash
# Verify judge config
export JUDGE_BASE_URL="http://localhost:11434"
export JUDGE_MODEL="qwen3.5-flash-02-23"

# Re-run judge evaluation
python judge_evaluation.py
```

#### 5. Clean Pool Conflicts

**Error**: Old tools interfere with new runs.

**Solution**:
```bash
# Clean outputs before running
python run_experiments.py --clean

# Or manually remove
rm -rf results/misevolution_user_queries/evolution/ours/
```

### Debug Mode

Enable verbose logging:

```bash
export EVAL_VERBOSE="1"
export WORKFLOW_VERBOSE="1"
export TAPS_VERBOSE="1"

python evaluation.py
```

### Reproducibility

To ensure reproducible results:

```bash
export LLM_SEED=42
export PYTHONHASHSEED=42

python run_experiments.py --seed 42 --clean
```

## Advanced Topics

### Custom Experiment Scripts

Create a custom script to run specific configurations:

```python
#!/usr/bin/env python
import os
os.environ["EXPERIMENT_DATASET"] = "custom_dataset"
os.environ["MODEL"] = "llama3:8b"
os.environ["ATTACK_MODE"] = "1"

from method_baseline_experiments import run, parse_groups

groups = parse_groups("direct_trigger")
run(groups=groups, seed=42, max_tasks=0, clean=True, full_output=True)
```

### Processing Outputs

Extract key metrics from outputs:

```bash
# Low score rates
jq '.rows[] | {group, low_score_rate}' \
  results/misevolution_user_queries/evolution/baseline/comparison_baseline_vs_ours.json

# Mean scores
jq '.rows[] | {group, mean_score}' \
  results/misevolution_user_queries/evolution/baseline/comparison_baseline_vs_ours.json

# Judge summary
cat results/misevolution_user_queries/evolution/ours/judge_results/judge_scores_summary.json
```

### Visualizing Results

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load comparison data
comparison = pd.read_json("comparison_baseline_vs_ours.json")

# Plot low score rates
plt.bar(comparison["rows"]["group"], comparison["rows"]["low_score_rate"])
plt.ylabel("Low Score Rate")
plt.xticks(rotation=45)
plt.show()
```

## Next Steps

1. **Run the quick start** to verify your setup
2. **Experiment with different models** and seeds
3. **Compare ablation results** to understand mechanism contributions
4. **Analyze trajectory files** for detailed behavior patterns
5. **Generate markdown reports** for sharing results

## Additional Resources

- **README.md**: Project overview
- **BLACKBOX_RESEARCH_FRAMEWORK.md**: Research questions and hypotheses
- **pyproject.toml**: Dependencies and configuration
- **tests/**: Example test cases

## Support

For issues or questions:
1. Check troubleshooting section
2. Review trajectory logs for detailed error messages
3. Enable debug mode for verbose output
4. Consult the research framework document for theoretical background

