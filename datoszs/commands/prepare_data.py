from datoszs.config import host_name
from datoszs.db import global_connection
from datoszs.model import load_cases, load_documents, load_advocates
import datetime
import datoszs.output as output
import frogress
import os
import pandas as pd
import shutil
import pypandoc
from pypandoc.pandoc_download import download_pandoc


def load_readme_content(cases):
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'public_data_README.md'), 'r') as f:
        content = f.read()
    return content.format(
        HOST=host_name(),
        DECISION_PERCENTAGE=int(100 * (1 - len(cases) / sum(cases['case_result'].isnull()))) if cases else 0,
        ADVOCATE_PERCENTAGE=int(100 * (1 - len(cases) / sum(cases['advocate_id'].isnull()))) if cases else 0,
        LAST_UPDATE=datetime.date.today()
    )


def prepare(cases, advocates, documents, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)
    output.save_csv(cases, 'cestiadvokati_cases', output_dir=dest)
    output.save_csv(advocates, 'cestiadvokati_advocates', output_dir=dest)
    output.save_csv(documents, 'cestiadvokati_documents', output_dir=dest)
    readme = load_readme_content(cases)
    with open(os.path.join(dest, 'README.md'), 'w') as f:
        f.write(readme)
    download_pandoc()
    readme_html = pypandoc.convert_file(
        os.path.join(dest, 'README.md'),
        to='html5',
        extra_args=['-s', '-S', '-H', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'pandoc.css')]
    )
    with open(os.path.join(dest, 'README.html'), 'w') as f:
        f.write(readme_html)


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
            dest
        )
