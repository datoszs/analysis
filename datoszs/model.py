from .config import get_config
from .remote import get_filename
from bs4 import BeautifulSoup
from sql import Table
import os
import re


def load_documents(connection, court):
    with connection.cursor() as cursor:
        documents = Table('document')
        select = documents.select()
        select.where = documents.court_id == court.id
        query, args = tuple(select)
        cursor.execute(query, args)
        cols = [col[0] for col in cursor.description]
        for fetched in cursor:
            yield court.create_document(dict(zip(cols, fetched)))


class Document:

    def __init__(self, info):
        self.info = info

    @property
    def html_content(self):
        if not self.info['local_path'].endswith('html'):
            raise Exception('There is not HTML document.')
        if not hasattr(self, '_html_content'):
            with open(get_filename(os.path.join(get_config('storage.path', required=True), self.info['local_path'])), 'r') as f:
                self._html_content = f.read()
        return self._html_content


class ConstitutionalCourtDocument(Document):

    @property
    def content_info(self):
        soup = BeautifulSoup(self.html_content, 'html.parser')
        panel = soup.find('div', {'id': 'recordCardPanel'})
        result = {}
        for row in panel.find_all('tr'):
            cols = row.find_all('td')
            result[cols[0].text.strip()] = cols[1].text.strip()
        content = soup.find('td', {'id': 'uc_vytah_cellContent'}).text.strip()
        lawyer_matched = re.match('.*?[Zz]ast[^,]*? (.*?),.*', content.split('\n')[0], flags=re.DOTALL)
        residence_matched = re.match('.*?[Ss]e sídlem (.*?), (.*?),.*', content.split('\n')[0], flags=re.DOTALL)
        if lawyer_matched is not None and len(lawyer_matched.group(1)) > 40:
            lawyer_matched = None
        if residence_matched is not None and len(residence_matched.group(1) + residence_matched.group(2)) > 60:
            residence_matched = None
        without_lawyer = 'bez právního zastoupení' in content.split('\n')[0]
        result['lawyer'] = ('bez právního zastoupení' if without_lawyer else '') if lawyer_matched is None else lawyer_matched.group(1)
        result['residence'] = '' if residence_matched is None else '{}, {}'.format(residence_matched.group(1), residence_matched.group(2))
        result['content'] = content
        return result


class Court:

    def __init__(self, id, document_factory):
        self.id = id
        self._document_factory = document_factory

    def create_document(self, info):

        return self._document_factory(info)


class Courts:

    SUPREME_ADMINISTRATIVE = Court(1, Document)
    SUPREME = Court(2, Document)
    CONSTITUTINAL = Court(3, ConstitutionalCourtDocument)

    ALL = [SUPREME_ADMINISTRATIVE, SUPREME, CONSTITUTINAL]
