import pprint as pp

from approvaltests.approvals import verify
from asv import results

from asv_spyglass._asv_ro import ReadOnlyASVBenchmarks
from asv_spyglass._aux import getstrform
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
