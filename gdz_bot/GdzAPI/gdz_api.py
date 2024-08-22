# -*- coding: ascii -*-
# by MrFriot

import logging

# +lxml
import aiohttp
import bs4

logger: logging.Logger = logging.getLogger(__name__)


class Number:
    def __init__(self, num: str = "", url: str = "") -> None:
        self.num = num
        self.url = url

    async def get_answers(self) -> dict[str, str]:
        """
        This function returns answers as images.
        If something goes wrong, the function will return an empty dict.
        """
        # The main things
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                status = response.status
                if status == 200:
                    html = await response.text()
                else:
                    logger.warning(
                        f"Can't to get response with num page | num: {self.url} | response status: {status}"
                    )
                    return {}
        soup: bs4.BeautifulSoup = bs4.BeautifulSoup(html, "lxml")
        result: dict[str, str] = {}
        # Parsing
        for div_task in soup.find_all("div", {"class": "task-img-container"}):
            div_img = div_task.find("img")
            if (f"https:{div_img.get("src")}".split("/"))[-1][-3::1] in ("jpg", "png"):
                result[div_img.get("alt")] = f"https:{div_img.get("src")}"
        # return result
        return result


class Book:
    def __init__(
        self,
        title: str = "",
        url: str = "",
        cover_url: str = "",
        type_: str = "",
        authors: list[str] | tuple[str] = ("", ""),
        publisher: str = "",
    ) -> None:
        self.title = title
        self.url = url
        self.cover_url = cover_url
        self.type_ = type_
        self.authors = authors
        self.publisher = publisher

    async def get_num_structure(self) -> dict:
        """
        This function returns the structure of numbers in the book.
        If something goes wrong, the function will return an empty dict.
        """
        # The main things
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                status = response.status
                if status == 200:
                    html = await response.text()
                else:
                    logger.warning(
                        f"Can't to get response with book page | book: {self.url} | response status: {status}"
                    )
                    return {}
        soup: bs4.BeautifulSoup = bs4.BeautifulSoup(html, "lxml")

        def __rec(target) -> dict:
            r_dict: dict = {}
            div_section: bs4.element.Tag
            for div_section in target:
                # find name
                r_section_name: str = "*stub"
                h_index: int = 0
                while r_section_name == "*stub":
                    h_index += 1
                    div_section_name = div_section.findChildren(
                        f"h{h_index}", {"class": "heading"}
                    )
                    if div_section_name:
                        r_section_name = " ".join(div_section_name[0].text.split())
                    elif 10 < h_index:
                        break
                # find content
                if div_section.find("div", recursive=False):
                    r_num_list: list[Number] = []
                    div_num: bs4.element.Tag
                    for div_num in div_section.find("div", recursive=False).find_all(
                        "a"
                    ):
                        r_num_list.append(
                            Number(
                                div_num.get("title"),
                                f"https://gdz.ru{div_num.get("href")}",
                            )
                        )
                    r_dict[r_section_name] = r_num_list
                elif div_section.find("section", recursive=False):
                    r_dict[r_section_name] = {}
                    r_dict[r_section_name] = __rec(
                        div_section.find_all("section", recursive=False)
                    )
                else:
                    return {}
            # return result
            return r_dict

        # Parsing
        result = __rec(
            soup.find("div", {"class": "task__list"}).find_all(
                "section", {"class": "section-task"}, recursive=False
            )
        )
        # Return result
        return result


class Chapter:
    def __init__(
        self,
        class_: int = 0,
        subject: str = "",
        url: str = "",
        books: list[Book] | tuple[Book] = (),
    ) -> None:
        self.class_ = class_
        self.subject = subject
        self.url = url
        self.books: list[Book] = list(books)

    async def get_books(self) -> list[Book]:
        """
        This function returns Book objects located in chapter.
        If something goes wrong, the function will return an empty list.
        I don't like this feature, but it works :|
        """
        # The main things
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                status = response.status
                if status == 200:
                    html = await response.text()
                else:
                    logger.warning(
                        f"Can't to get response with chapter page | chapter: {self.url} | response status: {status}"
                    )
                    return []
        soup: bs4.BeautifulSoup = bs4.BeautifulSoup(html, "lxml")
        result: list[Book] = []
        # Parsing
        div_book_list: bs4.element.Tag = soup.find("ul", {"class": "book__list"})
        div_book: bs4.element.Tag
        for div_book in div_book_list.find_all("a", {"class": "book__link"}):
            div_book_attr: bs4.element.Tag
            if not div_book.find("p", {"class": "book__premium"}) is None:
                continue
            book_type: str = ""
            book_authors: list[str] = []
            book_publisher: str = ""

            for div_book_attr in div_book.find(
                "div", {"class": "book__description"}
            ).findChildren(recursive=False):
                if div_book_attr.get("data-book-type"):
                    book_type = div_book_attr.get("data-book-type")
                elif div_book_attr.find("span", {"itemprop": "author"}):
                    book_authors = div_book_attr.find(
                        "span", {"itemprop": "author"}
                    ).text.split(", ")
                elif div_book_attr.find("span", {"itemprop": "publisher"}):
                    book_publisher = div_book_attr.find(
                        "span", {"itemprop": "publisher"}
                    ).text

            result.append(
                Book(
                    " ".join(
                        div_book.find("div", {"class": "book__description"})
                        .find("h4", {"class": "book__title"})
                        .text.split()
                    ),
                    f"https://gdz.ru{div_book.get("href")}",
                    f"https:{div_book.find("img", {"class": "book__cover"}).get("src")}",
                    book_type,
                    book_authors,
                    book_publisher,
                )
            )
        # Return result
        self.books: list[Book] = result


class Api:
    @staticmethod
    async def get_chapter(chapter_class: int = 0, chapter_subject: str = "") -> Chapter:
        """
        This function returns chapter by class and subject.
        If something goes wrong, the function will return an empty chapter.
        """
        # The main things
        if (
            1 > chapter_class > 11
            or type(chapter_class) is not int
            or chapter_subject == ""
            or type(chapter_subject) is not str
        ):
            return Chapter()
        async with aiohttp.ClientSession() as session:
            async with session.get("https://gdz.ru./") as response:
                status = response.status
                if status == 200:
                    html = await response.text()
                else:
                    logger.warning(
                        f"Can't to get response with main gdz page | response status: {status}"
                    )
                    return Chapter()
        soup: bs4.BeautifulSoup = bs4.BeautifulSoup(html, "lxml")
        # Parsing
        div_classes: bs4.element.ResultSet[bs4.element.Tag] = (
            soup.find("div", {"class": "sidebar__main"})
            .find("div")
            .findChildren(recursive=False)
        )
        div_subjects: bs4.element.ResultSet[bs4.element.Tag] = div_classes[
            chapter_class - 1
        ].find_all("a", {"class": "link link-sub"})
        for div_subject in div_subjects:
            if chapter_subject.lower() in div_subject.text.lower():
                return Chapter(
                    chapter_class,
                    chapter_subject,
                    f"https://gdz.ru{div_subject.get("href")}",
                )
        # If chapter not found
        logger.warning(
            f'Chapter not found | input: class - "{chapter_class}", subject - "{chapter_subject}"'
        )
        return Chapter()

    @staticmethod
    async def get_available_chapters() -> dict[str : list[Chapter]]:
        """
        This function returns a list of available chapters.
        If something goes wrong, the function will return an empty list.
        """
        # The main things
        async with aiohttp.ClientSession() as session:
            async with session.get("https://gdz.ru./") as response:
                status = response.status
                if status == 200:
                    html = await response.text()
                else:
                    logger.warning(
                        f"Can't to get response with main gdz page | response status: {status}"
                    )
                    return []
        soup: bs4.BeautifulSoup = bs4.BeautifulSoup(html, "lxml")
        result: dict[int : list[Chapter]] = {}
        # Parsing
        div_classes: bs4.element.ResultSet[bs4.element.Tag] = (
            soup.find("div", {"class": "sidebar__main"})
            .find("div")
            .findChildren(recursive=False)
        )
        class_num: int = 0
        for div_class in div_classes:
            class_num += 1
            subj_in_class: list[Chapter] = []
            div_subjects: bs4.element.ResultSet[bs4.element.Tag] = div_class.find_all(
                "a", {"class": "link link-sub"}
            )
            for div_subject in div_subjects:
                subj_in_class.append(
                    Chapter(
                        class_num,
                        div_subject.text.lower(),
                        f"https://gdz.ru{div_subject.get("href")}",
                    )
                )
            result[str(class_num)] = subj_in_class
        # Return result
        return result
