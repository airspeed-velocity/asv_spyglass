import dataclasses
import math
import re
from collections import namedtuple

import polars as pl
from asv_runner.statistics import get_err

ASVResult = namedtuple(
    "ASVResult",
    [
        "key",
        "params",
        "value",
        "stats",
        "samples",
        "version",
        "machine",
        "env_name",
    ],
)


def result_iter(bdot):
    for key in bdot.get_all_result_keys():
        params = bdot.get_result_params(key)
        result_value = bdot.get_result_value(key, params)
        result_stats = bdot.get_result_stats(key, params)
        result_samples = bdot.get_result_samples(key, params)
        result_version = bdot.benchmark_version.get(key)
        yield ASVResult(
            key,
            params,
            result_value,
            result_stats,
            result_samples,
            result_version,
            bdot.params["machine"],
            bdot.env_name,
        )


@dataclasses.dataclass
class PreparedResult:
    """Augmented with information from the benchmarks.json"""

    units: dict
    results: dict
    stats: dict
    versions: dict
    machine_name: str
    env_name: str
    param_names: list

    def __iter__(self):
        for field in dataclasses.fields(self):
            yield getattr(self, field.name)

    def to_df(self):
        """
        Converts a PreparedResult object to a DataFrame, exploding the
        parameters in the keys and flattening the results.
        """

        data = []
        for key, result in self.results.items():
            # Extract benchmark name and parameters
            match = re.match(r"(.+)\((.*)\)", key)
            if match:
                benchmark_name = match.group(1)
                params = match.group(2).split(", ")
            else:
                benchmark_name = key
                params = []

            # Flatten the results tuple
            stats_dict, samples = self.stats[key]
            if stats_dict is None:
                stats_dict_maybe_null = {
                    "ci_99_a": None,
                    "ci_99_b": None,
                    "q_25": None,
                    "q_75": None,
                    "number": None,
                    "repeat": None,
                }
            else:
                stats_dict_maybe_null = stats_dict

            row = {
                "benchmark_base": benchmark_name,
                "name": key,
                "result": result,
                "units": self.units[key],
                "machine": self.machine_name,
                "env": self.env_name,
                "version": self.versions[key],
                **stats_dict_maybe_null,  # Expand the stats dictionary
                "samples": samples,
            }
            # Combine param and parameter name for column names
            row.update(
                dict(
                    zip(
                        [f"param_{name}" for name in self.param_names[key]],
                        params,
                    )
                )
            )
            data.append(row)

        return pl.DataFrame(data)


class ASVBench:
    def __init__(self, benchname: str, pr: PreparedResult):
        self.name = benchname
        self._pr = pr
        self.time = pr.results.get(self.name, math.nan)
        self.stats = pr.stats.get(self.name, (None,))
        self.err = None
        if self.name in pr.stats.keys() and self.stats[0]:
            self.err = get_err(self.time, self.stats[0])
        self.version = pr.versions.get(self.name)
        self.unit = pr.units.get(self.name)
