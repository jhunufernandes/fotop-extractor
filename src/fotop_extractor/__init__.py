from dataclasses import dataclass
from logging import INFO, basicConfig, info
from math import ceil
from os import makedirs
from os.path import join as os_path_join

from bs4 import BeautifulSoup
from httpx import Response, get

basicConfig(level=INFO)


@dataclass
class FotopExtractorSchema:
    event_id: int
    runner_id: int
    sample: int | None = None
    columns: int = 4


class HTTPClient:
    @staticmethod
    def get(url: str) -> Response:
        info(f"HTTPClient.get: {url}")
        return get(url)


class HTMLParser:
    @staticmethod
    def parse_html(html_text: str) -> BeautifulSoup:
        info("HTMLParser.parse_html")
        return BeautifulSoup(html_text, "html.parser")

    @staticmethod
    def find_by_class(soup_tree: BeautifulSoup, element_tag: str, classname: str):
        info("HTMLParser.find_by_class: {element_tag} {classname}")
        return soup_tree.find_all(element_tag, class_=classname)


class FileWriter:
    @staticmethod
    def make_dir(path: str) -> None:
        info(f"FileWriter.make_dir: {path}")
        makedirs(path, exist_ok=True)

    @staticmethod
    def write_file(file_path: str, file_content: bytes) -> None:
        info(f"FileWriter.write_file: {file_path}")
        with open(file_path, "wb") as f:
            f.write(file_content)


class FotopExtractor:
    def __init__(self, input: FotopExtractorSchema) -> None:
        self.event_url = (
            f"https://fotop.com.br/fotos/eventos/busca/id/{input.runner_id}/evento/{input.event_id}/busca/numero"
        )
        self.sample = input.sample
        self.columns = input.columns

    def run(self):
        event_page_response = HTTPClient.get(self.event_url)
        event_page_html_text = event_page_response.text

        event_page_html_tree = HTMLParser.parse_html(event_page_html_text)
        elements = HTMLParser.find_by_class(event_page_html_tree, "span", "fotoCorredor")

        if self.sample:
            elements = elements[: self.sample]

        for idx, el in enumerate(elements):
            line = ceil(idx / self.columns)
            column = idx % self.columns

            img = el.find("img")
            attrs = img.attrs
            src = attrs["src"]

            dir = "images"
            FileWriter.make_dir(dir)

            img_response = HTTPClient.get(src)
            img_content = img_response.content
            img_extension = src.split(".")[-1]
            img_filename = f"{line}-{column}.{img_extension}"

            file_path = os_path_join(dir, img_filename)
            FileWriter.write_file(file_path, img_content)
