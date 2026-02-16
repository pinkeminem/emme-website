import json
from flask import Blueprint, render_template, redirect
from models import get_content, get_rows

public = Blueprint('public', __name__)


@public.route('/')
def index():
    nav_links = get_content('index', 'nav_links', [
        {'label': 'music', 'href': '/music'},
        {'label': 'live', 'href': '/live'},
        {'label': 'shop', 'href': '/shop'},
        {'label': 'about', 'href': '/about'},
        {'label': 'contact', 'href': '/contact'},
    ])
    social_links = get_content('index', 'social_links', [
        {'label': 'instagram', 'url': 'https://www.instagram.com/emme.emme.emme.emme/'},
        {'label': 'bandcamp', 'url': 'https://3mm3.bandcamp.com/'},
        {'label': 'soundcloud', 'url': 'https://soundcloud.com/3m_m3'},
        {'label': 'youtube', 'url': 'https://www.youtube.com/@emmemme'},
    ])
    mobile_links = get_content('index', 'mobile_links', [
        {'label': 'music', 'href': '/music'},
        {'label': 'bandcamp', 'href': 'https://3mm3.bandcamp.com/', 'external': True},
        {'label': 'soundcloud', 'href': 'https://soundcloud.com/3m_m3', 'external': True},
        {'label': 'youtube', 'href': 'https://www.youtube.com/@emmemme', 'external': True},
        {'label': 'live', 'href': '/live'},
        {'label': 'shop', 'href': '/shop'},
        {'label': 'about', 'href': '/about'},
        {'label': 'contact', 'href': '/contact'},
    ])
    return render_template('index.html',
                           nav_links=nav_links,
                           social_links=social_links,
                           mobile_links=mobile_links)


@public.route('/about')
def about():
    bio = get_content('about', 'bio', {
        'html': '<p>Raised on a combination of punk, electronic, noise, and theater. Emme fuses harsh vocals with heavy, detailed lighting and sound design for immersive performances that touch on themes of death, tragedy, and horror. Originally from Los Angeles, Emme has lived in New York and Portland, where she quickly rose to prominence as a pivotal underground artist. Now relocated to Berlin, she is expanding her world through the use of new mediums and collaborations. Her first piece, "Heaven Help Me" began as an underground noise show and has been performed at <span class="highlight">CTM</span>, <span class="highlight">The Venice Biennale</span>, <span class="highlight">LUFF</span>, and many others.</p>'
    })
    stage_bio = get_content('about', 'stage_bio', {
        'html': '<p>beyond music, emme brings technical expertise to theatrical and live event production. trained in lighting design and stage management, with experience spanning experimental theatre, live performance, and large-scale events.</p>'
    })
    skills = get_content('about', 'skills', [
        'lighting design & programming',
        'stage management',
        'production coordination',
        'technical direction',
        'live event production',
        'dmx & lighting control systems',
    ])
    credits = get_content('about', 'credits', [
        {'title': 'Iceland', 'role': 'Assistant Lighting Designer', 'venue': 'La MaMa ETC, NYC'},
        {'title': 'PORT SF', 'role': 'Lighting Designer', 'venue': 'New Expressive Works, Portland'},
        {'title': 'Doc Martens Anniversary', 'role': 'Director of Production', 'venue': 'Daemon Concept, Berlin'},
    ])
    return render_template('about.html', bio=bio, stage_bio=stage_bio,
                           skills=skills, credits=credits)


@public.route('/contact')
def contact():
    return render_template('contact.html')


@public.route('/gallery')
def gallery():
    images = get_rows('gallery_images')
    if not images:
        images = [
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
    return render_template('gallery.html', images=images)


@public.route('/live')
def live():
    shows = get_rows('shows')
    videos = get_rows('live_videos')
    if not videos:
        videos = [
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
    return render_template('live.html', shows=shows, videos=videos)


@public.route('/music')
def music():
    releases = get_rows('releases')
    if not releases:
        releases = [
            {'title': 'heaven help me', 'cover_image': 'images/albums/heaven-help-me.jpg', 'bandcamp_url': 'https://3mm3.bandcamp.com/album/heaven-help-me'},
            {'title': 'heaven help me (instrumentals)', 'cover_image': 'images/albums/heaven-help-me-instrumentals.jpg', 'bandcamp_url': 'https://3mm3.bandcamp.com/album/heaven-help-me-instrumentals'},
            {'title': 'tuning / opening', 'cover_image': 'images/albums/tuning-opening.jpg', 'bandcamp_url': 'https://3mm3.bandcamp.com/album/tuning-opening'},
            {'title': 'help me', 'cover_image': 'images/albums/help-me.jpg', 'bandcamp_url': 'https://3mm3.bandcamp.com/album/help-me'},
            {'title': 'heaven', 'cover_image': 'images/albums/heaven.jpg', 'bandcamp_url': 'https://3mm3.bandcamp.com/album/heaven'},
            {'title': 'i close my eyes', 'cover_image': 'images/albums/i-close-my-eyes.jpg', 'bandcamp_url': 'https://3mm3.bandcamp.com/album/i-close-my-eyes'},
        ]
    tracks = get_rows('soundcloud_tracks')
    if not tracks:
        tracks = [
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
            {'title': 'coração pt. 3', 'url': 'https://soundcloud.com/3m_m3/coracao-pt-3'},
            {'title': 'coração pt. 1 & 2', 'url': 'https://soundcloud.com/3m_m3/coracao-1-n-2'},
            {'title': 'how my blood boils', 'url': 'https://soundcloud.com/3m_m3/how-my-blood-boils'},
            {'title': 'safety (alternate)', 'url': 'https://soundcloud.com/3m_m3/safety-alternate-version'},
            {'title': 'safety', 'url': 'https://soundcloud.com/3m_m3/safety'},
        ]
    wip = get_content('music', 'wip', {
        'title': 'my body as a shield',
        'cover': 'images/soundcloud/mbaas.jpg',
        'url': 'https://soundcloud.com/3m_m3/sets/mbaas-demos/s-Lj3hsFM6O93',
    })
    listen_links = get_content('music', 'listen_links', [
        {'label': 'bandcamp', 'url': 'https://3mm3.bandcamp.com/'},
        {'label': 'soundcloud', 'url': 'https://soundcloud.com/3m_m3'},
        {'label': 'youtube', 'url': 'https://www.youtube.com/@emmemme'},
    ])
    return render_template('music.html', releases=releases, tracks=tracks,
                           wip=wip, listen_links=listen_links)


@public.route('/shop')
def shop():
    return redirect('https://shop.emme-em.me/')


@public.route('/blog')
def blog():
    posts = get_rows('blog_posts')
    if not posts:
        posts = [
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
    return render_template('blog.html', posts=posts)


@public.route('/lighting')
def lighting():
    shows = get_rows('lighting_shows')
    if not shows:
        shows = [
            {
                'role': 'Assistant Lighting Designer', 'title': 'Iceland',
                'venue': 'La MaMa Experimental Theatre Club', 'location': 'New York, NY',
                'links_json': json.dumps([
                    {'label': 'la mama', 'url': 'https://www.lamama.org/shows/iceland-2023'},
                    {'label': 'dc theater arts', 'url': 'https://dctheaterarts.org/2023/03/28/myth-and-nature-guide-a-destined-human-romance-in-iceland-at-nycs-la-mama/'},
                ]),
            },
            {
                'role': 'Lighting Designer', 'title': 'PORT SF',
                'venue': 'New Expressive Works', 'location': 'Portland, OR',
                'links_json': json.dumps([
                    {'label': 'fact/sf', 'url': 'https://factsf.org/port'},
                ]),
            },
            {
                'role': 'Director of Production', 'title': 'Doc Martens Anniversary Party',
                'venue': 'Daemon Concept', 'location': 'Berlin, DE',
                'links_json': '[]',
            },
        ]
    # Parse links_json for template
    for show in shows:
        if isinstance(show.get('links_json'), str):
            show['links'] = json.loads(show['links_json'])
        else:
            show['links'] = show.get('links_json', [])

    photos = get_rows('lighting_photos')
    if not photos:
        photos = [
            {'filename': 'images/lighting/biennale.jpg', 'alt_text': 'Lighting work'},
            {'filename': 'images/lighting/emme-15.jpg', 'alt_text': 'Lighting work'},
            {'filename': 'images/lighting/emme-17.jpg', 'alt_text': 'Lighting work'},
        ]
    return render_template('lighting.html', shows=shows, photos=photos)


@public.route('/archive')
def archive():
    articles = get_rows('archive_articles', order_by='year DESC, id')
    # Group by year
    years = {}
    for a in articles:
        y = a['year']
        if y not in years:
            years[y] = []
        years[y].append(a)
    return render_template('archive.html', years=years, articles=articles)
