from datoszs.model import Courts, load_documents
from datoszs.config import get_config
import pandas
import os


def execute():
    output_dir = get_config('output.dir', default='output')
    result = []
    for doc in load_documents(Courts.CONSTITUTINAL):
        doc_info = doc.content_info
        identifier = doc_info['Identifikátor evropské judikatury']
        identifier_dir = os.path.join(output_dir, '-'.join(identifier.split(':')[:-1]))
        if not os.path.exists(identifier_dir):
            os.makedirs(identifier_dir)
        filename = os.path.join(identifier_dir, identifier.replace(':', '-').replace('.', '-'))
        with open(filename, 'w') as f:
            f.write(doc_info['content'])
            doc_info['txt_file'] = filename.replace(output_dir, '')
        del doc_info['content']
        result.append(doc_info)
    pandas.DataFrame(result).to_csv(os.path.join(output_dir, 'data.csv'), index=False, sep=';')
