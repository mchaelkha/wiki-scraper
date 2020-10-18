from collections import defaultdict
import urllib.parse
import mechanicalsoup
import json
import argparse
import re

out = []

def init_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    return parser

def convert_date(date):
    def convert_month(month):
        if month == "January":
            return "01"
        elif month == "February":
            return "02"
        elif month == "March":
            return "03"
        elif month == "April":
            return "04"
        elif month == "May":
            return "05"
        elif month == "June":
            return "06"
        elif month == "July":
            return "07"
        elif month == "August":
            return "08"
        elif month == "September":
            return "09"
        elif month == "October":
            return "10"
        elif month == "November":
            return "11"
        elif month == "December":
            return "12"
    date.replace(u'\xa0', " ")
    date_parts = re.split("\s", date)
    day = ""
    month = ""
    year = ""
    for part in date_parts:
        if 'a' in part or 'e' in part or 'i' in part or 'u' in part:
            month = part
        elif len(part) == 4:
            year = part
        else:
            if ',' in part:
                day = part[:-1]
            else:
                day = part
    month = convert_month(month)
    return "-".join([year, month, day])

def scrape(browser, url):
    resp = browser.open(url)
    soup = browser.get_current_page()

    contributor = soup.find("div", class_="contributor")
    artist_name = contributor.contents[0].contents[0]

    album = soup.find("th", class_="summary album").contents[0]
    date = soup.find("td", class_="published")
    release_date = convert_date(date.contents[0])
    genre_list = soup.find("td", class_="category hlist").contents[0]

    genres = []
    for item in genre_list.contents[1]:
        if hasattr(item, 'contents'):
            genres.append(item.contents[0].contents[0].title())

    track_list = soup.find("table", class_="tracklist")
    track_table = track_list.contents[0].contents
    track_info = []
    for i in range(1, len(track_table) - 1):
        track_length = track_table[i].contents[4].contents[0]
        track_no = int(track_table[i].contents[0].contents[0][:-1])
        track_title = ""
        # If anchor element in track title
        if len(track_table[i].contents[1].contents) > 1:
            track_title = track_table[i].contents[1].contents[0][1:-2]
        else:
            track_title = track_table[i].contents[1].contents[0][1:-1]
        track = {
            "Title": track_title,
            "Length": track_length,
            "Track": track_no
        }
        track_info.append(track)

    info = {}
    info["Artist"] = {
        "FirstName": artist_name
    }
    info["Album"] = {
        "Title": album,
        "ReleaseDate": release_date,
        "Genre": genres
    }
    info["Songs"] = track_info

    return json.dumps(info, indent=2)


def main():
    parser = init_parser()
    args = parser.parse_args()
    url = args.url

    browser = mechanicalsoup.StatefulBrowser();
    json = scrape(browser, url)
    print(json)


if __name__ == '__main__':
    main()
