from datoszs.config import host_name
from datoszs.db import global_connection
from datoszs.model import load_cases, load_documents, load_advocates
from pypandoc.pandoc_download import download_pandoc
import datetime
import datoszs.output as output
import frogress
import json
import locale
import os
import pandas as pd
import pypandoc
import tempfile
import zipfile


def load_readme_content(cases, advocates, documents, now):
    locale.setlocale(locale.LC_ALL, '')
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'public_data_README.md'), 'r') as f:
        content = f.read()
    return content.format(
        HOST=host_name(),
        DECISION_PERCENTAGE=int(100 * (cases['case_result'].notnull().sum() / len(cases))) if len(cases) > 0 else 0,
        ADVOCATE_PERCENTAGE=int(100 * (cases['advocate_id'].notnull().sum() / len(cases))) if len(cases) > 0 else 0,
        LAST_UPDATE=now.strftime('%Y-%m-%d'),
        CASE_NUM='{:n}'.format(len(cases)),
        ADVOCATE_NUM='{:n}'.format(len(advocates)),
        DOCUMENT_NUM='{:n}'.format(len(documents))
    )


def prepare(cases, advocates, documents, dest, now):
    tempdir = tempfile.mkdtemp()
    os.makedirs(dest, exist_ok=True)
    output.save_csv(cases, 'cases', output_dir=tempdir)
    output.save_csv(advocates, 'advocates', output_dir=tempdir)
    output.save_csv(documents, 'documents', output_dir=tempdir)
    readme = load_readme_content(cases, advocates, documents, now)
    with open(os.path.join(tempdir, 'README.md'), 'w') as f:
        f.write(readme)
    download_pandoc(version='1.19.1')
    readme_html = pypandoc.convert_file(
        os.path.join(tempdir, 'README.md'),
        to='html5',
        extra_args=['-s', '-S', '-H', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'pandoc.css')]
    )
    datafile_name = 'cestiadvokati-{}.zip'.format(now.strftime('%Y-%m-%d'))
    metafile_name = 'cestiadvokati-{}.meta.json'.format(now.strftime('%Y-%m-%d'))
    with open(os.path.join(tempdir, 'README.html'), 'w') as f:
        f.write(readme_html)
    with open(os.path.join(dest, metafile_name), 'w') as f:
        json.dump({
            'advocates': len(advocates),
            'cases': len(cases),
            'documents': len(documents),
            'exported': now.strftime('%Y-%m-%d %H:%M:%S'),
        }, f, indent=4, sort_keys=True)
    with zipfile.ZipFile(os.path.join(dest, datafile_name), 'w', zipfile.ZIP_DEFLATED) as zp:
        for fn in ['README.md', 'README.html', 'advocates.csv', 'cases.csv', 'documents.csv']:
            print('adding', fn)
            zp.write(os.path.join(tempdir, fn), fn)
    with open(os.path.join(dest, 'latest.json'), 'w') as f:
        json.dump({
            'data': datafile_name,
            'meta': metafile_name,
        }, f, indent=4, sort_keys=True)


def generator2dataframe(generator):
    result = []
    for row in frogress.bar(generator()):
        result.append(row.public_info)
    return pd.DataFrame(result)


def execute(dest):
    with global_connection():
        prepare(
            generator2dataframe(load_cases),
            generator2dataframe(load_advocates),
            generator2dataframe(load_documents),
            dest,
            datetime.datetime.now()
        )
