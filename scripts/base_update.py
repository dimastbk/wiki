import re
from dataclasses import dataclass, field
from datetime import date, datetime

import pywikibot

MONTH_MAP = (
    ("января", "01"),
    ("февраля", "02"),
    ("марта", "03"),
    ("апреля", "04"),
    ("мая", "05"),
    ("июня", "06"),
    ("июля", "07"),
    ("августа", "08"),
    ("сентября", "09"),
    ("октября", "10"),
    ("ноября", "11"),
    ("декабря", "12"),
)


@dataclass
class SubSection:
    title: str
    result: bool = False
    preliminary_result: bool = False
    disputed_result: bool = False
    difficult_discussion: bool = False


@dataclass
class Section:
    title: str
    result: bool = False
    preliminary_result: bool = False
    disputed_result: bool = False
    difficult_discussion: bool = False
    sub_sections: list["SubSection"] = field(default_factory=list)


class BaseUpdate:
    date_re = re.compile(r".*/(\d{1,2} \w+ 20\d\d).*")
    section_re = re.compile(r"^(===?[^=]+===?) *$", flags=re.M)

    main_section_re = re.compile(r"^== *([^=]+?) *== *$", flags=re.M)
    main_section_result = re.compile(r"^=== *Итог *===$", flags=re.M + re.I)
    main_section_preliminary_result = re.compile(
        r"^=== *Предварительный итог *===$", flags=re.M + re.I
    )
    main_section_disputed_result = re.compile(
        r"^=== *Оспоренный итог *===$", flags=re.M + re.I
    )
    sub_section_re = re.compile(
        r"^=== *((?:<s>)? *\[\[:?[^=\]]+?\]\] *(?:</s>)?) *===$", flags=re.M
    )
    sub_section_result = re.compile(r"^==== *Итог *====$", flags=re.M + re.I)
    sub_section_preliminary_result = re.compile(
        r"^==== *Предварительный итог *====$", flags=re.M + re.I
    )
    sub_section_disputed_result = re.compile(
        r"^==== *Оспоренный итог *====$", flags=re.M + re.I
    )

    category_name: str
    result_page_name: str
    result_page_template: str

    def __init__(self) -> None:
        self.site = pywikibot.Site("ru", "wikipedia")

    def parsedate(self, value: str) -> date:
        date_match = self.date_re.match(value).group(1)

        for month, number in MONTH_MAP:
            date_match = date_match.replace(month, number)

        return datetime.strptime(date_match, "%d %m %Y").date()

    def parsepage(self, page: pywikibot.Page) -> list[Section]:
        sections = self.section_re.split(page.text)
        result_sections = []
        result_section = None

        for section in sections:
            if section_match := self.main_section_re.match(section):
                if result_section is not None:
                    result_sections.append(result_section)
                result_section = Section(title=section_match.group(1))

            elif self.main_section_result.match(section):
                result_section.result = True
                for sub_section in result_section.sub_sections:
                    sub_section.result = True

            elif self.main_section_preliminary_result.match(section):
                result_section.preliminary_result = True

            elif self.main_section_disputed_result.match(section):
                result_section.disputed_result = True

            elif section_match := self.sub_section_re.match(section):
                result_section.sub_sections.append(
                    SubSection(title=section_match.group(1))
                )

            elif self.sub_section_result.match(section):
                result_section.sub_sections[-1].result = True

            elif self.sub_section_preliminary_result.match(section):
                result_section.sub_sections[-1].preliminary_result = True

            elif self.sub_section_disputed_result.match(section):
                result_section.sub_sections[-1].disputed_result = True

        if result_section is not None:
            result_sections.append(result_section)

        return result_sections

    def build_section_list(self):
        day_pages: dict[date, list[Section]] = {}

        category = pywikibot.Category(self.site, self.category_name)

        day_page: pywikibot.Page
        for day_page in category.articles(content=True):
            try:
                page_date = self.parsedate(
                    day_page.title(
                        with_ns=False, with_section=False, without_brackets=True
                    )
                )
                day_pages[page_date] = self.parsepage(day_page)
            except Exception as exc:
                print(exc)

        return day_pages

    def format_sub_section(self, section: SubSection) -> str:
        title = section.title
        if section.result and "<s>" not in section.title:
            title = f"<s>{title}</s>"
        return f"<small>{title}</small>"

    def format_section(self, section: Section) -> list[str]:
        title = section.title
        if section.result and "<s>" not in section.title:
            title = f"<s>{title}</s>"
        return [title] + [
            self.format_sub_section(sub_section) for sub_section in section.sub_sections
        ]

    def format_day_row(self, day: date, sections: list[Section]) -> str:
        formated_sections = " • ".join(
            sum([self.format_section(section) for section in sections], [])
        )
        return f"|{day}|{formated_sections}"

    def make_page_text(self, pages: dict[date, list[Section]]) -> str:
        page_text = "\n\n".join(
            [self.format_day_row(day, sections) for day, sections in pages.items()]
        )
        return self.result_page_template.format(page_text)

    def sort_pages(self, pages: dict[date, list[Section]]):
        pages = dict(sorted(pages.items(), key=lambda item: item[0], reverse=True))
        return pages

    def save_result_page(self, result_page_text: str):
        result_page = pywikibot.Page(self.site, self.result_page_name)
        result_page.text = result_page_text
        result_page.save("Бот: обновление")

    def run(self):
        pages = self.build_section_list()
        pages = self.sort_pages(pages)
        result_text = self.make_page_text(pages)
        self.save_result_page(result_text)
