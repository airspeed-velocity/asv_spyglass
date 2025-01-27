import pprint as pp

from approvaltests.approvals import verify

from asv_spyglass._asv_ro import ReadOnlyASVBenchmarks


def test_ro_benchmarks(shared_datadir):
    benchmarks = ReadOnlyASVBenchmarks(
        shared_datadir / "d6b286b8_asv_samples_benchmarks.json"
    )
    verify(pp.pformat(benchmarks))


def test_ro_benchmarks_filter(shared_datadir):
    benchmarks = ReadOnlyASVBenchmarks(
        shared_datadir / "d6b286b8_asv_samples_benchmarks.json", "multi"
    )
    verify(pp.pformat(benchmarks))
