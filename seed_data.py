#!/usr/bin/env python3
"""
Seed the emme.db database with all default data from public.py fallbacks
and parse archive.html for archive_articles.
"""

import json
import os
import sys
from html.parser import HTMLParser

# Ensure we can import from the project directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import get_db, init_db


# ---------------------------------------------------------------------------
# Archive HTML parser
# ---------------------------------------------------------------------------

class ArchiveParser(HTMLParser):
    """Parse archive.html to extract article data."""

    def __init__(self):
        super().__init__()
        self.articles = []
        self.current_year = None
        self.current_article = {}

        # State tracking
        self._in_year_header = False
        self._in_article_date = False
        self._in_article_title = False
        self._in_article_category = False
        self._current_data = ''

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get('class', '')

        if tag == 'div' and 'year-header' in cls:
            self._in_year_header = True
            self._current_data = ''

        elif tag == 'span' and 'article-date' in cls:
            self._in_article_date = True
            self._current_data = ''

        elif tag == 'a' and 'article-title' in cls:
            self._in_article_title = True
            self._current_data = ''
            self.current_article['url'] = attrs_dict.get('href', '')

        elif tag == 'span' and 'article-category' in cls:
            self._in_article_category = True
            self._current_data = ''

    def handle_endtag(self, tag):
        if self._in_year_header and tag == 'div':
            self._in_year_header = False
            try:
                self.current_year = int(self._current_data.strip())
            except ValueError:
                pass

        elif self._in_article_date and tag == 'span':
            self._in_article_date = False
            self.current_article['month_day'] = self._current_data.strip()

        elif self._in_article_title and tag == 'a':
            self._in_article_title = False
            self.current_article['title'] = self._current_data.strip()

        elif self._in_article_category and tag == 'span':
            self._in_article_category = False
            self.current_article['category'] = self._current_data.strip()

            # We have a complete article -- save it
            if self.current_year is not None and self.current_article.get('title'):
                self.articles.append({
                    'year': self.current_year,
                    'month_day': self.current_article.get('month_day', ''),
                    'title': self.current_article.get('title', ''),
                    'url': self.current_article.get('url', ''),
                    'category': self.current_article.get('category', ''),
                })
            self.current_article = {}

    def handle_data(self, data):
        if self._in_year_header:
            self._current_data += data
        elif self._in_article_date:
            self._current_data += data
        elif self._in_article_title:
            self._current_data += data
        elif self._in_article_category:
            self._current_data += data


def parse_archive(filepath):
    """Read and parse archive.html, return list of article dicts."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    parser = ArchiveParser()
    parser.feed(html)
    return parser.articles


# ---------------------------------------------------------------------------
# Hardcoded seed data (matches fallback defaults in routes/public.py)
# ---------------------------------------------------------------------------

GALLERY_IMAGES = [
    {'filename': 'images/gallery/emme-libretto-white-face.png', 'alt_text': 'libretto white face'},
    {'filename': 'images/gallery/emme-photoshoot-1.jpg', 'alt_text': 'photoshoot'},
    {'filename': 'images/gallery/emme-luff-1.jpg', 'alt_text': 'LUFF festival'},
    {'filename': 'images/gallery/emme-venice-biennale.jpg', 'alt_text': 'Venice Biennale'},
    {'filename': 'images/gallery/emme-frost-face.png', 'alt_text': 'frost face'},
    {'filename': 'images/gallery/emme-photoshoot-2.jpg', 'alt_text': 'photoshoot'},
    {'filename': 'images/gallery/emme-denver-1.jpg', 'alt_text': 'Denver show'},
    {'filename': 'images/gallery/emme-collision-edit.png', 'alt_text': 'collision'},
    {'filename': 'images/gallery/emme-photoshoot-3.jpg', 'alt_text': 'photoshoot'},
    {'filename': 'images/gallery/emme-luff-2.jpg', 'alt_text': 'LUFF festival'},
    {'filename': 'images/gallery/emme-hand-face.png', 'alt_text': 'hand face'},
    {'filename': 'images/gallery/emme-photoshoot-4.jpg', 'alt_text': 'photoshoot'},
    {'filename': 'images/gallery/emme-denver-2.jpg', 'alt_text': 'Denver show'},
    {'filename': 'images/gallery/emme-press-hauntedreverie.jpg', 'alt_text': 'press photo'},
    {'filename': 'images/gallery/emme-photoshoot-5.jpg', 'alt_text': 'photoshoot'},
    {'filename': 'images/gallery/emme-luff-3.jpg', 'alt_text': 'LUFF festival'},
    {'filename': 'images/gallery/emme wild things.png', 'alt_text': 'wild things'},
    {'filename': 'images/gallery/emme-photoshoot-6.jpg', 'alt_text': 'photoshoot'},
    {'filename': 'images/gallery/emme-denver-3.jpg', 'alt_text': 'Denver show'},
    {'filename': 'images/gallery/emme-hhm-flyer.png', 'alt_text': 'Heaven Help Me flyer'},
    {'filename': 'images/gallery/emme-photoshoot-7.jpg', 'alt_text': 'photoshoot'},
    {'filename': 'images/gallery/emme flowers floating.png', 'alt_text': 'flowers floating'},
    {'filename': 'images/gallery/emme-cd-release-1.jpg', 'alt_text': 'CD release flyer'},
    {'filename': 'images/gallery/emme-cd-release-2.jpg', 'alt_text': 'CD release flyer'},
    {'filename': 'images/gallery/emme 2025 tour flyer text.png', 'alt_text': '2025 tour flyer'},
    {'filename': 'images/gallery/emme 4 final shows.png', 'alt_text': 'final shows'},
    {'filename': 'images/gallery/emme emo.png', 'alt_text': 'emo'},
    {'filename': 'images/gallery/emme hamilton.png', 'alt_text': 'hamilton'},
    {'filename': 'images/gallery/emme hell.png', 'alt_text': 'hell'},
    {'filename': 'images/gallery/emme magali.png', 'alt_text': 'magali'},
    {'filename': 'images/gallery/emme puzzle.png', 'alt_text': 'puzzle'},
    {'filename': 'images/gallery/emme terrible.png', 'alt_text': 'terrible'},
    {'filename': 'images/gallery/emme cassete a side cover i close my eyes heaven.png', 'alt_text': 'cassette a side'},
    {'filename': 'images/gallery/emme cassete b side cover help me .png', 'alt_text': 'cassette b side'},
    {'filename': 'images/gallery/EMME STICKER LOGO.png', 'alt_text': 'sticker logo'},
]

LIVE_VIDEOS = [
    {'filename': 'videos/biennale.mov', 'title': 'Venice Biennale', 'location': 'Venice, IT'},
    {'filename': 'videos/luff.mp4', 'title': 'LUFF', 'location': 'Lausanne, CH'},
    {'filename': 'videos/vienna.mov', 'title': 'Rhiz', 'location': 'Vienna, AT'},
    {'filename': 'videos/nyc-grove.mov', 'title': 'The Grove', 'location': 'New York, NY'},
    {'filename': 'videos/nyc-purg.mov', 'title': 'Purgatory', 'location': 'New York, NY'},
    {'filename': 'videos/nyc-rash.mov', 'title': 'Rash', 'location': 'New York, NY'},
    {'filename': 'videos/pdx-beach.mov', 'title': 'A Beach', 'location': 'Portland, OR'},
    {'filename': 'videos/vienna-2.mov', 'title': 'Rhiz II', 'location': 'Vienna, AT'},
    {'filename': 'videos/luff-2.mov', 'title': 'LUFF II', 'location': 'Lausanne, CH'},
    {'filename': 'videos/nyc-purg-2.mov', 'title': 'Purgatory II', 'location': 'New York, NY'},
    {'filename': 'videos/zurich-umbo.mov', 'title': 'Umbo', 'location': 'Zurich, CH'},
    {'filename': 'videos/zurich-umbo-2.mov', 'title': 'Umbo II', 'location': 'Zurich, CH'},
    {'filename': 'videos/nyc-hart.mov', 'title': 'Hart Bar', 'location': 'New York, NY'},
    {'filename': 'videos/nyc-hart-2.mov', 'title': 'Hart Bar II', 'location': 'New York, NY'},
    {'filename': 'videos/nyc-pecos.mov', 'title': 'Pecos', 'location': 'New York, NY'},
    {'filename': 'videos/nyc-pecos-2.mov', 'title': 'Pecos II', 'location': 'New York, NY'},
    {'filename': 'videos/pdx-beach-2.mov', 'title': 'A Beach II', 'location': 'Portland, OR'},
    {'filename': 'videos/pdx-beach-3.mov', 'title': 'A Beach III', 'location': 'Portland, OR'},
    {'filename': 'videos/nyc-rash-2.mov', 'title': 'Rash II', 'location': 'New York, NY'},
    {'filename': 'videos/vienna-3.mov', 'title': 'Rhiz III', 'location': 'Vienna, AT'},
    {'filename': 'videos/luff-3.mov', 'title': 'LUFF III', 'location': 'Lausanne, CH'},
    {'filename': 'videos/nyc-grove-2.mov', 'title': 'The Grove II', 'location': 'New York, NY'},
]

RELEASES = [
    {'title': 'heaven help me', 'cover_image': 'images/albums/heaven-help-me.jpg', 'bandcamp_url': 'https://3mm3.bandcamp.com/album/heaven-help-me'},
    {'title': 'heaven help me (instrumentals)', 'cover_image': 'images/albums/heaven-help-me-instrumentals.jpg', 'bandcamp_url': 'https://3mm3.bandcamp.com/album/heaven-help-me-instrumentals'},
    {'title': 'tuning / opening', 'cover_image': 'images/albums/tuning-opening.jpg', 'bandcamp_url': 'https://3mm3.bandcamp.com/album/tuning-opening'},
    {'title': 'help me', 'cover_image': 'images/albums/help-me.jpg', 'bandcamp_url': 'https://3mm3.bandcamp.com/album/help-me'},
    {'title': 'heaven', 'cover_image': 'images/albums/heaven.jpg', 'bandcamp_url': 'https://3mm3.bandcamp.com/album/heaven'},
    {'title': 'i close my eyes', 'cover_image': 'images/albums/i-close-my-eyes.jpg', 'bandcamp_url': 'https://3mm3.bandcamp.com/album/i-close-my-eyes'},
]

SOUNDCLOUD_TRACKS = [
    {'title': 'black kray x malibu', 'url': 'https://soundcloud.com/3m_m3/black-kray-x-malibu'},
    {'title': 'badman vip', 'url': 'https://soundcloud.com/3m_m3/badman-vip-vip-vip'},
    {'title': 'a song to replace shame', 'url': 'https://soundcloud.com/3m_m3/a-song-to-replace-shame'},
    {'title': 'spit on me', 'url': 'https://soundcloud.com/3m_m3/spit-on-me'},
    {'title': 'doe in the park // not enough', 'url': 'https://soundcloud.com/3m_m3/doe-in-the-park-not-enough'},
    {'title': 'for nat', 'url': 'https://soundcloud.com/3m_m3/for-nat'},
    {'title': 'counting worms', 'url': 'https://soundcloud.com/3m_m3/counting-worms'},
    {'title': 'smoggy', 'url': 'https://soundcloud.com/3m_m3/smoggy'},
    {'title': 'pathetic', 'url': 'https://soundcloud.com/3m_m3/pathetic'},
    {'title': 'bite me', 'url': 'https://soundcloud.com/3m_m3/bite-me'},
    {'title': u'cora\u00e7\u00e3o pt. 3', 'url': 'https://soundcloud.com/3m_m3/coracao-pt-3'},
    {'title': u'cora\u00e7\u00e3o pt. 1 & 2', 'url': 'https://soundcloud.com/3m_m3/coracao-1-n-2'},
    {'title': 'how my blood boils', 'url': 'https://soundcloud.com/3m_m3/how-my-blood-boils'},
    {'title': 'safety (alternate)', 'url': 'https://soundcloud.com/3m_m3/safety-alternate-version'},
    {'title': 'safety', 'url': 'https://soundcloud.com/3m_m3/safety'},
]

LIGHTING_SHOWS = [
    {
        'role': 'Assistant Lighting Designer',
        'title': 'Iceland',
        'venue': 'La MaMa Experimental Theatre Club',
        'location': 'New York, NY',
        'links_json': json.dumps([
            {'label': 'la mama', 'url': 'https://www.lamama.org/shows/iceland-2023'},
            {'label': 'dc theater arts', 'url': 'https://dctheaterarts.org/2023/03/28/myth-and-nature-guide-a-destined-human-romance-in-iceland-at-nycs-la-mama/'},
        ]),
    },
    {
        'role': 'Lighting Designer',
        'title': 'PORT SF',
        'venue': 'New Expressive Works',
        'location': 'Portland, OR',
        'links_json': json.dumps([
            {'label': 'fact/sf', 'url': 'https://factsf.org/port'},
        ]),
    },
    {
        'role': 'Director of Production',
        'title': 'Doc Martens Anniversary Party',
        'venue': 'Daemon Concept',
        'location': 'Berlin, DE',
        'links_json': '[]',
    },
]

LIGHTING_PHOTOS = [
    {'filename': 'images/lighting/biennale.jpg', 'alt_text': 'Lighting work'},
    {'filename': 'images/lighting/emme-15.jpg', 'alt_text': 'Lighting work'},
    {'filename': 'images/lighting/emme-17.jpg', 'alt_text': 'Lighting work'},
]

BLOG_POSTS = [
    {
        'title': 'Machine Girl Talk Anime, Cyberpunk, and Their Craziest Live Shows',
        'url': 'https://emmmmmmmmme.wordpress.com/2018/12/13/machine-girl-talk-anime-cyberpunk-craziest-live-shows/',
        'excerpt': 'An interview with Machine Girl about their influences, touring chaos, and the intersection of hardcore, cyberpunk aesthetics, and anime culture.',
        'category': 'interview',
        'date_display': 'Dec 13, 2018',
    },
    {
        'title': 'Nest HQ Archive',
        'url': '/archive',
        'excerpt': '180+ articles written for Nest HQ covering electronic music, interviews, album reviews, premieres, and artist spotlights.',
        'category': 'archive',
        'date_display': '2014 - 2019',
    },
]


# ---------------------------------------------------------------------------
# Insert helpers
# ---------------------------------------------------------------------------

def insert_gallery_images(db, data):
    for i, img in enumerate(data):
        db.execute(
            'INSERT INTO gallery_images (filename, alt_text, sort_order) VALUES (?, ?, ?)',
            (img['filename'], img['alt_text'], i)
        )
    return len(data)


def insert_live_videos(db, data):
    for i, vid in enumerate(data):
        db.execute(
            'INSERT INTO live_videos (filename, title, location, sort_order) VALUES (?, ?, ?, ?)',
            (vid['filename'], vid['title'], vid['location'], i)
        )
    return len(data)


def insert_releases(db, data):
    for i, rel in enumerate(data):
        db.execute(
            'INSERT INTO releases (title, cover_image, bandcamp_url, sort_order) VALUES (?, ?, ?, ?)',
            (rel['title'], rel['cover_image'], rel['bandcamp_url'], i)
        )
    return len(data)


def insert_soundcloud_tracks(db, data):
    for i, trk in enumerate(data):
        db.execute(
            'INSERT INTO soundcloud_tracks (title, url, sort_order) VALUES (?, ?, ?)',
            (trk['title'], trk['url'], i)
        )
    return len(data)


def insert_lighting_shows(db, data):
    for i, show in enumerate(data):
        db.execute(
            'INSERT INTO lighting_shows (role, title, venue, location, links_json, sort_order) VALUES (?, ?, ?, ?, ?, ?)',
            (show['role'], show['title'], show['venue'], show['location'], show['links_json'], i)
        )
    return len(data)


def insert_lighting_photos(db, data):
    for i, photo in enumerate(data):
        db.execute(
            'INSERT INTO lighting_photos (filename, alt_text, sort_order) VALUES (?, ?, ?)',
            (photo['filename'], photo['alt_text'], i)
        )
    return len(data)


def insert_blog_posts(db, data):
    for i, post in enumerate(data):
        db.execute(
            'INSERT INTO blog_posts (title, url, excerpt, category, date_display, sort_order) VALUES (?, ?, ?, ?, ?, ?)',
            (post['title'], post['url'], post['excerpt'], post['category'], post['date_display'], i)
        )
    return len(data)


def insert_archive_articles(db, articles):
    for art in articles:
        db.execute(
            'INSERT INTO archive_articles (year, month_day, title, url, category) VALUES (?, ?, ?, ?, ?)',
            (art['year'], art['month_day'], art['title'], art['url'], art['category'])
        )
    return len(articles)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print('Initializing database...')
    init_db()

    db = get_db()

    # Clear existing data from all seed tables so this script is idempotent
    tables_to_clear = [
        'gallery_images', 'live_videos', 'releases', 'soundcloud_tracks',
        'lighting_shows', 'lighting_photos', 'blog_posts', 'archive_articles',
    ]
    for table in tables_to_clear:
        db.execute(f'DELETE FROM {table}')

    counts = {}

    # Insert hardcoded seed data
    counts['gallery_images'] = insert_gallery_images(db, GALLERY_IMAGES)
    counts['live_videos'] = insert_live_videos(db, LIVE_VIDEOS)
    counts['releases'] = insert_releases(db, RELEASES)
    counts['soundcloud_tracks'] = insert_soundcloud_tracks(db, SOUNDCLOUD_TRACKS)
    counts['lighting_shows'] = insert_lighting_shows(db, LIGHTING_SHOWS)
    counts['lighting_photos'] = insert_lighting_photos(db, LIGHTING_PHOTOS)
    counts['blog_posts'] = insert_blog_posts(db, BLOG_POSTS)

    # Parse archive.html and insert articles
    archive_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'archive.html')
    if os.path.exists(archive_path):
        articles = parse_archive(archive_path)
        counts['archive_articles'] = insert_archive_articles(db, articles)
    else:
        print(f'WARNING: {archive_path} not found, skipping archive articles.')
        counts['archive_articles'] = 0

    db.commit()
    db.close()

    # Report
    print('\n--- Seed Data Report ---')
    total = 0
    for table, count in counts.items():
        print(f'  {table}: {count} records')
        total += count
    print(f'\n  TOTAL: {total} records inserted')
    print('Done.')


if __name__ == '__main__':
    main()
