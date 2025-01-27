from pathlib import Path

from asv import results
from asv.commands.compare import _is_result_better, _isna, unroll_result
from asv.util import human_value
from asv_runner.console import color_print
import polars as pl

from asv_spyglass._asv_ro import ReadOnlyASVBenchmarks
from asv_spyglass._num import Ratio
from asv_spyglass.changes import (
    ASVChangeInfo,
    Better,
    Failure,
    Fixed,
    Incomparable,
    NoChange,
    Worse,
    ResultMark,
)
from asv_spyglass.results import ASVBench, PreparedResult, result_iter


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

    def prepare(self, result_data):
        """
        Processes result data and returns extracted information.

        Args:
            result_data: Result data to be processed.

        Returns:
            tuple: A tuple containing units, results, stats, versions,
                   and the machine/environment name.
        """
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
            machine_env_name = f"{machine}/{env_name}"
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

    # Extract data
    mname_1 = f"{pr1.machine_name}/{pr1.env_name}"
    mname_2 = f"{pr2.machine_name}/{pr2.env_name}"
    machine_env_names = {mname_1, mname_2}

    # Create a list to collect data for the DataFrame
    data = []

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
            benchmark_name = f"{benchmark} [{mname_1} -> {mname_2}]"
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
                "unit": asv1.unit or asv2.unit,
                "color": diffinfo.color.name.lower(),
                "state": diffinfo.state,
            }
        )

    # Create a Polars DataFrame
    df = pl.DataFrame(data)

    # Sort the DataFrame
    if sort == "ratio":
        df = df.sort("ratio", descending=True)
    elif sort == "name":
        df = df.sort("benchmark")

    # Get commit names or use empty strings
    name_1 = ""  # commit_names.get(hash_1, "")
    name_2 = ""  # commit_names.get(hash_2, "")
    name_1 = f"<{name_1}>" if name_1 else ""
    name_2 = f"<{name_2}>" if name_2 else ""

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

        if not filtered_df.is_empty():
            table_data = []
            for row in filtered_df.rows():
                table_data.append(
                    [
                        str(row[1]),  # mark (convert to string)
                        human_value(row[2], row[8], err=row[6]),  # before
                        human_value(row[3], row[8], err=row[7]),  # after
                        str(Ratio(row[2], row[3])),  # ratio
                        row[0],  # benchmark
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
