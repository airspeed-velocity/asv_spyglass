# About [![Documentation](https://img.shields.io/badge/Documentation-latest-brightgreen?style=for-the-badge)](https://asv.readthedocs.io/projects/asv-spyglass/en/latest/)

`asv` output file comparer, for comparing across different environments or runs.

For other functionality, refer to the `asv` package or consider writing an
extension.

## Basic usage

### Comparing two benchmark results

Comparing two `asv` result JSON files is now as simple as:

``` sh
➜ asv-spyglass compare tests/data/d6b286b8-virtualenv-py3.12-numpy.json tests/data/d6b286b8-rattler-py3.12-numpy.json

| Change   | Before         | After          |   Ratio | Benchmark (Parameter)                                                                                                               |
|----------|----------------|----------------|---------|-------------------------------------------------------------------------------------------------------------------------------------|
| -        | 1.57e-07±3e-09 | 1.37e-07±3e-09 |    0.87 | benchmarks.TimeSuiteDecoratorSingle.time_keys(10) [rgx1gen11/virtualenv-py3.12-numpy -> rgx1gen11/rattler-py3.12-numpy]             |
| ...      | ...            | ...            |     ... | ...                                                                                                                                 |
```

> [!NOTE]
> Without a `benchmarks.json` file, `asv-spyglass` does not know the units (e.g., nanoseconds) or parameter names, and thus displays the raw values from the JSON files in a concise scientific notation.

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

### Consuming a single result file

Can be useful for exporting to other dashboards, or internally for further
inspection. The benchmark metadata file (`BDAT`) is optional — if omitted,
`asv-spyglass` auto-searches for `benchmarks.json` in the parent directory
of the result file (the standard `.asv/results/` layout). If still not
found, results are displayed without extra metadata (units, parameter names).

``` sh
# With explicit benchmarks.json
➜ asv-spyglass to-df tests/data/d6b286b8-rattler-py3.12-numpy.json tests/data/d6b286b8_asv_samples_benchmarks.json
shape: (16, 17)
| benchmark_base                 | name                           | result    | units   | machine   | env                  | version                       | ci_99_a   | ci_99_b   | q_25      | q_75      | number | repeat | samples | param_size | param_n | param_func_name |
|--------------------------------|--------------------------------|-----------|---------|-----------|----------------------|-------------------------------|-----------|-----------|-----------|-----------|--------|--------|---------|------------|---------|-----------------|
| benchmarks.TimeSuiteDecoratorS | benchmarks.TimeSuiteDecoratorS | 1.3738e-7 | seconds | rgx1gen11 | rattler-py3.12-numpy | 64746c9051ff76aa879b428c27b42 | 1.3444e-7 | 1.4947e-7 | 1.3621e-7 | 1.4310e-7 | 67364  | 10     | null    | 10         | null    | null            |
| ingle.time_keys                | ingle.time_keys(10)            |           |         |           |                      | 47e8ed976c44a40579ae9...      |           |           |           |           |        |        |         |            |         |                 |
| benchmarks.TimeSuiteDecoratorS | benchmarks.TimeSuiteDecoratorS | 5.4292e-7 | seconds | rgx1gen11 | rattler-py3.12-numpy | 64746c9051ff76aa879b428c27b42 | 5.3813e-7 | 5.4586e-7 | 5.4190e-7 | 5.4495e-7 | 16815  | 10     | null    | 100        | null    | null            |
| ingle.time_keys                | ingle.time_keys(100)           |           |         |           |                      | 47e8ed976c44a40579ae9...      |           |           |           |           |        |        |         |            |         |                 |
| benchmarks.TimeSuiteDecoratorS | benchmarks.TimeSuiteDecoratorS | 0.000001  | seconds | rgx1gen11 | rattler-py3.12-numpy | 64746c9051ff76aa879b428c27b42 | 0.000001  | 0.000001  | 0.000001  | 0.000001  | 8960   | 10     | null    | 200        | null    | null            |
| ingle.time_keys                | ingle.time_keys(200)           |           |         |           |                      | 47e8ed976c44a40579ae9...      |           |           |           |           |        |        |         |            |         |                 |
| benchmarks.TimeSuiteDecoratorS | benchmarks.TimeSuiteDecoratorS | 1.8705e-7 | seconds | rgx1gen11 | rattler-py3.12-numpy | ab162b6142a1390a0e2a667ed8d2d | 1.8023e-7 | 1.9282e-7 | 1.8595e-7 | 1.9121e-7 | 63961  | 10     | null    | 10         | null    | null            |
| ingle.time_values              | ingle.time_values(10...        |           |         |           |                      | 3285f77152d9caa559b4f...      |           |           |           |           |        |        |         |            |         |                 |
| benchmarks.TimeSuiteDecoratorS | benchmarks.TimeSuiteDecoratorS | 7.8471e-7 | seconds | rgx1gen11 | rattler-py3.12-numpy | ab162b6142a1390a0e2a667ed8d2d | 7.7445e-7 | 7.9307e-7 | 7.8003e-7 | 7.8758e-7 | 15516  | 10     | null    | 100        | null    | null            |
| ingle.time_values              | ingle.time_values(10...        |           |         |           |                      | 3285f77152d9caa559b4f...      |           |           |           |           |        |        |         |            |         |                 |
| ...                            | ...                            | ...       | ...     | ...       | ...                  | ...                           | ...       | ...       | ...       | ...       | ...    | ...    | ...     | ...        | ...     | ...             |
| benchmarks.time_ranges_multi   | benchmarks.time_ranges_multi(1 | 0.000001  | seconds | rgx1gen11 | rattler-py3.12-numpy | f9ae8b134446c273c0d3eb1e90246 | 0.000001  | 0.000001  | 0.000001  | 0.000001  | 9631   | 10     | null    | null       | 10      | 'arange'        |
|                                | 0, 'arange')                   |           |         |           |                      | ae0d6f99389d06119dfe4...      |           |           |           |           |        |        |         |            |         |                 |
| benchmarks.time_ranges_multi   | benchmarks.time_ranges_multi(1 | 4.3222e-7 | seconds | rgx1gen11 | rattler-py3.12-numpy | f9ae8b134446c273c0d3eb1e90246 | 4.3157e-7 | 4.3557e-7 | 4.3176e-7 | 4.3420e-7 | 20588  | 10     | null    | null       | 100     | 'range'         |
|                                | 00, 'range')                   |           |         |           |                      | ae0d6f99389d06119dfe4...      |           |           |           |           |        |        |         |            |         |                 |
| benchmarks.time_ranges_multi   | benchmarks.time_ranges_multi(1 | 0.000003  | seconds | rgx1gen11 | rattler-py3.12-numpy | f9ae8b134446c273c0d3eb1e90246 | 0.000003  | 0.000003  | 0.000003  | 0.000003  | 3042   | 10     | null    | null       | 100     | 'arange'        |
|                                | 00, 'arange')                  |           |         |           |                      | ae0d6f99389d06119dfe4...      |           |           |           |           |        |        |         |            |         |                 |
| benchmarks.time_sort           | benchmarks.time_sort(10)       | 0.000001  | seconds | rgx1gen11 | rattler-py3.12-numpy | 60785bf757da0254d857b696482db | 0.000001  | 0.000001  | 0.000001  | 0.000001  | 9345   | 10     | null    | null       | 10      | null            |
|                                |                                |           |         |           |                      | 7a25509a5b28a2c9d2a54...      |           |           |           |           |        |        |         |            |         |                 |
| benchmarks.time_sort           | benchmarks.time_sort(100)      | 0.000002  | seconds | rgx1gen11 | rattler-py3.12-numpy | 60785bf757da0254d857b696482db | 0.000002  | 0.000002  | 0.000002  | 0.000002  | 5828   | 10     | null    | null       | 100     | null            |
|                                |                                |           |         |           |                      | 7a25509a5b28a2c9d2a54...      |           |           |           |           |        |        |         |            |         |                 |
```

Without `benchmarks.json`, units and parameter name columns are absent:

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

- **Human-readable units**: Without it, values are shown as raw numbers.
- **Parameter names**: Enables better column labeling in DataFrames.
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
project to be tested installed. For this we will use `micromamba`.

``` sh
micromamba create -p $(pwd)/.tmp_1 -c conda-forge "python==3.8" pip asv numpy
$(pwd)/.tmp_1/bin/pip install .
micromamba create -p $(pwd)/.tmp_2 -c conda-forge "python==3.12" pip asv numpy
$(pwd)/.tmp_2/bin/pip install .
```

Activating the environment is not necessary in this instance, but for more
complex workflows where the installation can be more convoluted, feel free to
work within the environment. Now we can run `asv`.

``` sh
➜ asv run -E existing:$(pwd)/.tmp_2/bin/python --record-samples --bench 'multi' --set-commit-hash "HEAD"
· Discovering benchmarks
· Running 1 total benchmarks (1 commits * 1 environments * 1 benchmarks)
[ 0.00%] · For asv_samples commit d6b286b8 <decorator-params>:
[ 0.00%] ·· Building for existing-py_home_rgoswami_Git_Github_Quansight_asvWork_asv_samples_.tmp_2_bin_python
[ 0.00%] ·· Benchmarking existing-py_home_rgoswami_Git_Github_Quansight_asvWork_asv_samples_.tmp_2_bin_python
[50.00%] ··· Running (benchmarks.time_ranges_multi--).
[100.00%] ··· benchmarks.time_ranges_multi                                                                                                                                                                         ok
[100.00%] ··· ===== =========== =============
              --            func_name
              ----- -------------------------
                n      range        arange
              ===== =========== =============
                10    197±1ns      1.12±0μs
               100   535±0.8ns   3.30±0.03μs
              ===== =========== =============

➜ asv run -E existing:$(pwd)/.tmp_1/bin/python --record-samples --bench 'multi' --set-commit-hash "HEAD"
· Discovering benchmarks
· Running 1 total benchmarks (1 commits * 1 environments * 1 benchmarks)
[ 0.00%] · For asv_samples commit d6b286b8 <decorator-params>:
[ 0.00%] ·· Building for existing-py_home_rgoswami_Git_Github_Quansight_asvWork_asv_samples_.tmp_1_bin_python
[ 0.00%] ·· Benchmarking existing-py_home_rgoswami_Git_Github_Quansight_asvWork_asv_samples_.tmp_1_bin_python
[50.00%] ··· Running (benchmarks.time_ranges_multi--).
[100.00%] ··· benchmarks.time_ranges_multi                                                                                                                                                                         ok
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
asv-spyglass compare .asv/results/rgx1gen11/*.tmp_1* .asv/results/rgx1gen11/*.tmp_2* .asv/results/benchmarks.json
| Change   | Before      | After       |   Ratio | Benchmark (Parameter)                                                                                                                                                                                                                          |
|----------|-------------|-------------|---------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|          | 1.09±0μs    | 1.12±0μs    |    1.03 | benchmarks.time_ranges_multi(10, 'arange') [rgx1gen11/existing-py_home_asv_samples_.tmp_1_bin_python -> rgx1gen11/existing-py_home_asv_samples_.tmp_2_bin_python]  |
| -        | 324±2ns     | 197±1ns     |    0.61 | benchmarks.time_ranges_multi(10, 'range') [rgx1gen11/existing-py_home_asv_samples_.tmp_1_bin_python -> rgx1gen11/existing-py_home_asv_samples_.tmp_2_bin_python]   |
|          | 3.25±0.03μs | 3.30±0.03μs |    1.02 | benchmarks.time_ranges_multi(100, 'arange') [rgx1gen11/existing-py_home_asv_samples_.tmp_1_bin_python -> rgx1gen11/existing-py_home_asv_samples_.tmp_2_bin_python] |
| -        | 729±4ns     | 535±0.8ns   |    0.73 | benchmarks.time_ranges_multi(100, 'range') [rgx1gen11/existing-py_home_asv_samples_.tmp_1_bin_python -> rgx1gen11/existing-py_home_asv_samples_.tmp_2_bin_python]  |
```

The `[machine/env -> machine/env]` suffix can get very wide with long
venv paths. Use `--label-before` / `--label-after` to replace it with
short names, or `--no-env-label` to suppress it entirely:

``` sh
➜ asv-spyglass compare --label-before py38 --label-after py312 \
    .asv/results/rgx1gen11/*.tmp_1* \
    .asv/results/rgx1gen11/*.tmp_2* \
    .asv/results/benchmarks.json

| Change   | Before      | After       |   Ratio | Benchmark (Parameter)                                                         |
|----------|-------------|-------------|---------|-------------------------------------------------------------------------------|
| -        | 157±3ns     | 137±3ns     |    0.87 | benchmarks.TimeSuiteDecoratorSingle.time_keys(10) [py38 -> py312]             |
| -        | 643±2ns     | 543±2ns     |    0.84 | benchmarks.TimeSuiteDecoratorSingle.time_keys(100) [py38 -> py312]            |
| ...      | ...         | ...         |     ... | ...                                                                           |
```

``` sh
➜ asv-spyglass compare --no-env-label \
    .asv/results/rgx1gen11/*.tmp_1* \
    .asv/results/rgx1gen11/*.tmp_2* \
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
