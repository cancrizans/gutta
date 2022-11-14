import click
import sys,os
sys.path.append(os.path.dirname(__file__))

import builder


@click.group('guttacli')
@click.pass_context
def cli(ctx):
    pass

@cli.command("build")
def command_build():
    click.echo("Building your webcomic...")
    builder.build_website()


def main():
    """A static website builder for webcomics!"""
    cli(prog_name="gutta")

if __name__ == '__main__':
    main()
