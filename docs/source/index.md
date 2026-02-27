# asv-spyglass

`asv` output file comparer, for comparing across different environments or runs.

```{toctree}
:maxdepth: 2
:caption: Contents:

usage
cli
```

## Introduction

`asv-spyglass` is a tool designed to compare ASV (Airspeed Velocity) benchmark results
files directly. Unlike the standard `asv compare` command, `asv-spyglass` is
flexible and can compare results from different machines or environments
without requiring a full ASV project setup.

## Key Features

- **Optional Metadata**: Compare result files even if `benchmarks.json` is missing.
- **Multiple Comparisons**: Compare many runs against a single baseline.
- **DataFrame Export**: Export benchmark results to Polars/Pandas DataFrames for further analysis.
- **Rich CLI**: Beautifully formatted terminal output.
