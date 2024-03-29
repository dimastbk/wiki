import re
from datetime import date

from scripts.base_update import BaseUpdate, Section, SubSection


class KRAZUpdate(BaseUpdate):
    sub_section_re = re.compile(r"^=== *((?:<s>)? *\[\[:?[^=]+?) *===$", flags=re.M)

    category_name = "Категория:Википедия:Незакрытые обсуждения разделения страниц"
    result_page_name = "Википедия:К разделению"
    result_page_template = """{{{{/Шапка}}}}

== Текущие обсуждения ==

{{{{#invoke:RequestTable|TableByDate|header=Статьи, вынесенные на разделение|link=Википедия:К разделению

{}

}}}}

{{{{/Подвал}}}}
"""

    def format_sub_section(self, section: SubSection) -> str:
        title = section.title
        if section.result and "<s>" not in section.title:
            title = f"<s>{title}</s>"
        return f"\n** {title}"

    def format_section(self, section: Section) -> str:
        title = section.title
        if section.result and "<s>" not in section.title:
            title = f"<s>{title}</s>"
        return f"\n* {title}" + "".join(
            [
                self.format_sub_section(sub_section)
                for sub_section in section.sub_sections
            ]
        )

    def format_day_row(self, day: date, sections: list[Section]) -> str:
        formated_sections = "".join(
            [self.format_section(section) for section in sections]
        )
        return f"|{day}|{formated_sections}"


if __name__ == "__main__":
    runner = KRAZUpdate()
    runner.run()
