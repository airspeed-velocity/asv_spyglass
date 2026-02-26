import sys
from pathlib import Path

import click
import polars as pl
import rich_click
from asv import results

from asv_spyglass._asv_ro import ReadOnlyASVBenchmarks
from asv_spyglass.compare import ResultPreparer, do_compare

rich_click.rich_click.USE_RICH_MARKUP = True
rich_click.rich_click.SHOW_ARGUMENTS = True
rich_click.rich_click.GROUP_ARGUMENTS_OPTIONS = True


def _resolve_bconf(result_path: str, bconf: str | None) -> str | None:
    """Auto-search for benchmarks.json when not explicitly provided."""
    if bconf:
        return bconf
    bconf_path = Path(result_path).parent.parent / "benchmarks.json"
    if bconf_path.exists():
        return str(bconf_path)
    return None


@click.group(cls=rich_click.RichGroup)
def cli():
    """ASV benchmark analysis tool."""
    pass


@cli.command(cls=rich_click.RichCommand)
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
    """Compare two ASV result files.

    B1 and B2 are paths to ASV result JSON files.
    BCONF is an optional path to the benchmarks.json metadata file.
    If BCONF is not provided, it is searched for in the parent directory of B1.
    If still not found, comparisons proceed without extra metadata (units, etc).
    """
    if only_improved and only_regressed:
        raise click.UsageError(
            "--only-improved and --only-regressed are mutually exclusive."
        )
    bconf = _resolve_bconf(b1, bconf)

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


@cli.command(cls=rich_click.RichCommand)
@click.argument("bres", type=click.Path(exists=True), required=True)
@click.argument("bdat", type=click.Path(exists=True), required=False)
@click.option(
    "--csv",
    type=click.Path(),
    help="Save data to csv",
)
def to_df(bres, bdat, csv):
    """Generate a dataframe from an ASV result file.

    BRES is the path to an ASV result JSON file.
    BDAT is an optional path to the benchmarks.json metadata file.
    If BDAT is not provided, it is searched for in the parent directory of BRES.
    If still not found, results are displayed without extra metadata (units, etc).
    """
    res = results.Results.load(bres)
    bdat = _resolve_bconf(bres, bdat)
    bdat_path = Path(bdat) if bdat else None
    benchdat = ReadOnlyASVBenchmarks(bdat_path).benchmarks
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


if __name__ == "__main__":
    cli()
