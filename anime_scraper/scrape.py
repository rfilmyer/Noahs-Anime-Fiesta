import bs4
import requests
import logging
from typing import List, Tuple, Dict
import csv

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
    anime_info, reviews = parse_review_page(bs4.BeautifulSoup(review_response.text, "lxml"))
    anime_info["anime_id"] = anime_id
    return anime_info, reviews

def get_data_by_anime_id(anime_id: int, session: requests.Session=None) -> AnimeListing:
    if not session:
        session = requests
    anime_info, reviews = get_paged_reviews_by_id(anime_id, session)
    return anime_info, reviews

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Get reviews and metadata from MyAnimeList")
    parser.add_argument("-a", "--anime-id", type=int, nargs='*',
                        help="Specify one or more anime IDs for which to pull data.")
    parser.add_argument("-f", "--from-file", type=str,
                        help="Read a list of anime IDs from a file.")
    parser.add_argument("--reviews-directory", "-r", type=str,
                        help="The folder where the script will store review data.",
                        default="reviews")
    parser.add_argument("--output-file", "-o", type=str,
                        help="Where to put a file containing extended metadata about each anime.",
                        default="metadata.csv")
    args = parser.parse_args()


    anime_info_list = []
    all_reviews = {}

    if args.anime_id:
        session = requests.Session()
        for anime_id in args.anime_id:
            anime_info, reviews = get_data_by_anime_id(anime_id, session)
            anime_info_list.append(anime_info)
            all_reviews[anime_id] = reviews

    if args.from_file:
        with open(args.from_file) as f:
            anime_ids = f.readlines()

        session = requests.Session()
        for anime_id in anime_ids:
            anime_id = int(anime_id.strip())
            anime_info, reviews = get_data_by_anime_id(anime_id, session)
            anime_info_list.append(anime_info)
            all_reviews[anime_id] = reviews

    with open(f"{args.output_file}", "w") as csvfile:
        metadata_csv = csv.writer(csvfile)
        columns = ("anime_id", "num_episodes", "studios", "rating", "score", "rank", "popularity_rank")
        metadata_csv.writerow(columns)
        for anime in anime_info_list:
            metadata_csv.writerow((anime.get(column) for column in columns))




    for anime_id, review_list in all_reviews:
        with open(f"{args.reviews_directory}/{anime_id}.csv", "w") as csvfile:
            review_csv = csv.writer(csvfile)
            review_csv.writerow(("overall", "review"))
            for review in review_list:
                review_csv.writerow(review)



