import pprint as pp
import shutil

from approvaltests.approvals import verify
from asv import results
from click.testing import CliRunner

from asv_spyglass._asv_ro import ReadOnlyASVBenchmarks
from asv_spyglass._aux import getstrform
from asv_spyglass.cli import cli
from asv_spyglass.compare import (
    ResultPreparer,
    do_compare,
    result_iter,
)


def test_result_iter(shared_datadir):
    res = results.Results.load(
        getstrform(shared_datadir / "a0f29428-conda-py3.11-numpy.json")
    )
    verify(pp.pformat([tuple(x) for x in (result_iter(res))]))


def test_do_compare(shared_datadir):
    output, _, _ = do_compare(
        getstrform(shared_datadir / "a0f29428-conda-py3.11-numpy.json"),
        getstrform(shared_datadir / "a0f29428-virtualenv-py3.12-numpy.json"),
        shared_datadir / "asv_samples_a0f29428_benchmarks.json",
    )
    verify(output)


def test_do_compare_no_bconf(shared_datadir):
    """do_compare works without benchmarks.json (GH-8)."""
    output, _, _ = do_compare(
        getstrform(shared_datadir / "a0f29428-conda-py3.11-numpy.json"),
        getstrform(shared_datadir / "a0f29428-virtualenv-py3.12-numpy.json"),
        benchmarks_path=None,
    )
    assert "benchmarks.TimeSuite.time_add_arr" in output
    assert "0.3" in output  # Ratio


def test_do_compare_split(shared_datadir):
    """--split returns all non-empty sections (GH-13)."""
    result, _, _ = do_compare(
        getstrform(shared_datadir / "d6b286b8-virtualenv-py3.12-numpy.json"),
        getstrform(shared_datadir / "d6b286b8-rattler-py3.12-numpy.json"),
        shared_datadir / "d6b286b8_asv_samples_benchmarks.json",
        split=True,
    )
    verify(result)


def test_do_compare_custom_labels(shared_datadir):
    """--label-before/--label-after replace env suffix (GH-12)."""
    result, _, _ = do_compare(
        getstrform(shared_datadir / "d6b286b8-virtualenv-py3.12-numpy.json"),
        getstrform(shared_datadir / "d6b286b8-rattler-py3.12-numpy.json"),
        shared_datadir / "d6b286b8_asv_samples_benchmarks.json",
        label_before="main",
        label_after="pr",
    )
    assert "[main -> pr]" in result
    assert "virtualenv" not in result
    assert "rattler" not in result


def test_do_compare_no_env_label(shared_datadir):
    """--no-env-label suppresses env suffix entirely (GH-12)."""
    result, _, _ = do_compare(
        getstrform(shared_datadir / "d6b286b8-virtualenv-py3.12-numpy.json"),
        getstrform(shared_datadir / "d6b286b8-rattler-py3.12-numpy.json"),
        shared_datadir / "d6b286b8_asv_samples_benchmarks.json",
        no_env_label=True,
    )
    assert "[" not in result
    assert "->" not in result


def test_do_compare_worsened_flag(shared_datadir):
    """do_compare returns worsened=True when regressions exist."""
    _, worsened, improved = do_compare(
        getstrform(shared_datadir / "d6b286b8-virtualenv-py3.12-numpy.json"),
        getstrform(shared_datadir / "d6b286b8-rattler-py3.12-numpy.json"),
        shared_datadir / "d6b286b8_asv_samples_benchmarks.json",
    )
    assert worsened is True
    assert improved is True


def test_do_compare_only_improved(shared_datadir):
    """--only-improved filters to green results only."""
    result, _, _ = do_compare(
        getstrform(shared_datadir / "d6b286b8-virtualenv-py3.12-numpy.json"),
        getstrform(shared_datadir / "d6b286b8-rattler-py3.12-numpy.json"),
        shared_datadir / "d6b286b8_asv_samples_benchmarks.json",
        only_improved=True,
    )
    assert result.strip()
    # Should not contain any "+" (worsened) markers
    for line in result.splitlines():
        if line.startswith("|"):
            assert "| + " not in line


def test_do_compare_only_regressed(shared_datadir):
    """--only-regressed filters to red results only."""
    result, _, _ = do_compare(
        getstrform(shared_datadir / "d6b286b8-virtualenv-py3.12-numpy.json"),
        getstrform(shared_datadir / "d6b286b8-rattler-py3.12-numpy.json"),
        shared_datadir / "d6b286b8_asv_samples_benchmarks.json",
        only_regressed=True,
    )
    assert result.strip()
    # Should not contain any "-" (improved) markers
    for line in result.splitlines():
        if line.startswith("|"):
            assert "| - " not in line


def test_result_df(shared_datadir):
    res = results.Results.load(
        getstrform(shared_datadir / "d6b286b8-rattler-py3.12-numpy.json")
    )
    benchdat = ReadOnlyASVBenchmarks(
        shared_datadir / "d6b286b8_asv_samples_benchmarks.json"
    ).benchmarks
    preparer = ResultPreparer(benchdat)
    pres1 = preparer.prepare(res).to_df()
    verify(pp.pformat(pres1.to_dict()))


def test_result_df_no_bconf(shared_datadir):
    """ResultPreparer.to_df works without benchmarks.json (GH-8)."""
    res = results.Results.load(
        getstrform(shared_datadir / "a0f29428-conda-py3.11-numpy.json")
    )
    benchmarks = ReadOnlyASVBenchmarks(None).benchmarks
    preparer = ResultPreparer(benchmarks)
    df = preparer.prepare(res).to_df()
    assert "benchmark_base" in df.columns
    assert "name" in df.columns
    assert df["benchmark_base"][0] == "benchmarks.TimeSuite.time_add_arr"


def test_to_df_auto_search(shared_datadir, tmp_path):
    """to-df auto-discovers benchmarks.json in parent dir (GH-8)."""
    # Set up .asv/results/<machine>/<result>.json layout
    machine_dir = tmp_path / "results" / "machine1"
    machine_dir.mkdir(parents=True)
    result_file = shared_datadir / "d6b286b8-rattler-py3.12-numpy.json"
    shutil.copy(result_file, machine_dir / result_file.name)
    benchmarks_file = shared_datadir / "d6b286b8_asv_samples_benchmarks.json"
    shutil.copy(benchmarks_file, tmp_path / "results" / "benchmarks.json")

    runner = CliRunner()
    result = runner.invoke(cli, ["to-df", str(machine_dir / result_file.name)])
    assert result.exit_code == 0
    # 17 columns = benchmarks.json was auto-discovered (without it: 12)
    assert "shape: (16, 17)" in result.output
    assert "sec" in result.output  # units from benchmarks.json
