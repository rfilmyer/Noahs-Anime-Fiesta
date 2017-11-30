import scrape
import bs4

YURI_ON_ICE = 32995
YU_YU_HAKUSHO = 392

info, reviews = scrape.get_paged_reviews_by_id(YU_YU_HAKUSHO)

with open("yoi-reviews.html", encoding="utf-8") as f:
   review_page = bs4.BeautifulSoup(f, "lxml")
info, reviews = scrape.parse_review_page(review_page)

print(info)

print(f"Parsed {len(reviews)} reviews.")
for review in reviews:
    print("")
    print(f"Overall score: {review[0]}")
    print("Review:")
    print(review[1])