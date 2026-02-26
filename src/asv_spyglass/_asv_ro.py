import itertools
import re
from pathlib import Path

from asv.util import load_json as asv_json_load  # type: ignore[import-untyped]

from asv_spyglass._aux import getstrform


class ReadOnlyASVBenchmarks:
    """Read-only holder for a set of ASV benchmarks."""

    api_version = 2

    def __init__(
        self, benchmarks_file: Path | None, regex: str | list[str] | None = None
    ):
        """Load benchmarks from a JSON file, optionally filtering by regex."""
        self._base_benchmarks = {}  # Store all benchmarks here
        self._benchmark_selection: dict[str, list[int]] = {}
        self.filtered_benchmarks = {}  # Store selected benchmarks here after parameter expansion

        if benchmarks_file is None:
            return

        d = asv_json_load(getstrform(benchmarks_file), api_version=self.api_version)

        if not regex:
            regex = []
        if isinstance(regex, str):
            regex = [regex]

        for benchmark in d.values():
            self._base_benchmarks[benchmark["name"]] = benchmark
            if benchmark.get("params"):
                self._benchmark_selection[benchmark["name"]] = []
                param_tuples = [tuple(map(str, p)) for p in benchmark["params"]]
                for idx, param_set in enumerate(itertools.product(*param_tuples)):
                    name = f"{benchmark['name']}({', '.join(param_set)})"
                    if not regex or any(re.search(reg, name) for reg in regex):
                        self.filtered_benchmarks[name] = (
                            benchmark  # Store with full name
                        )
                        self._benchmark_selection[benchmark["name"]].append(idx)
            else:
                self._benchmark_selection[benchmark["name"]] = []
                if not regex or any(re.search(reg, benchmark["name"]) for reg in regex):
                    self.filtered_benchmarks[benchmark["name"]] = benchmark

    def __repr__(self) -> str:
        """Return a string representation of the filtered benchmarks."""
        import pprint

        pp = pprint.PrettyPrinter()
        return pp.pformat(self.filtered_benchmarks)

    @property
    def benchmarks(self) -> dict[str, dict]:
        """Get a dictionary of filtered benchmarks."""
        return self.filtered_benchmarks
