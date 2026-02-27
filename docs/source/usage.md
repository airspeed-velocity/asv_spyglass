# Usage Guide

## Installation

You can install `asv-spyglass` using `pip`, `pixi`, or `uv`:

```bash
pip install asv-spyglass
# OR
pixi add asv-spyglass
# OR
uv add asv-spyglass
```

## Basic Comparison

The most common use case is comparing two result files:

```bash
asv-spyglass compare result_before.json result_after.json
```

If you have the `benchmarks.json` file available (usually in the root of your ASV project), you can provide it for enhanced metadata:

```bash
asv-spyglass compare result_before.json result_after.json benchmarks.json
```

## Comparing Multiple Runs

To compare multiple contender runs against a single baseline:

```bash
asv-spyglass compare-many baseline.json contender1.json contender2.json --bconf benchmarks.json
```

## Metadata Handling

`asv-spyglass` can function with only result JSON files. However, providing the `benchmarks.json` file enables:

- **Human-readable units**: Values are shown with appropriate prefixes (e.g., `ns`, `μs`) instead of raw scientific notation.
- **Parameter names**: DataFrame exports will have semantic column names for benchmark parameters.
- **Statistical significance**: Benchmark-specific thresholds are used if defined.

If not explicitly provided, the tool will attempt to automatically find `benchmarks.json` in the parent directory of the first result file.
