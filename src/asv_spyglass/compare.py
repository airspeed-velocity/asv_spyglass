from pathlib import Path

from asv import results
from asv.commands.compare import _is_result_better, _isna, unroll_result
from asv.util import human_value
from asv_runner.console import color_print

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

    # Prepare results using the ResultPreparer class
    preparer = ResultPreparer(benchmarks)
    pr1 = preparer.prepare(res_1)
    pr2 = preparer.prepare(res_2)

    # Extract data from prepared results
    machine_env_names = set()
    mname_1 = f"{pr1.machine_name}/{pr1.env_name}"
    mname_2 = f"{pr2.machine_name}/{pr2.env_name}"
    machine_env_names.add(mname_1)
    machine_env_names.add(mname_2)

    benchmarks_1 = set(pr1.results.keys())
    benchmarks_2 = set(pr2.results.keys())
    joint_benchmarks = sorted(list(benchmarks_1 | benchmarks_2))
    bench = {}

    if split:
        bench["green"] = []
        bench["red"] = []
        bench["lightgrey"] = []
        bench["default"] = []
    else:
        bench["all"] = []

    states = []
    for benchmark in joint_benchmarks:
        asv1 = ASVBench(benchmark, pr1)
        asv2 = ASVBench(benchmark, pr2)

        ratio = Ratio(asv1.time, asv2.time)
        diffinfo = _get_change_info(
            asv1,
            asv2,
            factor,
            use_stats,
        )
        states.append(diffinfo.state)

        if isinstance(diffinfo, NoChange):
            # Mark statistically insignificant results
            if _is_result_better(
                asv1.time, asv2.time, None, None, factor
            ) or _is_result_better(asv2.time, asv1.time, None, None, factor):
                ratio.is_insignificant = True

        if only_changed and diffinfo.mark.value in (" ", "x", "*"):
            continue

        details = (
            f"{diffinfo.mark:1s} "
            f"{human_value(asv1.time, asv1.unit, err=asv1.err):>15s} "
            f"{human_value(asv2.time, asv2.unit, err=asv2.err):>15s} "
            f"{str(ratio):>8s} "
        )
        split_line = details.split()
        if len(machine_env_names) > 1:
            benchmark_name = f"{benchmark} [{mname_1} -> {mname_2}]"
        else:
            benchmark_name = benchmark
        if len(split_line) == 4:
            split_line += [benchmark_name]
        else:
            split_line = [" "] + split_line + [benchmark_name]
        if split:
            bench[diffinfo.color].append(split_line)
        else:
            bench["all"].append(split_line)

    if split:
        keys = ["green", "default", "red", "lightgrey"]
    else:
        keys = ["all"]

    titles = {}
    titles["green"] = "Benchmarks that have improved:"
    titles["default"] = "Benchmarks that have stayed the same:"
    titles["red"] = "Benchmarks that have got worse:"
    titles["lightgrey"] = "Benchmarks that are not comparable:"
    titles["all"] = "All benchmarks:"

    all_tables = {}  # Dictionary to hold tables for each key

    for key in keys:
        if len(bench[key]) == 0:
            continue

        if not only_changed:
            color_print("")
            color_print(titles[key])
            color_print("")

        name_1 = False  # commit_names.get(hash_1)
        if name_1:
            name_1 = f"<{name_1}>"
        else:
            name_1 = ""

        name_2 = False  # commit_names.get(hash_2)
        if name_2:
            name_2 = f"<{name_2}>"
        else:
            name_2 = ""

        if sort == "default":
            pass
        elif sort == "ratio":
            bench[key].sort(key=lambda v: v[3], reverse=True)
        elif sort == "name":
            bench[key].sort(key=lambda v: v[2])
        else:
            raise ValueError("Unknown 'sort'")

        print(states)
        table_data = [
            [
                row[0],  # Change mark
                row[1],  # Before
                row[2],  # After
                row[3],  # Ratio
                row[4],  # Benchmark name
            ]
            for row in bench[key]
        ]

        all_tables[key] = {
            "title": titles[key],
            "headers": [
                "Change",
                f"Before {name_1}",
                f"After {name_2}",
                "Ratio",
                "Benchmark (Parameter)",
            ],
            "table_data": table_data,
            "states": states,
        }

    return all_tables
