from pathlib import Path

import click
import polars as pl
from asv import results
from rich import box
from rich.console import Console
from rich.table import Table
from rich_click import RichCommand, RichGroup

from asv_spyglass._asv_ro import ReadOnlyASVBenchmarks
from asv_spyglass.changes import ResultMark
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
def compare(b1, b2, bconf, factor, split, only_changed, sort):
    """
    Compare two ASV result files.
    """
    all_tables = do_compare(b1, b2, bconf, factor, split, only_changed, sort)

    console = Console()

    for key, table_data in all_tables.items():
        if not only_changed:
            console.print("")
            console.print(table_data["title"], style="bold")
            console.print("")

        table = Table(
            title=table_data["title"],
            show_header=True,
            header_style="bold magenta",
            box=box.SIMPLE,
        )

        for header in table_data["headers"]:
            table.add_column(
                header, justify="right" if header != "Benchmark (Parameter)" else "left"
            )

        for row in table_data["table_data"]:
            change_mark = row[0]
            row_style = ""

            # Determine row style based on change_mark
            if change_mark == ResultMark.BETTER:
                row_style = "green"
            elif change_mark == ResultMark.WORSE:
                row_style = "red"
            elif change_mark == ResultMark.FAILURE:
                row_style = "red"
            elif change_mark == ResultMark.FIXED:
                row_style = "green"
            elif change_mark == ResultMark.INCOMPARABLE:
                row_style = "light_grey"
            elif change_mark == ResultMark.UNCHANGED:
                row_style = "white"
            elif change_mark == ResultMark.INSIGNIFICANT:
                row_style = "white"

            table.add_row(*row, style=row_style)

        console.print(table)

        # Print summary of worsened/improved status
        if not split:
            if (av_x := sum([x.value for x in table_data["states"]])) > 0:
                console.print("[bold green]Net Improvement![/]")
            elif av_x < 0:
                console.print("[bold red]Net Regression![/]")


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
