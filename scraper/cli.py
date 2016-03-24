import json
import os
import sys

import click
import jsonschema
import lxml.etree
import lxml.html
import requests

from .htmlpage import load_html_page, etree2html
from .verbosescraper import verbose_scrape
from .webscraper import scrape_page, xpath_returns_text

SCHEMA_FILENAME = os.path.join(os.path.dirname(__file__), 'scraperschema.json')


@click.command()
@click.option('-f', '--file', 'cfg_file', type=click.File(),
              help='name of JSON file containing xpaths')
@click.option('-x', '--xpath', help='XPATH expression')
@click.option('-u', '--url', help='URL of HTML page')
@click.option('-P', '--page', type=click.File('rb'),
              help='name of file containing HTML content')
@click.option('-s', '--sep', default='-',
              help='output list separator')
@click.option('-w', '--width', type=int, default=78,
              help='output separator width')
@click.option('-v', '--verbose', is_flag=True,
              help='display the results for each scraper step')
def main(cfg_file, xpath, url, page, sep, width, verbose):
    separator = sep * width + '\n'

    try:
        config = json.load(cfg_file) if cfg_file else {}
        jsonschema.validate(config, json.load(open(SCHEMA_FILENAME)))
        etree = lxml.html.fromstring(load_html_page(config, page, url))
        if config:
            if verbose:
                steps, result = verbose_scrape(etree, config, sep=separator)
                click.echo('\n'.join(steps) + '\n' + separator)
            else:
                result = scrape_page(etree, config)
            click.echo(json.dumps(result, indent=4, sort_keys=True))
            return

        if not xpath:
            click.echo(etree2html(etree))
            return

        results = etree.xpath(xpath)
        if not results:
            return

        if xpath_returns_text(xpath):
            click.echo('\n'.join(results))
            return

        elements = map(etree2html, results)
        separator = bytes(separator, 'utf8')
        click.echo(separator + (separator).join(elements) + separator)

    except (
        EnvironmentError,
        json.JSONDecodeError, jsonschema.ValidationError,
        requests.RequestException, requests.HTTPError,
        lxml.etree.ParseError, UnicodeDecodeError,
        lxml.etree.XPathSyntaxError, lxml.etree.XPathEvalError
    ) as exception:
        error = exception.__class__.__name__
        click.echo('{}: {}'.format(error, exception), err=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
