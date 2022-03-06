import collections as std
import operator
import shutil

import click as _click
from clickclick import OutputFormat
from clickclick.console import print_table

OVERFLOW_COLUMN = "..."


class Table:
    def __init__(self, rows=None):
        self.rows = [] if rows is None else rows

    def add(self, **kwargs):
        self.rows.append(kwargs)

    def extend(self, gen):
        self.rows.extend([x for x in gen if isinstance(x, std.Mapping)])

    def push(self, data):
        if not isinstance(data, std.Mapping):
            raise ValueError("dataneeds to be a dict-like value")
        self.rows.append(data)

    def show(
        self, widths=None, fields=None, resize_fields=None, show_overflow=True, show_footer=True
    ):
        if not any([self.rows, widths, fields]):
            raise Exception("No field data")

        if widths is None:
            widths = {k: len(k) for k in self.rows[0].keys()}
            for r in self.rows:
                for k, v in r.items():
                    widths[k] = max(widths[k], len(str(v)))

        if resize_fields:
            resize_fields = ensure_list(resize_fields)
            for x in resize_fields:
                widths[x] = -1

        max_width = adjust_column_widths(widths, use_full_width=show_overflow)

        if fields is None:
            if widths:
                fields = list(widths.keys())
            else:
                fields = list(self.rows[0].keys())

        with OutputFormat("text"):
            print_table(fields, self.rows, max_column_widths=widths)
            if show_footer:
                _click.secho(" " * max_width, fg="black", bg="white")


def ensure_list(x):
    if not isinstance(x, list):
        return [x]
    return x


def get_terminal_size(columns=None, lines=None):
    return shutil.get_terminal_size(fallback=(columns or 80, lines or 24))


def adjust_column_widths(widths, use_full_width=False):
    num_columns = len(widths)
    allocated = sum(x for x in widths.values() if x > 0)
    num_to_fix = len([1 for x in widths.values() if x <= 0])

    if use_full_width and num_to_fix == 0:
        widths[OVERFLOW_COLUMN] = 0
        num_columns += 1
        num_to_fix += 1

    max_width, _ = get_terminal_size()

    if num_to_fix != 0:

        used = allocated + num_columns

        remaining = max_width - used
        per_column = int(remaining / num_to_fix)

        for k, v in widths.items():
            if v <= 0:
                widths[k] = per_column

        widths[k] += remaining - int(per_column * num_to_fix)
    else:
        allocated = sum(x for x in widths.values() if x > 0)
        overflow = allocated + num_columns - max_width
        if overflow > 0:
            biggest = max(widths.items(), key=operator.itemgetter(1))[0]
            widths[biggest] -= overflow

    if OVERFLOW_COLUMN in widths:
        x = widths[OVERFLOW_COLUMN]
        del widths[OVERFLOW_COLUMN]
        if x > 0:
            widths[" " * x] = x

    return max_width - 1


def better_settings():
    max_width, _ = get_terminal_size()

    return dict(terminal_width=max_width - 1, max_content_width=max_width - 1)


def format_command_tree(ctx):
    treedata = _build_command_tree(ctx.find_root().command)

    output = []
    _format_tree(output, treedata)

    formatter = ctx.make_formatter()
    formatter.write_dl(output)

    return formatter.getvalue()


class _TreeData:
    def __init__(self, click_command):
        self.name = click_command.name
        self.children = []
        self.short_help = None

        if isinstance(click_command, _click.Command):
            self.short_help = click_command.get_short_help_str()


def _build_command_tree(click_command):
    data = _TreeData(click_command)

    if isinstance(click_command, _click.Group):
        data.children = [_build_command_tree(cmd) for _, cmd in click_command.commands.items()]

    return data


def _format_tree(output, treedata, depth=0, is_last_item=False, is_last_parent=False):
    if depth == 0:
        prefix = ""
        tree_item = ""
    else:
        prefix = "    " if is_last_parent else "│   "
        tree_item = "└── " if is_last_item else "├── "

    help_str = ("  \t" + treedata.short_help) if treedata.short_help else ""
    output.append((prefix * (depth - 1) + tree_item + treedata.name, help_str))

    for i, child in enumerate(sorted(treedata.children, key=lambda x: x.name)):
        _format_tree(
            output,
            child,
            depth=(depth + 1),
            is_last_item=(i == (len(treedata.children) - 1)),
            is_last_parent=is_last_item,
        )
