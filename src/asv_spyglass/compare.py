from pathlib import Path

import polars as pl
# TODO - Add typing to `asv`
from asv import results  # type: ignore[import-untyped]
from asv.commands.compare import _is_result_better, _isna, unroll_result  # type: ignore[import-untyped]
from asv.util import human_value  # type: ignore[import-untyped]

from asv_spyglass._asv_ro import ReadOnlyASVBenchmarks
from asv_spyglass._num import Ratio
from asv_spyglass.changes import (
    ASVChangeInfo,
    Better,
    Failure,
    Fixed,
    Incomparable,
    NoChange,
    ResultMark,
    Worse,
)
from asv_spyglass.results import ASVBench, PreparedResult, result_iter


# TODO - Again, instead of having a class with a single method, this could be
#        simplified to a function, to reduce the risk of breaking things by
#        misconfiguring instance state.
#        So it could be:
#        ```py
#        prepared_results = prepare_results(benchmarks, result_data)
#        ```
class ResultPreparer:
    """
    Prepares benchmark results for comparison by extracting relevant data
    like units, values, stats, versions, and machine/environment names.
    """

    def __init__(self, benchmarks):
        """
        Initializes ResultPreparer with benchmark data.

        Args:
            benchmarks: Benchmark data used for extracting units.
        """
        self.benchmarks = benchmarks

    # TODO - What is the shape of result_data?
    def prepare(self, result_data):
        """
        Processes result data and returns extracted information.

        Args:
            result_data: Result data to be processed.

        Returns:
            tuple: A tuple containing units, results, stats, versions,
                   and the machine/environment name.
        """
        # TODO - set type hints for these
        units = {}
        results = {}
        ss = {}
        versions = {}
        param_names = {}
        btype = {}
        machine_env_name = None

        for (
            key,
            params,
            value,
            stats,
            samples,
            version,
            machine,
            env_name,
        ) in result_iter(result_data):
            if machine_env_name is None:
                machine_env_name = f"{machine}/{env_name}"

            # TODO - Add type hints to unroll_result
            for name, value, stats, samples in unroll_result(
                key, params, value, stats, samples
            ):
                results[name] = value
                # TODO(hz): Split samples out later when _is_result_better is
                # not used anymore, currently in a tuple for ASV compatibility
                ss[name] = (stats, samples)
                versions[name] = version
                # HACK(hz): The names already include the parameters i.e.
                # benchmark(param) so this works around the situation
                bench_key = [x for x in self.benchmarks.keys() if key in x][0]
                units[name] = self.benchmarks.get(bench_key, {}).get("unit")
                btype[name] = self.benchmarks.get(bench_key, {}).get("type")
                param_names[name] = self.benchmarks.get(bench_key, {}).get(
                    "param_names"
                )

        # TODO - CHECK that result_data is not empty, otherwise this will throw
        machine, env_name = machine_env_name.split("/")

        return PreparedResult(
            units=units,
            results=results,
            stats=ss,
            versions=versions,
            machine_name=machine,
            env_name=env_name,
            param_names=param_names,
        )


def _get_change_info(
    asv1: ASVBench, asv2: ASVBench, factor, use_stats
) -> ASVChangeInfo:
    if (
        asv1.version is not None
        and asv2.version is not None
        and asv1.version != asv2.version
    ):
        # not comparable
        return Incomparable()
    elif asv1.time is not None and asv2.time is None:
        # introduced a failure
        return Failure()
    elif asv1.time is None and asv2.time is not None:
        # fixed a failure
        return Fixed()
    elif asv1.time is None and asv2.time is None:
        # both failed
        return NoChange()
    elif _isna(asv1.time) or _isna(asv2.time):
        # either one was skipped
        return NoChange()
    elif _is_result_better(
        asv2.time,
        asv1.time,
        asv2.stats_n_samples,
        asv1.stats_n_samples,
        factor,
        use_stats=use_stats,
    ):
        return Better()
    elif _is_result_better(
        asv1.time,
        asv2.time,
        asv1.stats_n_samples,
        asv2.stats_n_samples,
        factor,
        use_stats=use_stats,
    ):
        return Worse()
    else:
        return NoChange()


def _create_comparison_dataframe(
    pr1: PreparedResult,
    pr2: PreparedResult,
    factor: float,
    only_changed: bool,
    use_stats: bool,
):
    """
    Creates a Polars DataFrame comparing results from two PreparedResult objects.

    Args:
        pr1 (PreparedResult): The first PreparedResult object.
        pr2 (PreparedResult): The second PreparedResult object.
        factor (float): The factor used for determining significance.
        only_changed (bool): Whether to only include changed benchmarks.
        use_stats (bool): Whether to use statistical significance.

    Returns:
        pl.DataFrame: A DataFrame with comparison data.
    """
    data = []
    machine_env_names = {
        f"{pr1.machine_name}/{pr1.env_name}",
        f"{pr2.machine_name}/{pr2.env_name}",
    }

    for benchmark in sorted(set(pr1.results.keys()) | set(pr2.results.keys())):
        asv1 = ASVBench(benchmark, pr1)
        asv2 = ASVBench(benchmark, pr2)

        ratio = Ratio(asv1.time, asv2.time)
        diffinfo = _get_change_info(
            asv1,
            asv2,
            factor,
            use_stats,
        )

        if isinstance(diffinfo, NoChange):
            # Mark statistically insignificant results
            if _is_result_better(
                asv1.time, asv2.time, None, None, factor
            ) or _is_result_better(asv2.time, asv1.time, None, None, factor):
                ratio.is_insignificant = True

        if only_changed and diffinfo.mark in (
            ResultMark.UNCHANGED,
            ResultMark.INCOMPARABLE,
            ResultMark.FIXED,
        ):
            continue

        # Determine benchmark name format
        if len(machine_env_names) > 1:
            benchmark_name = (
                f"{benchmark} [{pr1.machine_name}/{pr1.env_name}"
                f" -> {pr2.machine_name}/{pr2.env_name}]"
            )
        else:
            benchmark_name = benchmark

        assert asv1.unit == asv2.unit, "Units for benchmark must match"

        data.append(
            {
                "benchmark": benchmark_name,
                "mark": diffinfo.mark,
                "before": asv1.time,
                "after": asv2.time,
                "ratio": ratio.val,
                "is_insignificant": ratio.is_insignificant,
                "err_before": asv1.err,
                "err_after": asv2.err,
                "unit": asv1.unit or asv2.unit,  # Use unit from asv1 or asv2
                "color": diffinfo.color.name.lower(),
                "state": diffinfo.state,
            }
        )

    return pl.DataFrame(data)


def _format_comparison_tables(
    df: pl.DataFrame, sort: str, name_1: str, name_2: str, split: bool
):
    """
    Formats a comparison DataFrame into tables for display.

    Args:
        df (pl.DataFrame): The comparison DataFrame.
        sort (str): The sorting method ("ratio" or "name").
        name_1 (str): The name of the first commit/result.
        name_2 (str): The name of the second commit/result.

    Returns:
        dict: A dictionary of formatted tables.
    """

    # Sort the DataFrame
    if sort == "ratio":
        df = df.sort("ratio", descending=True)
    elif sort == "name":
        df = df.sort("benchmark")

    # Construct the table data for each category
    all_tables = {}

    if split:
        colors = ["green", "default", "red", "lightgrey"]
    else:
        colors = ["all"]
        df = df.with_columns(pl.lit("all").alias("color"))

    for color in colors:
        if color != "all":
            filtered_df = df.filter(pl.col("color") == color)
        else:
            filtered_df = df

        if filtered_df.is_empty():
            continue

        table_data = []
        for row in filtered_df.iter_rows(named=True):
            table_data.append(
                [
                    str(row["mark"]),
                    human_value(row["before"], row["unit"], err=row["err_before"]),
                    human_value(row["after"], row["unit"], err=row["err_after"]),
                    str(Ratio(row["before"], row["after"])),
                    row["benchmark"],
                ]
            )

        if color == "all":
            title = "All benchmarks:"
        else:
            title = {
                "green": "Benchmarks that have improved:",
                "default": "Benchmarks that have stayed the same:",
                "red": "Benchmarks that have got worse:",
                "lightgrey": "Benchmarks that are not comparable:",
            }[color]

        all_tables[color] = {
            "title": title,
            "headers": [
                "Change",
                f"Before {name_1}",
                f"After {name_2}",
                "Ratio",
                "Benchmark (Parameter)",
            ],
            "table_data": table_data,
            "states": filtered_df.select(pl.col("state")).to_series().to_list(),
        }

    return all_tables


def do_compare(
    b1,
    b2,
    bdat,
    factor=1.1,
    split=False,
    only_changed=False,
    sort="default",
    machine=None,
    env_spec=None,
    use_stats=True,
):
    # Load results
    res_1 = results.Results.load(b1)
    res_2 = results.Results.load(b2)

    # Initialize benchmarks
    benchmarks = ReadOnlyASVBenchmarks(Path(bdat)).benchmarks

    # Prepare results
    preparer = ResultPreparer(benchmarks)
    pr1 = preparer.prepare(res_1)
    pr2 = preparer.prepare(res_2)

    # Create the comparison DataFrame
    df = _create_comparison_dataframe(pr1, pr2, factor, only_changed, use_stats)

    # Get commit names or use empty strings
    name_1 = ""  # commit_names.get(hash_1, "")
    name_2 = ""  # commit_names.get(hash_2, "")
    name_1 = f"<{name_1}>" if name_1 else ""
    name_2 = f"<{name_2}>" if name_2 else ""

    # Format the DataFrame into tables
    all_tables = _format_comparison_tables(df, sort, name_1, name_2, split)

    return all_tables
