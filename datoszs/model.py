from .config import storage_path, host_name
from .crawler import ConstitutionalCourtCrawler
from .db import connection
from .remote import get_filename
from bs4 import BeautifulSoup
from sql import Table, Column
import os
import re


def load_documents(court=None):
    with connection().cursor() as cursor:
        documents = Table('document')
        cases = Table('vw_case_for_advocates')
        pre_select = documents.join(
            cases, type_='INNER',
            condition=(cases.id_case==documents.case_id)
        )
        specific_court_columns = []
        for specific_court in Courts.ALL:
            court_documents = Table(specific_court.document_db_table)
            for col in specific_court.document_db_table_columns:
                specific_court_columns.append(Column(court_documents, col).as_('{}__{}'.format(specific_court.name, col)))
            pre_select = pre_select.join(
                court_documents, type_='LEFT',
                condition=(documents.id_document==court_documents.document_id)
            )
        select = pre_select.select(Column(documents, '*'), *specific_court_columns)
        if court is not None:
            select.where = documents.court_id == court.id
        query, args = tuple(select)
        cursor.execute(query, args)
        cols = [col[0] for col in cursor.description]
        for fetched in cursor:
            row = dict(zip(cols, fetched))
            current_court = court if court is not None else Courts.BY_ID[row['court_id']]
            row['court_id'] = current_court.name
            yield current_court.create_document(row)


def load_cases(court=None):
    with connection().cursor() as cursor:
        cases = Table('vw_case_for_advocates')
        annulment = Table('vw_computed_case_annulment')
        latest_advocates = Table('vw_latest_tagging_advocate')
        latest_results = Table('vw_latest_tagging_case_result')
        select = cases.join(
            latest_advocates, type_='LEFT',
            condition=(latest_advocates.case_id == cases.id_case) & (latest_advocates.status == 'processed')
        ).join(
            latest_results, type_='LEFT',
            condition=(latest_results.case_id == cases.id_case) & (latest_results.status == 'processed')
        ).join(
            annulment, type_='LEFT',
            condition=(annulment.annuled_case == cases.id_case)
        ).select(
            Column(cases, '*'),
            latest_advocates.advocate_id,
            latest_results.case_result,
            annulment.annuled_case,
            annulment.annuling_case
        )
        if court is not None:
            select.where = cases.court_id == court.id
        query, args = tuple(select)
        cursor.execute(query, args)
        cols = [col[0] for col in cursor.description]
        for fetched in cursor:
            row = dict(zip(cols, fetched))
            current_court = court if court is not None else Courts.BY_ID[row['court_id']]
            row['court_id'] = current_court.name
            yield Case(row)


def load_advocates():
    with connection().cursor() as cursor:
        advocates = Table('advocate')
        info = Table('advocate_info')
        select = advocates.join(
            info,
            condition=(advocates.id_advocate == info.advocate_id) & (info.valid_to == None)
        ).select(
            info.degree_before,
            info.degree_after,
            info.name,
            info.surname,
            advocates.id_advocate.as_('id'),
            advocates.identification_number.as_('registration_number'),
            advocates.registration_number.as_('identification_number')
        )
        query, args = tuple(select)
        cursor.execute(query, args)
        cols = [col[0] for col in cursor.description]
        for fetched in cursor:
            row = dict(zip(cols, fetched))
            yield Advocate(row)


class Document:

    def __init__(self, info, storage_path, host_name):
        self.info = info
        self._storage_path = storage_path
        self._host_name = host_name

    @property
    def html_content(self):
        if not self.info['local_path'].endswith('html'):
            raise Exception('There is not HTML document.')
        if not hasattr(self, '_html_content'):
            filename = get_filename(os.path.join(self._storage_path, self.info['local_path']))
            if not os.path.exists(filename):
                with open(filename, 'w') as f:
                    self._html_content = ConstitutionalCourtCrawler.start().get_document_html(self)
                    f.write(self._html_content)
            else:
                with open(filename, 'r') as f:
                    self._html_content = f.read()
        return self._html_content

    @property
    def registry_sign(self):
        cases = Table('vw_case_for_advocates')
        select = cases.select(cases.registry_sign)
        select.where = cases.id_case == self.info['case_id']
        query, args = tuple(select)
        with connection().cursor() as cursor:
            cursor.execute(query, args)
            return cursor.fetchone()[0]

    @property
    def court(self):
        return Courts.BY_NAME[self.info['court_id']]

    @property
    def public_info(self):
        public = {
            key: self.info[key]
            for key in [
                'case_id',
                'court_id',
                'decision_date',
                'local_path',
            ]
        }
        public['id'] = self.info['id_document']
        public['url_original'] = self.info['web_path']
        public['url_proxy'] = 'https://{}/public/document/view/{}'.format(self._host_name, public['id'])
        return public

    @property
    def court_specific_public_info(self):
        court_prefix = '{}__'.format(self.info['court_id'])
        result = {}
        for key, val in self.info.items():
            if not key.startswith(court_prefix):
                continue
            key = key.replace(court_prefix, '')
            if key.startswith('id_document'):
                continue
            if key == 'names':
                continue
            # remove typos
            key = key.replace('paralel', 'parallel')
            result[key] = val
        return result


class Advocate:

    def __init__(self, info):
        self.info = info

    @property
    def public_info(self):
        return {
            key: self.info[key]
            for key in [
                'degree_before',
                'degree_after',
                'id',
                'identification_number',
                'name',
                'registration_number',
                'surname',
            ]
        }


class Case:

    def __init__(self, info):
        self.info = info

    @property
    def public_info(self):
        public = {
            key: self.info[key]
            for key in [
                'advocate_id',
                'case_result',
                'court_id',
                'registry_sign',
                'year',
                'annuling_case',
            ]
        }
        public['id'] = self.info['id_case']
        if public['advocate_id'] is None:
            public['advocate_id'] = -1
        if public['annuling_case'] is None:
            public['annuling_case'] = -1
        public['annuled'] = int(bool(self.info['annuled_case']))
        return public


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

    def __init__(self, name, id, document_factory, document_db_table):
        self.id = id
        self.name = name
        self._document_factory = document_factory
        self.document_db_table = document_db_table

    def create_document(self, info):
        return self._document_factory(info, storage_path(), host_name())

    @property
    def document_db_table_columns(self):
        with connection().cursor() as cursor:
            documents = Table(self.document_db_table)
            select = documents.select(Column(documents, '*'), limit=1)
            query, args = tuple(select)
            cursor.execute(query, args)
            return [col[0] for col in cursor.description]


class Courts:

    SUPREME_ADMINISTRATIVE = Court('supreme_administrative', 1, Document, 'document_supreme_administrative_court')
    SUPREME = Court('supreme', 2, Document, 'document_supreme_court')
    CONSTITUTIONAL = Court('constitutional', 3, ConstitutionalCourtDocument, 'document_law_court')

    ALL = [SUPREME_ADMINISTRATIVE, SUPREME, CONSTITUTIONAL]
    BY_ID = {c.id: c for c in ALL}
    BY_NAME = {c.name: c for c in ALL}
