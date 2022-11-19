import click
import sys,os
sys.path.append(os.path.dirname(__file__))

import builder
import webserver

from __init__ import __version__


@click.group('guttacli')
@click.pass_context
def cli(ctx):
    pass

@cli.command('version')
def command_version():
    click.echo(__version__)

@cli.command("create")
def command_create():
    builder.create_website()

@cli.command("build")
def command_build():
    click.echo("Building your webcomic...")
    builder.build_website()
    click.echo("Done!")


@cli.command("go")
def command_go():
    click.echo("Building your webcomic...")
    builder.build_website()
    click.echo("Starting webserver at "+click.style("http://127.0.0.1:8069/",fg='red')+" , go there in your browser...")
    webserver.run_webserver()
    click.echo("Server closed.")


@cli.command('clean')
def command_clean():
    builder.clean_website()
    

def main():
    """A static website builder for webcomics!"""
    cli(prog_name="gutta")

if __name__ == '__main__':
    main()
