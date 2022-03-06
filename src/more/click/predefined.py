import click as _click

import codefresh.slugify as slugify


def output(varname="output", default="text"):
    return _click.option(
        "-o",
        "--output",
        slugify.for_identifier(varname),
        type=_click.Choice(["text", "json", "tsv", "yaml"]),
        default=default,
        help="Use alternative output format",
    )
