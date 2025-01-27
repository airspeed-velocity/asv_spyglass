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
    verify(
        pp.pformat(
            do_compare(
                getstrform(shared_datadir / "a0f29428-conda-py3.11-numpy.json"),
                getstrform(shared_datadir / "a0f29428-virtualenv-py3.12-numpy.json"),
                shared_datadir / "asv_samples_a0f29428_benchmarks.json",
            )
        )
    )


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
