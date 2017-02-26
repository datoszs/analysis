from urllib.parse import urljoin
from ghost import Ghost


class Crawler:

    def __init__(self, ghost_session):
        self._session = ghost_session

    @property
    def session(self):
        return self._session


class ConstitutionalCourtCrawler(Crawler):

    BASE_URL = "http://nalus.usoud.cz/Search/"
    SEARCH_URL = urljoin(BASE_URL, "Search.aspx")

    def __init__(self, ghost_session):
        self._session = ghost_session

    @staticmethod
    def start(timeout=10000):
        ghost = Ghost()
        session = ghost.start(
            download_images=False,
            show_scrollbars=False,
            wait_timeout=timeout,
            display=False,
            plugins_enabled=False
        )
        return ConstitutionalCourtCrawler(session)

    def get_document_html(self, document):
        self.session.open(self.SEARCH_URL)
        self.session.set_field_value('#ctl00_MainContent_citace', document.registry_sign)
        self.session.click("#ctl00_MainContent_but_search", expect_loading=True)
        self.session.click('a', expect_loading=True)
        return self.session.content
