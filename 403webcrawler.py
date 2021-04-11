import argparse
import threading
import sys
import datetime
from time import sleep
import requests
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(description='Welcome to 403 WebCrawler! Please refer to https://github.com/guilherme-sal/403webcrawler for more information.')
parser.add_argument('host', help='Target host')
parser.add_argument('-t', '--threads', type=int, default=5, help='Number of threads')
parser.add_argument('-v', '--verbose', action='store_true', help='Print crawling statuses')
parser.add_argument('-o', '--output', type=str, help='Output txt file')
parser.add_argument('-r', '--headers', type=str, help='Uses headers in file')
parser.add_argument('-s', '--search', type=str, help='Search for terms in links')

ROOT_URL = None
NON_CRAWLED_LINKS = []
CRAWLED_LINKS = []
EXTERNAL_LINKS = []
SEARCH_LINKS = []
MAIL = []
PHONE = []
HEADER = {}


def format_root_url(root_url):

    try:
        root_url = str(root_url)
        root_url = root_url.strip()
        if root_url[-1:] == '/':
            root_url = root_url[:-1]
            return root_url
        else:
            return root_url

    except:
        pass


def request():

    try:
        url = NON_CRAWLED_LINKS.pop(0)
        if url in CRAWLED_LINKS:
            pass
        else:
            CRAWLED_LINKS.append(url)
            response = requests.get(url, headers=HEADER)
            if args.verbose:
                print(f'Crawling {url}... {response.status_code}')
            else:
                pass
            return response.text

    except KeyboardInterrupt:
        sys.exit(0)

    except Exception as e:
        pass


def get_links(html):
    links = []
    try:
        soup = BeautifulSoup(html, "html.parser")
        tags_a = soup.find_all("a", href=True)
        for tag in tags_a:
            link = tag["href"]
            links.append(link)

        return links

    except Exception as e:
        pass


def format_links(links_list, ROOT_URL):
    formated_links = []
    try:
        for link in links_list:

            if link[0] == '/':
                link_formated = ROOT_URL + link
                formated_links.append(link_formated)

            elif link[:3] == 'tel':
                PHONE.append(link)

            elif link[:4] == 'mail':
                MAIL.append(link)

            elif (link[:3] != 'htt') & (link[:3] != 'www'):
                link_formated = ROOT_URL + '/' + link
                formated_links.append(link_formated)

            else:
                formated_links.append(link)
        return formated_links

    except Exception as e:
        pass


def set_links(links_list):
    try:
        set_links = set(links_list)
        return set_links

    except Exception as e:
        pass


def check_domain(set_links):
    checked_list =[]
    try:
        links_list = list(set_links)
        for link in links_list:
            if ROOT_URL in link:
                checked_list.append(link)
            else:
                EXTERNAL_LINKS.append(link)
        return checked_list

    except:
        pass


def crawl_check(links_list):
    try:
        for link in links_list:
            if link not in CRAWLED_LINKS:
                NON_CRAWLED_LINKS.append(link)
            else:
                pass

    except Exception as e:
        pass


def crawl_routine():
    requested_html = request()
    requested_links = get_links(requested_html)
    requested_formated_links = format_links(requested_links, ROOT_URL)
    requested_set_links = set_links(requested_formated_links)
    requested_checked_domains = check_domain(requested_set_links)
    crawl_check(requested_checked_domains)


def search_terms():
    terms_list = args.search.split(',')
    for term in terms_list:
        for link in CRAWLED_LINKS:
            if term in link:
                SEARCH_LINKS.append(link)
        else:
            pass


if __name__ == "__main__":

    args = parser.parse_args()

    if args.headers:
        with open(f'{args.headers}', 'r') as headers_file:
            for line in headers_file:
                key = line.split(':')[0].strip()
                value = line.split(':')[1].strip()
                HEADER[key] = value

    else:
        HEADER = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"}

    formated_root_url = format_root_url(args.host)
    ROOT_URL = formated_root_url
    NON_CRAWLED_LINKS.append(ROOT_URL)

    print('\n////////////////////////////////////////////////////////////////////')
    print(f"Started crawling host {ROOT_URL} at {datetime.datetime.now().strftime('%Y/%m/%d - %H:%M')}")
    print(f'Number of threads: {args.threads}')
    print(f'Verbose: {args.verbose}')
    print(f'Output: {args.output}')
    crawl_routine()

    while len(NON_CRAWLED_LINKS) > 0:

        THREADS = []
        for i in range(args.threads):
            t = threading.Thread(target=crawl_routine)
            THREADS.append(t)

        for t in THREADS:
            t.start()

        for t in THREADS:
            t.join()

    print(f"Stoped crawling host {ROOT_URL} at {datetime.datetime.now().strftime('%Y/%m/%d - %H:%M')}")

    if CRAWLED_LINKS:
        founded_internal_links = list(set(CRAWLED_LINKS))
        print('\n//////////////////////////////////////////')
        print(f'FOUNDED INTERNAL LINKS: {len(founded_internal_links)}')
        sleep(1)
        for link in founded_internal_links:
            print(f'{link}')

        if args.search:
            print('\n//////////////////////////////////////////')
            search_terms()
            search_terms_link_list = (set(SEARCH_LINKS))
            print(f'FOUNDED TERMS IN LINKS: {len(search_terms_link_list)}')
            sleep(1)
            for link in search_terms_link_list:
                print(f'{link}')

    if EXTERNAL_LINKS:
        founded_external_links =  list(set(EXTERNAL_LINKS))
        print('\n//////////////////////////////////////////')
        print(f'FOUNDED EXTERNAL LINKS: {len(founded_external_links)}')
        sleep(1)
        for link in founded_external_links:
            print(f'{link}')

    if MAIL:
        founded_mail = list(set(MAIL))
        print('\n//////////////////////////////////////////')
        print(f'FOUNDED MAIL: {len(founded_mail)}')
        sleep(1)
        for link in founded_mail:
            print(f'{link}')

    if PHONE:
        founded_phones = list(set(PHONE))
        print('\n//////////////////////////////////////////')
        print(f'FOUNDED PHONES: {len(founded_phones)}')
        sleep(1)
        for link in founded_phones:
            print(f'{link}')

    if args.output:
        print(f'\n Saving output: {args.output}...')
        with open(f'{args.output}', 'w') as file:
            if CRAWLED_LINKS:
                file.write(('//////////////////////////////////////////\n'))
                file.write(f'INTERNAL LINKS FOUNDED: {len(founded_internal_links)}\n')
                for line in founded_internal_links:
                    file.write(f'{line} \n')
            if SEARCH_LINKS:
                file.write(('\n//////////////////////////////////////////\n'))
                file.write(f'SEARCH TERMS FOUNDED: {len(search_terms_link_list)}\n')
                for line in search_terms_link_list:
                    file.write(f'{line} \n')
            if EXTERNAL_LINKS:
                file.write(('\n//////////////////////////////////////////\n'))
                file.write(f'EXTERNAL LINKS FOUNDED: {len(founded_external_links)}\n')
                for line in founded_external_links:
                    file.write(f'{line} \n')
            if MAIL:
                file.write(('\n//////////////////////////////////////////\n'))
                file.write(f'MAIL FOUNDED: {len(founded_mail)}\n')
                for line in founded_mail:
                    file.write(f'{line} \n')
            if PHONE:
                file.write(('\n//////////////////////////////////////////\n'))
                file.write(f'PHONES FOUNDED: {len(founded_phones)}\n')
                for line in founded_phones:
                    file.write(f'{line} \n')
            else:
                pass

    print("END")
