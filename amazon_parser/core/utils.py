#!/usr/bin/env python3
"""
Amazon KDP Parser with captcha avoidance techniques (no proxies)
"""
from dataclasses import dataclass
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Final

import requests
import time
import random
from bs4 import BeautifulSoup

from amazon_parser.settings import BASE_DIR

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

########################################################################################################

class HttpsProxyManager:
    def __init__(self, proxy_list: list[str]):
        """
        Initialize with list of proxies in format "host:port:user:pass"
        """
        self.proxies = []
        for proxy in proxy_list:
            host, port, user, password = proxy.strip().split(':')
            self.proxies.append({
                'host': host,
                'port': port,
                'user': user,
                'password': password
            })

    def get_proxy_dict(self, proxy: dict) -> dict:
        """Convert proxy info into requests format for HTTPS only"""
        auth = f"{proxy['user']}:{proxy['password']}"
        # Format specifically for HTTPS proxy
        proxy_url = f"http://{auth}@{proxy['host']}:{proxy['port']}"
        return {
            'http': proxy_url,
            'https': proxy_url
        }

    def get_random_proxy(self) -> dict:
        """Get a random proxy from the list"""
        return self.get_proxy_dict(random.choice(self.proxies))
    
########################################################################################################

@dataclass
class ParsedResult:
    rating: float | None
    reviews_count: int | None
    best_sellers_ranks: list[str] | None
    reviews: list[dict] | None


class AmazonKDPParser:
    """Parser for Amazon KDP website with basic captcha avoidance."""

    HTML_PAGES_DATA: Final[Path] = BASE_DIR / 'data'

    def __init__(self):
        """Initialize the parser with a requests session."""
        self.proxy_manager = HttpsProxyManager([
            "91.132.12.165:12323:14a0693892686:42fbec1479",
            "141.98.58.86:12323:14a0693892686:42fbec1479",
            "205.233.201.252:12323:14a0693892686:42fbec1479",
        ])
        self.session = requests.Session()
        self.configure_session()
        self._page_title = None

    def configure_session(self):
        """Configure the session with headers that make it look like a real browser."""
        # Rotate between common user agents
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
        ]
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.amazon.com/',
            'sec-ch-ua': '"Google Chrome";v="120", "Chromium";v="120", "Not=A?Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Connection': 'keep-alive'
        }
        headers.update({
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'DNT': '1',
        })

        # Update session headers
        self.session.headers.update(headers)
        self.session.proxies.update(self.proxy_manager.get_random_proxy())
        print(self.session.proxies)

        # self.session.cookies.update({
        #     'session-id': f'{random.randint(100000000, 999999999)}',
        #     'session-id-time': f'{int(time.time())}',
        #     'i18n-prefs': 'USD',
        #     'sp-cdn': 'L5Z9:US',
        #     'ubid-main': f'{random.randint(100000000, 999999999)}',
        #     'csm-hit': f'tb:{random.randint(100000000, 999999999)}+s-{random.randint(100000000, 999999999)}|{int(time.time())}',
        # })

    def fetch_page(self, url, max_retries=3):
        """
        Fetch the page with captcha avoidance techniques.

        Args:
            url (str, optional): Target URL
            max_retries (int): Maximum number of retry attempts

        Returns:
            str: HTML content if successful, None otherwise
        """
        target_url = url 

        for attempt in range(max_retries):
            try:
                logger.info(f"Attempt {attempt + 1}/{max_retries} to fetch {target_url}")

                # Add delays between requests to appear more human-like
                if attempt > 0:
                    delay = random.uniform(2, 5)
                    logger.info(f"Waiting {delay:.2f} seconds before retry")
                    time.sleep(delay)

                # Randomize the URL slightly to avoid pattern detection
                # Add a harmless parameter that makes each request look unique
                # modified_url = f"{target_url}{'&' if '?' in target_url else '?'}_={random.randint(1000000, 9999999)}"

                # Fetch the page
                response = self.session.get(
                    target_url,
                    timeout=15  # Add timeout to prevent hanging
                )
                if not response.ok:
                    logger.error(f"Failed to fetch data. Response: {response.status_code}, reason: {response.reason}")
                    break

                soup = BeautifulSoup(response.text, 'html.parser')

                # Check for captcha in the response
                if soup.find(id="captchacharacters"):
                    logger.warning("Captcha detected, trying different approach")
                    self.configure_session()
                    time.sleep(random.uniform(5, 10))
                    continue

                return response.text
            except Exception as e:
                logger.error(f"Error during fetch: {str(e)}")

        logger.error("All attempts failed")
        return None

    def warm_up_session(self):
        """
        Warm up the session by visiting other Amazon pages first.
        This can help avoid captchas by making the session look more natural.
        """
        warm_up_urls = [
            "https://www.amazon.com/",
            "https://www.amazon.com/books-used-books-textbooks/b/?ie=UTF8&node=283155",
            "https://www.amazon.com/Kindle-eBooks/b/?ie=UTF8&node=154606011"
        ]

        logger.info("Warming up session with preliminary requests")
        for url in warm_up_urls:
            try:
                logger.info(f"Visiting {url}")
                response = self.session.get(url, timeout=10)
                logger.info(f"Status: {response.status_code}")

                # Add random delay between requests
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                logger.warning(f"Warm-up request failed: {str(e)}")

        logger.info("Session warm-up complete")

    def _validate_response(self, soup):
        """Validate the response and raise an exception if it's not valid."""
        captcha = soup.find(id="captchacharacters")
        if captcha:
            raise Exception("Captcha detected")
        else:
            title = soup.title.string if soup.title else "No title found"
            logger.info(f"Successfully bypassed without captcha! Page title: {title}")
            self._page_title = title[:20].strip() if title != "No title found" else None

    def _get_rating_and_reviews_count(self, soup: BeautifulSoup) -> tuple[str | None, str | None]:
        """
        :return: tuple of rating and reviews count
        """
        customer_reviews_div = soup.find(id="detailBullets_averageCustomerReviews")
        if customer_reviews_div:
            rating_span = customer_reviews_div.find('span', class_='a-size-base a-color-base')
            if rating_span:
                rating = float(rating_span.text.strip())
            else:
                logger.warning("No rating span found")
                rating = None
            reviews_count_span = customer_reviews_div.find(id="acrCustomerReviewText")
            if reviews_count_span:
                reviews_count = float(reviews_count_span.text.strip().split()[0].replace(',', ''))
            else:
                logger.warning("No reviews count span found")
                reviews_count = None
            return rating, reviews_count
        else:
            logger.warning("No customer reviews div found")
            return None, None

    def _get_best_sellers_ranks(self, soup: BeautifulSoup) -> list[dict] | None:
        """
        :return: list of best sellers ranks values
        """
        def _parse_rank(rank_text: str) -> dict:
            rank_text = rank_text.replace(',', '')
            digit = re.search(r'\d+', rank_text)
            if digit:
                place = digit.group()
                rank_name = rank_text.replace(place, '').replace("#", '').strip()
                return {'place': place, 'rank_name': rank_name}
            else:
                return {'place': None, 'rank_name': rank_text}
            
        ranks_ul = soup.find('h2', string='Product details').find_next_sibling(id='detailBullets_feature_div').find_next_sibling('ul')
        first_rank_span = ranks_ul.find_next('span', class_='a-text-bold',)
        if first_rank_span and first_rank_span.text.strip() == 'Best Sellers Rank:':
            first_rank_value = first_rank_span.next_sibling.text.strip()
            # find all other ranks
            rankings = [_parse_rank(first_rank_value)]
            sub_ranks = ranks_ul.find('ul', class_="zg_hrsr").find_all('li')
            for sub_rank in sub_ranks:
                sub_rank_text = sub_rank.get_text(strip=True)
                rankings.append(_parse_rank(sub_rank_text))
            return rankings
        else:
            logger.warning("No \"Best Sellers Rank\" ul element found")
            return None

    def _get_popular_reviews(self, soup: BeautifulSoup) -> list[dict] | None:
        reviews_potential_containers_ids = ["cm-cr-dp-review-list", "cm-cr-global-review-list"]
        reviews = []

        for review_ul_container in reviews_potential_containers_ids:
            reviews_ul = soup.find(id=review_ul_container)
            if reviews_ul:
                items = reviews_ul.find_all('li')
                for item in items:
                    reviewer_span = item.find('span', class_='a-profile-name')
                    reviewer_name = reviewer_span.get_text(strip=True) if reviewer_span else None
                    starts_span = item.find('span', class_='a-icon-alt')
                    starts_value = starts_span.get_text(strip=True) if starts_span else None

                    # review_title_span = item.find('span', class_='cr-original-review-content')
                    review_title_span = item.find('span', class_='a-letter-space').find_next_sibling('span')
                    if not review_title_span:
                        review_title_span = item.find('span', class_='cr-translated-review-content')
                    review_title = review_title_span.get_text(strip=True) if review_title_span else None

                    review_content_span = item.find('span', {
                        'data-hook': 'review-body',
                        'class': 'a-size-base review-text'
                    })
                    review_content = review_content_span.find(class_='cr-original-review-content')
                    if not review_content:
                        review_content_div = review_content_span.find(
                            'div', {
                                'data-hook': 'review-collapsed',
                                'class': 'a-expander-content reviewText review-text-content a-expander-partial-collapse-content'
                            }
                        )
                        if not review_content_div:
                            review_content = None
                        else:
                            review_content = review_content_div.find('span')
                    review_content_text = review_content.get_text(strip=True) if review_content else None
                    reviews.append(
                        {
                            'reviewer_name': reviewer_name,
                            'starts_value': starts_value,
                            'review_title': review_title,
                            'review_content': review_content_text,
                        }
                    )
        return reviews

    def _parse_page(self, page_content: str) -> ParsedResult:
        """Parse the page and return the content."""
        soup = BeautifulSoup(page_content, 'html.parser')
        self._validate_response(soup)
        if not self.HTML_PAGES_DATA.exists():
            self.HTML_PAGES_DATA.mkdir()
        if self._page_title:
            content_filename = self.HTML_PAGES_DATA / f'{self._page_title}.html'
        else:
            content_filename = str(datetime.now())
        with open(content_filename, 'w') as f:
            f.write(page_content)
        try:
            rating, reviews_count = self._get_rating_and_reviews_count(soup)
        except Exception as e:
            logger.exception(f"Error getting rating and reviews count", exc_info=e)
            rating, reviews_count = None, None
        try:
            best_sellers_ranks = self._get_best_sellers_ranks(soup)
        except Exception as e:
            logger.exception(f"Error getting best sellers ranks", exc_info=e)
            best_sellers_ranks = None
        try:
            reviews = self._get_popular_reviews(soup)
        except Exception as e:
            logger.exception(f"Error getting popular reviews", exc_info=e)
            reviews = None
        data = ParsedResult(
            rating=float(rating) if rating else None,
            reviews_count=int(reviews_count) if reviews_count else None,
            best_sellers_ranks=best_sellers_ranks if best_sellers_ranks else None,
            reviews=reviews if reviews else None,
        )
        logger.info('Successfully parsed page, data: %s', data)
        return data
    
    def parse_amazon_book(self, url: str) -> ParsedResult:
        """Parse the Amazon book page and return the data."""
        html_content = self.fetch_page(url)
        if not html_content:
            raise Exception("Failed to fetch data")
        else:
            return self._parse_page(html_content)

