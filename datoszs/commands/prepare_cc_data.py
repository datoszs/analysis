from datoszs.db import global_connection
from datoszs.model import Courts, load_documents
import frogress
import os
import pandas as pd
import spiderpig as sp


@sp.configured()
def save_document(doc_info, output_dir=None):
    identifier = doc_info['Identifikátor evropské judikatury']
    identifier_dir = os.path.join(output_dir, '-'.join(identifier.split(':')[:-1]))
    if not os.path.exists(identifier_dir):
        os.makedirs(identifier_dir)
    filename = '{}.txt'.format(os.path.join(identifier_dir, identifier.replace(':', '-').replace('.', '-')))
    with open(filename, 'w') as f:
        f.write(doc_info['content'])
        doc_info['txt_file'] = filename.replace(output_dir, '')
    del doc_info['content']


@sp.configured()
def save_csv(data, output_dir=None):
    data.to_csv(os.path.join(output_dir, 'data.csv'), index=False, sep=';')


def execute():
    with global_connection():
        result = []
        for doc in frogress.bar(load_documents(Courts.CONSTITUTINAL)):
            doc_info = doc.content_info
            result.append(doc_info)
    save_csv(pd.DataFrame(result))
