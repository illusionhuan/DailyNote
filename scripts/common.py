import math
import logging
import warnings
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

logger = logging.getLogger("trending")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/json,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

MULTIPLIERS = {
    "hacker_news": 1.5,
    "github": 0.5,
    "juejin": 0.5,
    "v2ex": 8.0,
    "segmentfault": 0.08,
}


def make_session():
    s = requests.Session()
    s.headers.update(HEADERS)
    s.verify = False
    retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    return s


def normalize_score(source, raw_score):
    if not raw_score or raw_score <= 0:
        return 0
    mult = MULTIPLIERS.get(source, 1.0)
    score = math.log10(max(raw_score, 1)) * 100 * mult
    return min(int(score), 1000)
