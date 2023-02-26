import concurrent.futures
import random
import re
import time
from collections.abc import Iterable
from typing import Optional

import pywikibot
import requests

webcitation_re = re.compile(
    r"({{[^\}]*?\ *url *= *(?P<url>(?:https?|ftp)[^\|\} ]+)[^\}]*?"
    r"\| *archive-?url *= *(?P<archiveurl>https?:\/\/(?:www\.)?webcitation\.org\/?[^\|\} ]+) *"
    r"\| *archive-?date *= *(?P<archivedate>[\d-]+)[^\}]*?}})"
)

archive_date_re = re.compile(r"archive-?date( *)=( *)([\d-]+)([\|\} ]*)")

CHUNK = 5


class FixWikispaces:
    site: pywikibot.APISite

    category_name: str
    result_page_name: str
    result_page_template: str

    def __init__(self) -> None:
        self.site = pywikibot.Site("ru", "wikipedia")
        self.wa_responses = {}

    def load_url(
        self, value: tuple[str, str]
    ) -> tuple[str, tuple[Optional[str], Optional[str]]]:
        time.sleep(0.5)
        url = value[0]
        timestamp = value[1].replace("-", "")

        while True:
            try:
                response = requests.get(
                    f"https://archive.org/wayback/available?url={url}&timestamp={timestamp}"
                )
                if response.status_code == 429:
                    print(f"{url}:{response.status_code}")
                    time.sleep(random.randint(1, 5))
                    continue
                data = response.json()
                if "closest" in data["archived_snapshots"]:
                    return url, (
                        data["archived_snapshots"]["closest"]["url"].replace(
                            "http://web.archive.org", "https://web.archive.org"
                        ),
                        data["archived_snapshots"]["closest"]["timestamp"],
                    )
                return url, (None, None)
            except requests.exceptions.JSONDecodeError:
                print(f"{url}:{response.status_code}")
                return url, (None, None)

        # response = (
        #     requests.get(
        #         f"http://timetravel.mementoweb.org/api/json/{timestamp}/{url}"
        #     ).json(),
        # )
        # if

    def run(self):
        result: set[tuple[str, ...]] = set()
        urls: dict[str, dict] = {}

        pages: Iterable[pywikibot.Page] = self.site.search(
            r'insource:/webcitation/ prefix:"Шаблон:Население/"', namespaces=[10]
        )

        pages = list(pages)
        for page in pages:
            print(page)

            for item in webcitation_re.findall(page.text):
                urls.setdefault(item[1], item[3])

        print("Ссылок:", len(urls))
        with concurrent.futures.ThreadPoolExecutor(max_workers=CHUNK) as executor:
            for url, item in executor.map(self.load_url, list(urls.items())):
                self.wa_responses[url] = item

        for page in pages:
            old_text = page.text
            page_result: dict[str, str] = {}
            links: list[tuple[str, str, str, str]] = webcitation_re.findall(page.text)

            if not links:
                print(f"{page.title()}: Ссылки не найдены!")
                continue

            for link in links:
                archive_url, archive_timestamp = self.wa_responses.get(
                    link[1], (None, None)
                )
                if archive_url and archive_timestamp:
                    archive_date = "{}-{}-{}".format(
                        archive_timestamp[0:4],
                        archive_timestamp[4:6],
                        archive_timestamp[6:8],
                    )

                    template = (
                        link[0]
                        .replace(link[2], archive_url)
                        .replace("archiveurl", "archive-url")
                        .replace("archivedate", "archive-date")
                    )

                    template = archive_date_re.sub(
                        rf"archive-date\1=\2ЪъХъЪъ{archive_date}\4", template
                    ).replace("ЪъХъЪъ", "")

                    result.add(
                        (
                            link[0],
                            template,
                            template,
                        )
                    )
                    page_result[link[0]] = template
                else:
                    print("Архив не найден")
                    template = (
                        link[0]
                        .replace(link[2], "")
                        .replace("archiveurl", "archive-url")
                        .replace("archivedate", "archive-date")
                    )
                    template = archive_date_re.sub(
                        r"archive-date\1=\2ЪъХъЪъ\4", template
                    ).replace("ЪъХъЪъ", "")
                    result.add(
                        (
                            # f"[[{page.title()}]]",
                            link[0],
                            "https://web.archive.org/web/*/" + link[1],
                            template,
                            # json.dumps(wa_response),
                        )
                    )

            if page_result:
                for link, template in page_result.items():
                    page.text = page.text.replace(link, template)

                # pywikibot.showDiff(old_text, page.text)
                # if pywikibot.input_yn("Save?", default=True):
                try:
                    page.save("Бот: замена webcitation")
                except pywikibot.exceptions.LockedPageError as exc:
                    print(f"{page.title()}:{exc}")
                    pywikibot.showDiff(old_text, page.text)

        # print(self.make_result_page(result))

        with open("wiki.txt", "w") as file:
            file.write(self.make_result_page(result))

        result_page = pywikibot.Page(self.site, "Участник:DimaBot/Отчёты/webcitation")
        result_page.text = self.make_result_page(result)
        result_page.save("Бот: создание отчёта")

    def make_result_page(self, pages: set[tuple[str, ...]]):
        return "".join([f"* {link[0]} = {link[1]}\n" for link in pages])


if __name__ == "__main__":
    runner = FixWikispaces()
    runner.run()
