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
        select = documents.select()
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
        cases = Table('case')
        latest_advocates = Table('vw_latest_tagging_advocate')
        latest_results = Table('vw_latest_tagging_case_result')
        select = cases.join(
            latest_advocates, type_='LEFT',
            condition=(latest_advocates.case_id == cases.id_case) & (latest_advocates.status == 'processed')
        ).join(
            latest_results, type_='LEFT',
            condition=(latest_results.case_id == cases.id_case) & (latest_results.status == 'processed')
        ).select(
            Column(cases, '*'),
            latest_advocates.advocate_id,
            latest_results.case_result
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
        cases = Table('case')
        select = cases.select(cases.registry_sign)
        select.where = cases.id_case == self.info['case_id']
        query, args = tuple(select)
        with connection().cursor() as cursor:
            cursor.execute(query, args)
            return cursor.fetchone()[0]

    @property
    def public_info(self):
        public = dict(self.info)
        del public['job_run_id']
        public['id'] = public['id_document']
        del public['id_document']
        del public['inserted']
        del public['local_path']
        del public['record_id']
        public['url_original'] = public['web_path']
        del public['web_path']
        public['url_proxy'] = 'https://{}/public/document/view/{}'.format(self._host_name, public['id'])
        return public


class Advocate:

    def __init__(self, info):
        self.info = info

    @property
    def public_info(self):
        return dict(self.info)


class Case:

    def __init__(self, info):
        self.info = info

    @property
    def public_info(self):
        public = dict(self.info)
        public['id'] = public['id_case']
        del public['id_case']
        del public['job_run_id']
        del public['official_data']
        del public['decision_date']
        del public['proposition_date']
        del public['inserted']
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


class Courts:

    SUPREME_ADMINISTRATIVE = Court('supreme_administrative', 1, Document, 'document_supreme_administrative_court')
    SUPREME = Court('supreme', 2, Document, 'document_supreme_court')
    CONSTITUTIONAL = Court('constitutional', 3, ConstitutionalCourtDocument, 'document_law_court')

    ALL = [SUPREME_ADMINISTRATIVE, SUPREME, CONSTITUTIONAL]
    BY_ID = {c.id: c for c in ALL}
