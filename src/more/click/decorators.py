import functools

import click as _click
import pkg_resources
from click_plugins import with_plugins


def load_plugins(namespace):
    return with_plugins(pkg_resources.iter_entry_points(namespace))


def catch_exception(exception=Exception, exit_code=1, message=None):
    """ decorator a command/group to exit on exceptions, exiting with exit_code. """

    def decorator(f):
        @_click.pass_context
        def new_func(ctx, *args, **kwargs):
            try:
                return ctx.invoke(f, *args, **kwargs)
            except exception as e:  # noqa:W0703: depends on param so could be anything
                _click.secho(message if message else f"{e}", fg="red")
                ctx.exit(code=exit_code)

        return functools.update_wrapper(new_func, f)

    return decorator
