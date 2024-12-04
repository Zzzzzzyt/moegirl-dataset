import shutil
import time
from tqdm import tqdm
import requests
import urllib.parse
from bs4 import BeautifulSoup
from urllib3 import Retry
from requests.adapters import HTTPAdapter

requests.adapters.DEFAULT_RETRIES = 3

global_session = requests.Session()
retry = Retry(total=10, backoff_factor=3, backoff_max=10)
global_session.mount('https', HTTPAdapter(max_retries=retry))
global_session.mount('http', HTTPAdapter(max_retries=retry))


def safe_get(
    url: str,
    bar: tqdm = None,
    headers={},
    cookies={},
    timeout: float = 10,
    cooldown: float = 3,
    verbose: bool = True,
    session: requests.Session = None,
) -> requests.Response:
    if not session:
        global global_session
        session = global_session
    url_readable = urllib.parse.unquote(url)
    if verbose:
        if bar:
            bar.write('GET: {} '.format(url_readable), end='')
        else:
            print('GET: {} '.format(url_readable), end='')
    r = session.get(url, headers=headers, cookies=cookies, timeout=timeout)
    r.encoding = 'utf-8'
    elapsed = r.elapsed.total_seconds()
    if verbose:
        if bar:
            bar.write('{} in {:.3f}s'.format(r.status_code, elapsed))
        else:
            print('{} in {:.3f}s'.format(r.status_code, elapsed))
    if r.status_code != 200:
        if elapsed < cooldown:
            time.sleep(cooldown - elapsed)
            raise requests.HTTPError(request=r.request, response=r)
        raise RuntimeError(r)
    if elapsed < cooldown:
        time.sleep(cooldown - elapsed)
    return r


def safe_download(
    url: str,
    path: str,
    bar: tqdm = None,
    headers={},
    cookies={},
    timeout: float = 10,
    cooldown: float = 3,
    verbose: bool = True,
    session: requests.Session = None,
):
    if not session:
        global global_session
        session = global_session
    url_readable = urllib.parse.unquote(url)
    r = session.get(url, stream=True, headers=headers, cookies=cookies, timeout=timeout)
    if verbose:
        if bar:
            bar.write('Download {} '.format(url_readable), end='')
        else:
            print('Download {} '.format(url_readable), end='')
    if r.status_code != 200:
        if verbose:
            if bar:
                bar.write('ERROR: {}'.format(r.status_code))
            else:
                print('ERROR: {}'.format(r.status_code))
    else:
        with open(path, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
    elapsed = r.elapsed.total_seconds()
    if verbose:
        if bar:
            bar.write('{:.3f}s'.format(elapsed))
        else:
            print('{:.3f}s'.format(elapsed))
    if elapsed < cooldown:
        time.sleep(cooldown - elapsed)
    return r


def safe_soup(
    url: str,
    bar: tqdm = None,
    headers={},
    cookies={},
    timeout: float = 10,
    cooldown: float = 3,
    verbose: bool = True,
    session: requests.Session = None,
) -> BeautifulSoup:
    return BeautifulSoup(
        safe_get(
            url,
            bar=bar,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            cooldown=cooldown,
            verbose=verbose,
            session=session,
        ).text,
        'html.parser',
    )


def title_to_url(title):
    return urllib.parse.quote(title.replace(' ', '_'))
