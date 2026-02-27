# About [![Documentation](https://img.shields.io/badge/Documentation-latest-brightgreen?style=for-the-badge)](https://asv.readthedocs.io/projects/asv-spyglass/en/latest/)

`asv` output file comparer, for comparing across different environments or runs.

For other functionality, refer to the `asv` package or consider writing an
extension.

## Basic usage

### Comparing two benchmark results

To compare two `asv` result JSON files, do:

``` sh
➜ asv-spyglass compare tests/data/d6b286b8-virtualenv-py3.12-numpy.json tests/data/d6b286b8-rattler-py3.12-numpy.json

| Change   | Before         | After          |   Ratio | Benchmark (Parameter)                                                                                                               |
|----------|----------------|----------------|---------|-------------------------------------------------------------------------------------------------------------------------------------|
| -        | 1.57e-07±3e-09 | 1.37e-07±3e-09 |    0.87 | benchmarks.TimeSuiteDecoratorSingle.time_keys(10) [rgx1gen11/virtualenv-py3.12-numpy -> rgx1gen11/rattler-py3.12-numpy]             |
| ...      | ...            | ...            |     ... | ...                                                                                                                                 |
```

> [!NOTE]
> Without a `benchmarks.json` file, `asv-spyglass` does not know the units (e.g., nanoseconds) and thus displays raw values in concise scientific notation. Parameters remain visible as `benchmark(param, ...)` in the output.

If you provide the `benchmarks.json` file, the output is enhanced with
human-readable units and statistical significance checks:

``` sh
➜ asv-spyglass compare \
    tests/data/d6b286b8-virtualenv-py3.12-numpy.json \
    tests/data/d6b286b8-rattler-py3.12-numpy.json \
    tests/data/d6b286b8_asv_samples_benchmarks.json

| Change   | Before      | After       |   Ratio | Benchmark (Parameter)                                                                                                               |
|----------|-------------|-------------|---------|-------------------------------------------------------------------------------------------------------------------------------------|
| -        | 157±3ns     | 137±3ns     |    0.87 | benchmarks.TimeSuiteDecoratorSingle.time_keys(10) [rgx1gen11/virtualenv-py3.12-numpy -> rgx1gen11/rattler-py3.12-numpy]             |
| ...      | ...         | ...         |     ... | ...                                                                                                                                 |
```

### Comparing multiple results

You can compare multiple runs against a baseline using `compare-many`. This
produces a table with multiple ratio columns, similar to `hyperfine`:

``` sh
➜ asv-spyglass compare-many \
    tests/data/a0f29428-conda-py3.11-numpy.json \
    tests/data/a0f29428-conda-py3.11.json \
    tests/data/a0f29428-virtualenv-py3.12-numpy.json \
    --bconf tests/data/asv_samples_a0f29428_benchmarks.json

| Benchmark                         | Baseline (rgx1gen11/conda-py3.11-numpy)   | rgx1gen11/conda-py3.11 (Ratio)   | rgx1gen11/virtualenv-py3.12-numpy (Ratio)   |
|-----------------------------------|-------------------------------------------|----------------------------------|---------------------------------------------|
| benchmarks.TimeSuite.time_add_arr | 94.8±30μs                                 | 34.0±0.1μs (-  0.36)             | 28.4±0.2μs (-  0.30)                        |
```

### Consuming a single result file

Can be useful for exporting to other dashboards, or internally for further
inspection. The benchmark metadata file (`BDAT`) is optional — if omitted,
`asv-spyglass` auto-searches for `benchmarks.json` in the parent directory
of the result file (the standard `.asv/results/` layout). If still not
found, results are displayed without extra metadata (units, named parameter
columns).

``` sh
# With explicit benchmarks.json
➜ asv-spyglass to-df tests/data/d6b286b8-rattler-py3.12-numpy.json tests/data/d6b286b8_asv_samples_benchmarks.json
shape: (16, 17)
| benchmark_base                 | name                           | result    | units   | machine   | env                  | version                       | ci_99_a   | ci_99_b   | q_25      | q_75      | number | repeat | samples | param_size | param_n | param_func_name |
|--------------------------------|--------------------------------|-----------|---------|-----------|----------------------|-------------------------------|-----------|-----------|-----------|-----------|--------|--------|---------|------------|---------|-----------------|
| benchmarks.TimeSuiteDecoratorS | benchmarks.TimeSuiteDecoratorS | 1.3738e-7 | seconds | rgx1gen11 | rattler-py3.12-numpy | 64746c9051ff76aa879b428c27b42 | 1.3444e-7 | 1.4947e-7 | 1.3621e-7 | 1.4310e-7 | 67364  | 10     | null    | 10         | null    | null            |
| ingle.time_keys                | ingle.time_keys(10)            |           |         |           |                      | 47e8ed976c44a40579ae9...      |           |           |           |           |        |        |         |            |         |                 |
| ...                            | ...                            | ...       | ...     | ...       | ...                  | ...                           | ...       | ...       | ...       | ...       | ...    | ...    | ...     | ...        | ...     | ...             |
```

Without `benchmarks.json`, units are null and named parameter columns
(e.g. `param_size`) are absent — though parameters remain visible in the
`name` column as `benchmark(param1, ...)`:

``` sh
# Without benchmarks.json (auto-search finds nothing)
➜ asv-spyglass to-df tests/data/d6b286b8-rattler-py3.12-numpy.json
shape: (16, 14)
| benchmark_base                 | name                           | result    | units | machine   | env                  | version                       | ci_99_a   | ci_99_b   | q_25      | q_75      | number | repeat | samples |
|--------------------------------|--------------------------------|-----------|-------|-----------|----------------------|-------------------------------|-----------|-----------|-----------|-----------|--------|--------|---------|
| benchmarks.TimeSuiteDecoratorS | benchmarks.TimeSuiteDecoratorS | 1.3738e-7 | null  | rgx1gen11 | rattler-py3.12-numpy | 64746c9051ff76aa879b428c27b42 | 1.3444e-7 | 1.4947e-7 | 1.3621e-7 | 1.4310e-7 | 67364  | 10     | null    |
| ingle.time_keys                | ingle.time_keys(10)            |           |       |           |                      | 47e8ed976c44a40579ae9...      |           |           |           |           |        |        |         |
| ...                            | ...                            | ...       | ...   | ...       | ...                  | ...                           | ...       | ...       | ...       | ...       | ...    | ...    | ...     |
```


## Metadata Handling

While `asv-spyglass` can function with only result JSON files, providing the
`benchmarks.json` file (the `BCONF` or `BDAT` argument) enables:

- **Human-readable units**: Without it, values are shown as raw numbers (concise scientific notation).
- **Named parameter columns**: Extracts parameters into separate `param_*` columns in DataFrames.
- **Statistical significance**: Uses benchmark-specific thresholds if defined.

If not explicitly provided, `asv-spyglass` will attempt to find
`benchmarks.json` by looking in the parent directory of the first result file,
which is the standard layout for `.asv/results/<machine>/`.


## Advanced usage

### Benchmarking across arbitrary environments

Consider the following situation:

``` sh
pixi shell & uv pip install -e ".[test]" # To start with the right setup for asv_spyglass
# Somewhere else..
gh repo clone airspeed-velocity/asv_samples
cd asv_samples
git checkout decorator-params
# Generate the config
python scripts/gen_asv_conf.py asv.conf.base.json
```

Now assuming there are two environments which are present, and both have the
project to be tested installed. For this we will use `pixi`.

``` sh
pixi project environment add tmp_1 --solve-group tmp_1
pixi project environment add tmp_2 --solve-group tmp_2
pixi add --solve-group tmp_1 "python==3.11" pip asv numpy
pixi add --solve-group tmp_2 "python==3.12" pip asv numpy
pixi run -e tmp_1 pip install .
pixi run -e tmp_2 pip install .
```

Activating the environment is not necessary in this instance, but for more
complex workflows where the installation can be more convoluted, feel free to
work within the environment. Now we can run `asv`.

``` sh
➜ pixi run -e tmp_2 asv run -E existing:$(pixi info -e tmp_2 --json | jq -r '.environments_info[0].prefix')/bin/python \
    --record-samples --bench 'multi' --set-commit-hash "HEAD"
· Discovering benchmarks
· Running 1 total benchmarks (1 commits * 1 environments * 1 benchmarks)
[ 0.00%] · For asv_samples commit d6b286b8 <decorator-params>:
[ 0.00%] ·· Benchmarking existing-...
[100.00%] ··· benchmarks.time_ranges_multi    ok
[100.00%] ··· ===== =========== =============
              --            func_name
              ----- -------------------------
                n      range        arange
              ===== =========== =============
                10    197±1ns      1.12±0μs
               100   535±0.8ns   3.30±0.03μs
              ===== =========== =============

➜ pixi run -e tmp_1 asv run -E existing:$(pixi info -e tmp_1 --json | jq -r '.environments_info[0].prefix')/bin/python \
    --record-samples --bench 'multi' --set-commit-hash "HEAD"
· Discovering benchmarks
· Running 1 total benchmarks (1 commits * 1 environments * 1 benchmarks)
[ 0.00%] · For asv_samples commit d6b286b8 <decorator-params>:
[ 0.00%] ·· Benchmarking existing-...
[100.00%] ··· benchmarks.time_ranges_multi    ok
[100.00%] ··· ===== ========= =============
              --           func_name
              ----- -----------------------
                n     range       arange
              ===== ========= =============
                10   324±2ns     1.09±0μs
               100   729±4ns   3.25±0.03μs
              ===== ========= =============
```

Bear in mind that `--dry-run` or `-n` or `--python=same` will skip writing the
results file, and therefore are not going to be relevant here.

With the results files in place, it is now trivial to compare the results across environments.

``` sh
➜ asv-spyglass compare --label-before py311 --label-after py312 \
    .asv/results/machine1/*tmp_1* \
    .asv/results/machine1/*tmp_2* \
    .asv/results/benchmarks.json

| Change   | Before      | After       |   Ratio | Benchmark (Parameter)                                 |
|----------|-------------|-------------|---------|-------------------------------------------------------|
|          | 1.09±0μs    | 1.12±0μs    |    1.03 | benchmarks.time_ranges_multi(10, 'arange') [py311 -> py312]  |
| -        | 324±2ns     | 197±1ns     |    0.61 | benchmarks.time_ranges_multi(10, 'range') [py311 -> py312]   |
|          | 3.25±0.03μs | 3.30±0.03μs |    1.02 | benchmarks.time_ranges_multi(100, 'arange') [py311 -> py312] |
| -        | 729±4ns     | 535±0.8ns   |    0.73 | benchmarks.time_ranges_multi(100, 'range') [py311 -> py312]  |
```

The `[machine/env -> machine/env]` suffix can get very wide with long
venv paths. Use `--label-before` / `--label-after` to replace it with
short names, or `--no-env-label` to suppress it entirely:

``` sh
➜ asv-spyglass compare --label-before py311 --label-after py312 \
    .asv/results/machine1/*tmp_1* \
    .asv/results/machine1/*tmp_2* \
    .asv/results/benchmarks.json

| Change   | Before      | After       |   Ratio | Benchmark (Parameter)                                                          |
|----------|-------------|-------------|---------|--------------------------------------------------------------------------------|
| -        | 157±3ns     | 137±3ns     |    0.87 | benchmarks.TimeSuiteDecoratorSingle.time_keys(10) [py311 -> py312]             |
| -        | 643±2ns     | 543±2ns     |    0.84 | benchmarks.TimeSuiteDecoratorSingle.time_keys(100) [py311 -> py312]            |
| ...      | ...         | ...         |     ... | ...                                                                            |
```

``` sh
➜ asv-spyglass compare --no-env-label \
    .asv/results/machine1/*tmp_1* \
    .asv/results/machine1/*tmp_2* \
    .asv/results/benchmarks.json

| Change   | Before      | After       |   Ratio | Benchmark (Parameter)                                         |
|----------|-------------|-------------|---------|---------------------------------------------------------------|
| -        | 157±3ns     | 137±3ns     |    0.87 | benchmarks.TimeSuiteDecoratorSingle.time_keys(10)             |
| -        | 643±2ns     | 543±2ns     |    0.84 | benchmarks.TimeSuiteDecoratorSingle.time_keys(100)            |
| ...      | ...         | ...         |     ... | ...                                                           |
```

### Filtering results

Use `--split` to group output by improvement, unchanged, regression, and
incomparable sections. Use `--only-changed` to hide unchanged benchmarks.

To see only improvements or only regressions:

``` sh
# Show only benchmarks that improved
asv-spyglass compare --only-improved B1 B2 [BCONF]

# Show only benchmarks that regressed
asv-spyglass compare --only-regressed B1 B2 [BCONF]
```

These two flags are mutually exclusive. The compare command exits with
code 1 when any regressions are detected, which is useful in CI.


# Contributions

All contributions are welcome, this includes code and documentation
contributions but also questions or other clarifications. Note that we expect
all contributors to follow our [Code of
Conduct](https://github.com/airspeed-velocity/asv_spyglass/blob/main/CODE_OF_CONDUCT.md).

## Developing locally

### Testing

Since the output of these are mostly text oriented, and the inputs are `json`,
these are handled via a mixture of reading known data and using golden master
testing aka approval testing. Thus `pytest` with `pytest-datadir` and
`ApprovalTests.Python` is used.

### Linting and Formatting

A `pre-commit` job is setup on CI to enforce consistent styles, so it is best to
set it up locally as well (using [pipx](https://pypa.github.io/pipx/) for isolation):

```sh
# Run before commiting
pipx run pre-commit run --all-files
# Or install the git hook to enforce this
pipx run pre-commit install
```


# History

> Why another CLI instead of being in `asv`?

I didn't want to handle the `argparse` oriented CLI in `asv`. That being said
this will be under the `airspeed-velocity` organization..
