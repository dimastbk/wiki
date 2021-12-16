from scripts.base_update import BaseUpdate


class KULUpdate(BaseUpdate):
    category_name = "Категория:Википедия:Незакрытые обсуждения статей для улучшения"
    result_page_name = "Википедия:К улучшению"
    result_page_template = """{{{{Википедия:К улучшению/Шапка}}}}

== К улучшению ==

{{{{#invoke:RequestTable|TableByDate|days=90|header=Статьи, вынесенные на улучшение|link=Википедия:К улучшению

{}

}}}}

{{{{Википедия:К улучшению/Подвал}}}}
"""


if __name__ == "__main__":
    runner = KULUpdate()
    runner.run()
