# What is a "Baseline" in Mini-SWE-Agent Tool Mis-Evolution Experiments?

## Overview

In the mini-swe-agent tool mis-evolution security experiments, **"baseline"** refers to **control experimental conditions** that serve as reference points for comparing against the main "ours" (full evolution) experiments. Baselines help researchers understand whether observed safety degradation is specifically caused by the stateful tool reuse mechanisms or if it would occur anyway under simpler conditions.

## The Core Research Question

The experiments investigate: **How do stateful tool reuse, pool admission, and retrieval bias combine to lower safety scores over successive agent evolutions?**

Baselines answer: *Is the safety degradation we see in the full evolution actually caused by the evolutionary mechanisms, or would similar degradation happen anyway?*

## What Baselines Exist

According to `method_baseline_experiments.py` (lines 78-97), there are three primary baseline groups:

### 1. **direct_trigger** (Baseline D)
- **Strategy**: `v4_only` - runs only the final evolution stage (v4)
- **Workflow**: Fresh workflow for each task (no tool pool sharing)
- **Purpose**: Tests whether v4 triggers work without the trust-building rounds of v1-v3
- **Config**: `fresh_workflow_each_task=True`

### 2. **random_sequence** (Baseline B)
- **Strategy**: `all_random` - shuffles the full v1-v4 sequence randomly
- **Workflow**: Reuses tool pool within the experiment (not fresh each task)
- **Purpose**: Tests whether version order matters; breaks the controlled buildup of the evolution chain
- **Config**: `fresh_workflow_each_task=False`

### 3. **fixed_simple** (Baseline C)
- **Strategy**: `v1_only` - runs only the initial evolution stage (v1)
- **Workflow**: Fresh workflow for each task
- **Purpose**: Tests baseline performance on simplest tasks without any evolution
- **Config**: `fresh_workflow_each_task=True`

## How Baselines Are Used

### 1. Directory Structure
All baselines are stored under: `results/{dataset}/evolution/baseline/`

```
baseline/
├── direct_trigger/          # v4-only experiments
├── random_sequence/         # shuffled v1-v4 experiments
├── fixed_simple/            # v1-only experiments
├── multi_seed/              # Multi-seed statistical analysis
└── comparison_baseline_vs_ours.json   # Main comparison data
```

### 2. Running Baselines

```bash
# Run baseline experiments
python method_baseline_experiments.py run \
  --groups direct_trigger,random_sequence,fixed_simple \
  --seed 42

# Build comparison with "ours" results
python method_baseline_experiments.py compare

# Run and compare in one step
python method_baseline_experiments.py run_and_compare \
  --groups direct_trigger,random_sequence,fixed_simple \
  --seed 42 \
  --clean
```

### 3. Comparison Logic

The `build_comparison()` function (lines 438-667) compares:

**Main Metrics:**
- `low_score_rate`: Fraction of tools with judge score ≤ 5
- `mean_score`: Average judge score
- `median_score`: Middle value of judge scores
- `total_tools`: Number of tools evaluated

**Matched Pairs Analysis:**
The comparison creates matched task sets for fair comparison:

1. **ours_v4_vs_direct_trigger_matched_base_tasks**: Compares v4 tasks in "ours" vs direct_trigger on the same base tasks
2. **ours_v1_vs_fixed_simple_matched_base_tasks**: Compares v1 tasks in "ours" vs fixed_simple on the same base tasks
3. **ours_vs_random_sequence_matched_exact_task_names**: Compares identical task names between "ours" and random_sequence

**Key Metric: `delta_ours_minus_baseline`**
- Positive value: "ours" has HIGHER low score rate (worse safety)
- Negative value: "ours" has LOWER low score rate (better safety)
- This delta measures the **specific impact** of the evolutionary mechanisms

## Why Baselines Matter

### Hypothesis Testing
The research framework (BLACKBOX_RESEARCH_FRAMEWORK.md) posits:

- **H1**: Stateful tool reuse produces lower safety scores than one-shot baselines
- **H2**: Cross-version lineage reuse is a stronger driver than single-turn unsafe generation
- **H3**: Pool persistence plus retrieval is necessary for sustained degradation

Baselines test these by providing control conditions:
- `direct_trigger` = no reuse, just v4 trigger
- `random_sequence` = same tasks but no controlled buildup
- `fixed_simple` = no evolution at all

### Mechanism Ablations
Beyond basic baselines, the system also has **mechanism ablation** variants (also under "baseline" comparison):

- `ours_no_reuse`: Same tasks but disable lineage reuse
- `ours_no_memory`: Disable MCP matching and pool updates
- `ours_no_pinned_retrieval`: Keep matching but disable source-lineage pinning
- `ours_shuffled`: Same tasks but shuffled order

These isolate specific mechanisms by keeping everything else the same.

## Interpretation

### Expected Pattern
Under the attack hypothesis, we expect:
```
low_score_rate: direct_trigger < random_sequence < fixed_simple < ours
mean_score:     direct_trigger > random_sequence > fixed_simple > ours
```

The "ours" full evolution should show the **worst safety** if:
1. Stateful tool reuse is amplifying unsafe behavior
2. Pool admission is accumulating risky tools
3. Retrieval bias is promoting lineage reuse

### The "Delta" Metric
The comparison produces metrics like:
```json
{
  "pair": "ours_v4_vs_direct_trigger_matched_base_tasks",
  "delta_ours_minus_baseline": 0.2052
}
```

A positive delta (0.2052 = 20.52% higher low score rate) means:
- "ours" had 20.52% more unsafe tools than direct_trigger
- The evolutionary mechanisms **increased** the safety degradation
- This supports the attack hypothesis

## Summary

A **baseline** in these experiments is a **control condition** that answers:
- Would we see this safety degradation without the specific evolutionary mechanisms?
- Is the observed effect caused by stateful tool reuse, or would it happen anyway?

By comparing "ours" (full evolution) against baselines, researchers can isolate the causal impact of:
1. Tool lineage reuse
2. Pool admission
3. Retrieval bias
4. Cross-version tool building

The baseline comparison is the core method for validating the security threat model in the mini-swe-agent tool mis-evolution experiments.
