from pathlib import Path

import click
from rich_click import RichCommand, RichGroup
import polars as pl
from asv import results

from asv_spyglass._asv_ro import ReadOnlyASVBenchmarks
from asv_spyglass._aux import getstrform
from asv_spyglass.compare import ResultPreparer, do_compare


@click.group(cls=RichGroup)
def cli():
    """
    Command-line interface for ASV benchmark analysis.
    """
    pass


@cli.command(cls=RichCommand)
@click.argument("b1", type=click.Path(exists=True), required=True)
@click.argument("b2", type=click.Path(exists=True), required=True)
@click.argument("bconf", type=click.Path(exists=True), required=True)
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
def compare(b1, b2, bconf, factor, split, only_changed, sort):  # Renamed to 'compare'
    """
    Compare two ASV result files.
    """
    print(do_compare(b1, b2, bconf, factor, split, only_changed, sort))


@cli.command(cls=RichCommand)
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
        df.to_csv(csv)
    else:
        with pl.Config(
            tbl_formatting="ASCII_MARKDOWN",
            tbl_hide_column_data_types=True,
            fmt_str_lengths=50,
            tbl_cols=50,
        ):
            click.echo(df)
