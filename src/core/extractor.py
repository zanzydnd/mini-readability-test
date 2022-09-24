import requests
from bs4 import BeautifulSoup, Comment, NavigableString
import re
from typing import List
from urllib.parse import urlparse

from core.const import (
    WHITELISTED_TAGS,
    BLACKLISTED_TAGS,
    BLACKLISTED_CLASSES,
    BLACKLISTED_IDS,
    TEXT_HEADERS,
    TAGS_FOR_NEW_LINE,
    TAGS_FOR_DOUBLE_NEW_LINE,
)


class UsefulTextFromHtmlExtractor:
    def __init__(
        self,
        whitelisted_tags: List[str] = WHITELISTED_TAGS,
        blacklisted_tags: List[str] = BLACKLISTED_TAGS,
        blacklisted_classes: List[str] = BLACKLISTED_CLASSES,
        blacklisted_ids: List[str] = BLACKLISTED_IDS,
        text_headers: List[str] = TEXT_HEADERS,
        tags_for_newline: List[str] = TAGS_FOR_NEW_LINE,
        tags_for_double_newline: List[str] = TAGS_FOR_DOUBLE_NEW_LINE,
    ):
        self._whitelisted_tags = whitelisted_tags
        self._blacklisted_tags = blacklisted_tags
        self._blacklisted_classes = blacklisted_classes
        self._blacklisted_ids = blacklisted_ids
        self._text_headers = text_headers
        self._tags_for_newline = tags_for_newline
        self._tags_for_double_newline = tags_for_double_newline
        self._save_path = ""

    @classmethod
    def from_json_file(cls, path_to_file):
        return UsefulTextFromHtmlExtractor()

    @staticmethod
    def _validate_url(url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc, result.path])
        except:
            return False

    def _parse_url(self, url: str):
        uri = urlparse(url)

        self._url_domain = "{uri.scheme}://{uri.netloc}".format(uri=uri)

        path = uri.path[1:]
        if path[-1] == "/":
            path += "index"
        else:
            path = re.sub("\.\w*$", "", path)
        path += ".txt"

        # self._file_path = os.path.abspath(os.path.expanduser(
        #     os.path.join(self._path_to_save, uri.netloc, path)
        # ))

    def _remove_tag_empty(self, tag) -> bool:
        """
        Удалить пустые теги

        :param tag:
        :return: bool
        """
        if not tag.get_text(strip=True) and tag.name not in self._whitelisted_tags:
            tag.decompose()
            return True
        else:
            return False

    def _remove_tag_in_blacklist(self, tag) -> bool:
        """
        Удалить тег, если он в черном списке
        :param tag:
        :return: bool
        """
        if tag.name.lower() in self._blacklisted_tags:
            tag.decompose()
            return True
        else:
            return False

    def _remove_tags_class_in_blacklist(self, _tag) -> bool:
        if any(
            map(
                lambda class_mask: any(
                    class_mask in attr_class
                    for attr_class in _tag.attrs.get("class", [])
                ),
                self._blacklisted_classes,
            )
        ):
            _tag.decompose()
            return True
        else:
            return False

    def _remove_tags_class_in_id(self, tag):
        """
        Удалить тег, если его id в черном списке
        :param tag:
        :return:
        """
        if any(
            map(
                lambda id_mask: any(
                    id_mask in attr_id for attr_id in tag.attrs.get("id", [])
                ),
                self._blacklisted_ids,
            )
        ):
            tag.decompose()
            return True
        else:
            return False

    @staticmethod
    def _strip_unnecessary_params_in_tag(soup):
        """
        Убрать ненужные параметры из тега

        :param soup:
        :return:
        """
        for _tag in soup.find_all():
            if not isinstance(_tag, NavigableString):
                for _subtag in _tag.descendants:
                    if _subtag.name == "a":
                        _href = _subtag.attrs.get("href", None)
                        if _href is not None:
                            _subtag.attrs = {"href": _href}
                    else:
                        _subtag.attrs = {}

    def _unwrap_divs(self, _tag):
        """
        Распаковка div-a (достаем внутренние теги)

        :param _tag:
        :return:
        """
        child_tags = [
            child_tag
            for child_tag in _tag.contents
            if not isinstance(child_tag, NavigableString)
            and child_tag.name not in self._whitelisted_tags + self._blacklisted_tags
        ]
        if len(child_tags) == 1:
            _tag.unwrap()

    @staticmethod
    def _tags_as_string(tags) -> str:
        """
        Просто мапит все теги в строку
        :param tags:
        :return: str
        """
        return "".join(list(map(lambda _tag: str(_tag), list(tags))))

    def _add_newlines_before_tags(self, _soup):
        for _tag in _soup.find_all():
            if _tag.name in self._tags_for_newline:
                br = BeautifulSoup("<br>", "html.parser").br
                _tag.insert_before(br)
            elif _tag.name in self._tags_for_double_newline + self._text_headers:
                br = BeautifulSoup("<br>", "html.parser").br
                _tag.insert_before(br)
                br = BeautifulSoup("<br>", "html.parser").br
                _tag.insert_before(br)

    @staticmethod
    def _unwrap_nested_tags(_body):
        html = "".join(
            map(lambda _tag: str(_tag).strip(), _body.prettify().split("\n"))
        )
        _bs = BeautifulSoup("<html>" + html + "</html>", "html.parser")
        while len(_bs.contents) == 1:
            _bs.contents[0].unwrap()
        return _bs

    def _replace_header_if_contains_h1_to_h6_tags(self, _tag):
        """
        Заменяем заголовки если тег = h1..h6
        :param _tag:
        :return:
        """
        if (
            any("header" in attr_class for attr_class in _tag.attrs.get("class", []))
            and _tag.name not in self._text_headers
        ):
            subheaders_as_string = self._tags_as_string(
                _tag.find_all(self._text_headers)
            )
            _tag.replace_with(BeautifulSoup(subheaders_as_string, "html.parser"))

    def _remove_tags(self, _soup):
        """
        Удаление тегов


        :param _soup:
        :return:
        """
        _bs = BeautifulSoup(str(_soup).replace("\n", ""), "html.parser")
        for _tag in _bs.find_all():
            if _tag.name == "span":
                _tag.replace_with(
                    BeautifulSoup(
                        " {} ".format(self._tags_as_string(_tag.contents).strip()),
                        "html.parser",
                    )
                )
            elif _tag.name == "a":
                _href = _tag.attrs.get("href")
                if _href is not None and _href[0] == "/":
                    _href = self._url_domain + _href
                _tag.replace_with(
                    BeautifulSoup(
                        " [{}] [{}] ".format(
                            self._tags_as_string(_tag.contents).strip(), _href
                        ),
                        "html.parser",
                    )
                )
            elif _tag.name not in ["br"]:
                _tag.unwrap()
        return _bs

    @staticmethod
    def _replace_br_tags_with_newline(_soup):
        """
        Сделать \n, если тег <br>

        :param _soup:
        :return:
        """
        for _tag in _soup.find_all():
            if _tag.name == "br":
                _tag.replace_with("\n")

    @staticmethod
    def _limit_number_of_symbols_per_line(_article):

        """
        Не позволяет строке быть сликом длинной
        :param _article:
        :return:
        """
        from textwrap import wrap

        _lines = []
        for _line in _article.split("\n"):
            _lines.append(
                "\n".join(
                    wrap(_line, 80, break_long_words=False, break_on_hyphens=False)
                )
            )
        return "\n".join(_lines)

    def process(self, url: str):
        if not self._validate_url(url):
            return False

        self._parse_url(url)

        soup = BeautifulSoup(requests.get(url).content, "html.parser")

        # берем только body
        body = soup.find("body")

        # Удаление комментариев.
        comments = body.findAll(text=lambda text: isinstance(text, Comment))
        for comment in comments:
            comment.extract()

        # удаляем ненужные теги
        for tag in body.find_all():
            if (
                self._remove_tag_empty(tag)
                or self._remove_tag_in_blacklist(tag)
                or self._remove_tags_class_in_id(tag)
                or self._remove_tags_class_in_blacklist(tag)
            ):
                continue
            self._replace_header_if_contains_h1_to_h6_tags(tag)

        self._strip_unnecessary_params_in_tag(body)

        while True:
            old_doc = body.prettify()

            for tag in body.find_all():
                self._unwrap_divs(tag)
                self._remove_tag_empty(tag)

            if old_doc == body.prettify():
                break

        article = self._unwrap_nested_tags(body)
        self._add_newlines_before_tags(article)
        article = self._remove_tags(article)
        self._replace_br_tags_with_newline(article)

        article = re.sub("\n\n+", "\n\n", str(article)).strip()

        article = self._limit_number_of_symbols_per_line(article)

        return article
