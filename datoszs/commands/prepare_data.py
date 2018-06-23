from collections import defaultdict
from datoszs.config import host_name
from datoszs.db import global_connection
from datoszs.model import load_cases, load_documents, load_advocates
from glob import glob
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


def prepare(cases, advocates, documents, court_specific_documents, dest, now):
    tempdir = tempfile.mkdtemp()
    os.makedirs(dest, exist_ok=True)
    output.save_csv(cases, 'cases', output_dir=tempdir)
    output.save_csv(advocates, 'advocates', output_dir=tempdir)
    output.save_csv(documents, 'documents', output_dir=tempdir)
    for court_name, court_documents in court_specific_documents.items():
        output.save_csv(court_documents, 'documents_{}'.format(court_name), output_dir=tempdir)
    readme = load_readme_content(cases, advocates, documents, now)
    with open(os.path.join(tempdir, 'README.md'), 'w') as f:
        f.write(readme)
    download_pandoc(version='1.19.1')
    readme_html = pypandoc.convert_file(
        os.path.join(tempdir, 'README.md'),
        to='html5',
        extra_args=['-s', '-S', '-H', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'pandoc.css')]
    )
    datafile_name = 'oadvokatech.ospravedlnosti.cz-{}.zip'.format(now.strftime('%Y-%m-%d'))
    metafile_name = 'oadvokatech.ospravedlnosti.cz-{}.meta.json'.format(now.strftime('%Y-%m-%d'))
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
        for fn in ['README.md', 'README.html'] + [os.path.basename(fn) for fn in glob(os.path.join(tempdir, '*.csv'))]:
            print('adding', fn)
            zp.write(os.path.join(tempdir, fn), fn)
    with open(os.path.join(dest, 'latest.json'), 'w') as f:
        json.dump({
            'data': datafile_name,
            'meta': metafile_name,
        }, f, indent=4, sort_keys=True)


def iterable2dataframe(iterable, field_name='public_info'):
    result = []
    for row in frogress.bar(iterable):
        result.append(getattr(row, field_name))
    return pd.DataFrame(result)


def execute(dest):
    with global_connection():
        documents = list(load_documents())
        documents_by_court = defaultdict(list)
        for doc in documents:
            documents_by_court[doc.court.name].append(doc)
        prepare(
            iterable2dataframe(load_cases()),
            iterable2dataframe(load_advocates()),
            iterable2dataframe(documents),
            {court_name: iterable2dataframe(docs, field_name='court_specific_public_info') for court_name, docs in documents_by_court.items()},
            dest,
            datetime.datetime.now()
        )
