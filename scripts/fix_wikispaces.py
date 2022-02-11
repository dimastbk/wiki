import concurrent.futures
import json
import re
from typing import Iterable

import pywikibot
import requests
from more_itertools import chunked

moon_re = re.compile(
    r"\[(?P<url>https?:\/\/the-moon\.wikispaces\.com/[^\] ]+) (?P<title>[^\]]+)\]"
)

CHUNK = 10


def load_url(url):
    if url is None:
        return None

    return requests.get(
        f"https://archive.org/wayback/available?url={url}&timestamp=20180930"
    ).json()


class FixWikispaces:

    category_name: str
    result_page_name: str
    result_page_template: str

    def __init__(self) -> None:
        self.site = pywikibot.Site("ru", "wikipedia")

    def run(self):
        result: list[tuple[str, str, str, str]] = []

        pages: Iterable[pywikibot.Page] = self.site.search(
            r"insource:/\[https?:\/\/the-moon\.wikispaces\.com/"
        )

        for pages_chunk in chunked(pages, CHUNK):

            urls = []
            for page in pages_chunk:
                print(page)

                link = moon_re.search(page.text)

                if link:
                    urls.append(link.group("url"))
                else:

                    urls.append(None)

            wa_responses = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=CHUNK) as executor:
                for i in executor.map(load_url, urls):
                    wa_responses.append(i)

            for idx, page in enumerate(pages_chunk):
                link = moon_re.search(page.text)

                if not link:
                    continue

                wa_response = wa_responses[idx]
                try:

                    archive_timestamp = wa_response["archived_snapshots"]["closest"][
                        "timestamp"
                    ]
                    archive_date = "{}-{}-{}".format(
                        archive_timestamp[0:4],
                        archive_timestamp[4:6],
                        archive_timestamp[6:8],
                    )
                    archive_url = wa_response["archived_snapshots"]["closest"]["url"]

                    template = "{{{{cite web |url = {} |title = {} |lang = en |deadlink = yes |archive-url = {} |archive-date = {} }}}}".format(
                        link.group("url"),
                        link.group("title")
                        .removesuffix(".")
                        .replace("THE-MOON WIKI", "The Moon-Wiki"),
                        archive_url,
                        archive_date,
                    )

                    result.append(
                        (
                            f"[[{page.title()}]]",
                            link.group(0),
                            template,
                            json.dumps(wa_response),
                        )
                    )
                except Exception as exc:
                    print(exc)
                    result.append(
                        (
                            f"[[{page.title()}]]",
                            link.group(0),
                            str(exc),
                            json.dumps(wa_response),
                        )
                    )
                    continue

        print(self.make_result_page(result))
        result_page = pywikibot.Page(
            self.site, "Участник:DimaBot/Отчёты/the-moon.wikispaces.com"
        )
        result_page.text = self.make_result_page(result)
        result_page.save("Бот: создание отчёта")

    def make_result_page(self, pages: list[tuple]):
        return "{{|\n|-\n|{}\n|}}".format(
            "\n|-\n|".join("||".join(page) for page in pages)
        )


if __name__ == "__main__":
    runner = FixWikispaces()
    runner.run()
