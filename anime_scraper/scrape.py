import bs4
import requests
import logging
from typing import List, Tuple, Dict

# Custom Types
ReviewList = List[Tuple[int, str]]
AnimeDetails = Dict[str, str]
AnimeListing = Tuple[AnimeDetails, ReviewList]

logging.basicConfig()
logger = logging.getLogger()

details_url = "https://myanimelist.net/anime/{anime_id}"
reviews_url = details_url + "/Yuri_on_Ice/reviews"


def find_sidebar_info_by_label(label: str, surrounding_div: bs4.Tag) -> str:
    span = surrounding_div.find("span", text=label)

    # span.next_sibling can sometimes be a single newline character
    next_sibling = next(item for item in span.next_siblings if item != "\n")

    # sometimes, next_sibling is a bs4.NavigableString, sometimes it's a bs4.Tag
    info = next_sibling.text.strip() if isinstance(next_sibling, bs4.Tag) else next_sibling.strip()
    return info


def find_sidebar_statistics_by_label(label: str, surrounding_div: bs4.Tag) -> str:
    span = surrounding_div.find("span", text=label)
    next_siblings = span.next_siblings

    # we have to go to the *second* element in span.next_siblings
    next(next_siblings, None)
    metric = next(next_siblings, None)
    return metric.text if metric else None


def scrape_sidebar(sidebar: bs4.Tag) -> AnimeDetails:
    sidebar = sidebar.div

    def get_info(label: str) -> str:
        return find_sidebar_info_by_label(label, sidebar)

    def get_statistics(label: str) -> str:
        return find_sidebar_statistics_by_label(label, sidebar)

    return {"episodes": get_info("Episodes:"),
            "studios": get_info("Studios:"),
            "rating": get_info("Rating:"),
            "score": get_statistics("Score:"),
            "rank": get_statistics("Ranked:"),
            "popularity_rank": get_info("Popularity:")}


def scrape_review_main_bar(td: bs4.Tag) -> ReviewList:
    # every div.borderDark
    reviews = []
    review_divs = td.find_all("div", class_="borderDark")
    logger.warning("found %d reviews", len(review_divs))

    for borderDark in review_divs:
        # Overall Rating:

        # div.borderDark > div.spaceit > div.mb8 > 3rd div
        rating_div = [div for div in borderDark.div.div.contents if div.name == "div"][2]

        # <a>'s onclick gives the selector for the more structured review
        # but we are only interested in an overall score for now
        overall_rating_string = rating_div.contents[2]
        overall_rating = next(int(s) for s in overall_rating_string.split() if s.isdigit())

        # Review text:
        review_div = borderDark.find("div", recursive=False, class_="textReadability")

        unformatted_strings = [x for x in review_div.children if isinstance(x, bs4.NavigableString)]

        for paragraph in review_div.span(text=True):
            unformatted_strings.append(paragraph)

        review = "\n".join([x.strip() for x in unformatted_strings if x not in ("Helpful", "\n")])

        reviews.append((overall_rating, review))

    return reviews


def parse_review_page(page: bs4.BeautifulSoup) -> AnimeListing:
    # second td in first tr in $("#content table")
    content_div = page.find("div", id="content")
    sidebar, main_bar = content_div.table.tr.find_all("td", recursive=False)[:2]

    anime_info = scrape_sidebar(sidebar)
    reviews = scrape_review_main_bar(main_bar)

    return anime_info, reviews


def get_page_by_id(anime_id: int, session: requests.Session=None) -> requests.Response:
    if not session:
        session = requests
    return session.get(details_url.format(anime_id=anime_id))


def get_paged_reviews_by_id(anime_id: int, session: requests.Session=None, page_num: int=None) -> AnimeListing:
    if not session:
        session = requests
    review_response = session.get(reviews_url.format(anime_id=anime_id))
    return parse_review_page(bs4.BeautifulSoup(review_response.text, "lxml"))



if __name__ == '__main__':
    pass
