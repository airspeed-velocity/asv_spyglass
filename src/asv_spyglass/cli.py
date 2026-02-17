from pathlib import Path

import click
import polars as pl
from asv import results

from asv_spyglass._asv_ro import ReadOnlyASVBenchmarks
from asv_spyglass.compare import ResultPreparer, do_compare


@click.group()
def cli():
    """
    Command-line interface for ASV benchmark analysis.
    """
    pass


@cli.command()
@click.argument("b1", type=click.Path(exists=True), required=True)
@click.argument("b2", type=click.Path(exists=True), required=True)
@click.argument("bconf", type=click.Path(exists=True), required=False)
@click.option(
    "--factor",
    default=1.1,
    show_default=True,
    help="Factor for determining significant changes.",
)
@click.option(
    "--split",
    is_flag=True,
    help="Split output by improvement/regression.",
)
@click.option(
    "--only-changed",
    is_flag=True,
    help="Only show changed benchmarks.",
)
@click.option(
    "--sort",
    type=click.Choice(["default", "ratio", "name"]),
    default="default",
    show_default=True,
    help="Sort output by change, ratio, or name.",
)
@click.option(
    "--label-before",
    default=None,
    help="Custom label for the 'before' environment.",
)
@click.option(
    "--label-after",
    default=None,
    help="Custom label for the 'after' environment.",
)
@click.option(
    "--no-env-label",
    is_flag=True,
    help="Suppress the [machine/env -> machine/env] suffix.",
)
@click.option(
    "--only-improved",
    is_flag=True,
    help="Only show improved benchmarks.",
)
@click.option(
    "--only-regressed",
    is_flag=True,
    help="Only show regressed benchmarks.",
)
def compare(
    b1,
    b2,
    bconf,
    factor,
    split,
    only_changed,
    sort,
    label_before,
    label_after,
    no_env_label,
    only_improved,
    only_regressed,
):
    """
    Compare two ASV result files.
    """
    if only_improved and only_regressed:
        raise click.UsageError(
            "--only-improved and --only-regressed are mutually exclusive."
        )
    if not bconf:
        bconf_path = Path(b1).parent.parent / "benchmarks.json"
        if bconf_path.exists():
            bconf = str(bconf_path)
        else:
            raise click.UsageError(
                "Error: Missing argument 'BCONF'. "
                "Could not find 'benchmarks.json' "
                "automatically. Please provide the "
                "path to your benchmarks.json file."
            )

    import sys

    output, worsened, _ = do_compare(
        b1,
        b2,
        bconf,
        factor,
        split,
        only_changed,
        sort,
        label_before=label_before,
        label_after=label_after,
        no_env_label=no_env_label,
        only_improved=only_improved,
        only_regressed=only_regressed,
    )
    print(output)
    if worsened:
        sys.exit(1)


@cli.command()
@click.argument("bres", type=click.Path(exists=True), required=True)
@click.argument("bdat", type=click.Path(exists=True), required=True)
@click.option(
    "--csv",
    type=click.Path(),
    help="Save data to csv",
)
def to_df(bres, bdat, csv):
    """
    Generate a dataframe from an ASV result file.
    """
    res = results.Results.load(bres)
    benchdat = ReadOnlyASVBenchmarks(Path(bdat)).benchmarks
    preparer = ResultPreparer(benchdat)
    df = preparer.prepare(res).to_df()
    if csv:
        df.write_csv(csv)
    else:
        with pl.Config(
            tbl_formatting="ASCII_MARKDOWN",
            tbl_hide_column_data_types=True,
            fmt_str_lengths=50,
            tbl_cols=50,
        ):
            click.echo(df)
