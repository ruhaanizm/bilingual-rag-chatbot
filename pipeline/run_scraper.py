from scraper import crawl

START_URL = "https://www.hbtu.ac.in/"  # CHANGE THIS

crawl(START_URL, max_pages=200)