# -*- coding: utf-8 -*-
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""A list of static data"""

from __future__ import absolute_import, division, unicode_literals

# The margin at start/end to consider a video as watched
# This value is used by resumepoints and upnext
SECONDS_MARGIN = 30

# Fallback list of categories so we don't depend on web scraping only
CATEGORIES = [
    dict(name='Audiodescriptie', id='met-audiodescriptie', msgctxt=30070),
    dict(name='Cultuur', id='cultuur', msgctxt=30071),
    dict(name='Docu', id='docu', msgctxt=30072),
    dict(name='Entertainment', id='entertainment', msgctxt=30073),
    dict(name='Film', id='films', msgctxt=30074),
    dict(name='Human interest', id='human-interest', msgctxt=30075),
    dict(name='Humor', id='humor', msgctxt=30076),
    dict(name='Kinderen en jongeren', id='voor-kinderen', msgctxt=30077),
    dict(name='Koken', id='koken', msgctxt=30078),
    dict(name='Levensbeschouwing', id='levensbeschouwing', msgctxt=30087),
    dict(name='Lifestyle', id='lifestyle', msgctxt=30079),
    dict(name='Muziek', id='muziek', msgctxt=30080),
    dict(name='Nieuws en actua', id='nieuws-en-actua', msgctxt=30081),
    dict(name='Nostalgie', id='nostalgie', msgctxt=30088),
    dict(name='Series', id='series', msgctxt=30082),
    dict(name='Sport', id='sport', msgctxt=30083),
    dict(name='Talkshows', id='talkshows', msgctxt=30084),
    dict(name='Vlaamse Gebarentaal', id='met-gebarentaal', msgctxt=30085),
    dict(name='Wetenschap & natuur', id='wetenschap-en-natuur', msgctxt=30086),
]

# TODO: Find a solution for the below VRT YouTube channels
#     dict(label='VRT', url='https://www.youtube.com/channel/UCojJNXcer3yKj9Q-RWOFZuw'),
#     dict(label='VRT NU', url='https://www.youtube.com/channel/UCt3RWMlMKf5jKg5cvqxC_xA'),
#     dict(label='VRT met VGT', url='https://www.youtube.com/channel/UC5M_bvCAK3WkszBw_eCXxKQ'),

CHANNELS = [
    dict(
        id='O8',
        name='een',
        label='Eén',
        studio='Een',
        live_stream='https://www.vrt.be/vrtnu/livestream/#epgchannel=O8',
        live_stream_id='vualto_een_geo',
        youtube=[
            dict(label='Eén', url='https://www.youtube.com/user/welkombijeen'),
            dict(label='Muziek bij Eén', url='https://www.youtube.com/channel/UC7mPNmdg7ADGt0gH8xOrXpQ'),
        ],
        has_tvguide=True,
        logo='https://images.vrt.be/orig/logo/een/een_LOGO_zwart.png',
        epg_id='een.be',
        preset=1,
        vod=True,
    ),
    dict(
        id='1H',
        name='canvas',
        label='Canvas',
        studio='Canvas',
        live_stream='https://www.vrt.be/vrtnu/livestream/#epgchannel=1H',
        live_stream_id='vualto_canvas_geo',
        youtube=[
            dict(label='Canvas', url='https://www.youtube.com/user/CanvasTV'),
            dict(label='Sporza', url='https://www.youtube.com/user/SporzaOfficial'),
            dict(label='Terzake', url='https://www.youtube.com/user/terzaketv'),
        ],
        has_tvguide=True,
        logo='https://images.vrt.be/orig/logo/canvas/CANVAS_logo_lichtblauw.jpg',
        epg_id='canvas.be',
        preset=2,
        vod=True,
    ),
    dict(
        id='O9',
        name='ketnet',
        label='Ketnet',
        studio='Ketnet',
        live_stream='https://www.vrt.be/vrtnu/kanalen/ketnet/',
        live_stream_id='vualto_ketnet_geo',
        youtube=[
            dict(label='Ketnet', url='https://www.youtube.com/user/KetnetVideo'),
            dict(label='Ketnet Musical', url='https://www.youtube.com/channel/UCB90ZMfqVLgGtp3Z99h4GWg'),
            dict(label='Karrewiet', url='https://www.youtube.com/channel/UCCUHHJrtsoC1oyihO86mnMg'),
        ],
        has_tvguide=True,
        logo='https://images.vrt.be/orig/logo/ketnet/ketnet_LOGO_rood_geel.png',
        epg_id='ketnet.be',
        preset=12,
        vod=True,
    ),
    dict(
        id='',
        name='ketnet-jr',
        label='Ketnet Junior',
        studio='Ketnet Junior',
        live_stream_id='ketnet_jr',
        youtube=[
            dict(label='Ketnet Junior', url='https://www.youtube.com/channel/UCTxm_H52WlKWBEB_h7PjzFA'),
        ],
        logo='https://images.vrt.be/orig/2019/07/19/c309360a-aa10-11e9-abcc-02b7b76bf47f.png',
        epg_id='ketnetjr.be',
        preset=11,
        vod=True,
    ),
    dict(
        id='',
        name='podium19',
        label='Podium 19',
        studio='Podium 19',
        logo='https://images.vrt.be/orig/2020/12/19/53f5fa6f-4223-11eb-aae0-02b7b76bf47f.png',
        vod=True,
    ),
    dict(
        id='12',
        name='sporza',
        label='Sporza',
        studio='Sporza',
        live_stream_id='vualto_sporza_geo',
        youtube=[
            dict(label='Sporza', url='https://www.youtube.com/user/SporzaOfficial'),
        ],
        logo='https://images.vrt.be/orig/logo/sporza/sporza_logo_zwart.png',
        epg_id='sporza.be',
        preset=801,
        vod=True,
    ),
    dict(
        id='13',
        name='vrtnws',
        label='VRT NWS',
        studio='VRT NWS',
        live_stream_id='vualto_nieuws',
        # live_stream_id='vualto_journaal',
        youtube=[
            dict(label='VRT NWS', url='https://www.youtube.com/channel/UC59gT3bFTFNSqafRcluDIsQ'),
            dict(label='Terzake', url='https://www.youtube.com/user/terzaketv'),
        ],
        logo='https://images.vrt.be/orig/logos/vrtnws.png',
        epg_id='vrtnws.be',
        preset=802,
        vod=True,
    ),
    dict(
        id='11',
        name='radio1',
        label='Radio 1',
        studio='Radio 1',
        live_stream_id='vualto_radio1',
        youtube=[
            dict(label='Radio 1', url='https://www.youtube.com/user/vrtradio1'),
            dict(label='Universiteit van Vlaanderen', url='https://www.youtube.com/channel/UC7WpOKbKfzOOnD0PyUN_SYg'),
        ],
        logo='https://images.vrt.be/orig/logos/radio1.png',
        epg_id='radio1.be',
        preset=901,
        vod=True,
    ),
    dict(
        id='22',
        name='radio2',
        label='Radio 2',
        studio='Radio 2',
        live_stream_id='vualto_radio2',
        youtube=[
            dict(label='Radio 2', url='https://www.youtube.com/user/radio2inbeeld'),
            dict(label='Aha!', url='https://www.youtube.com/channel/UCa9lGLvXB-xJg3d0BjK_tIQ'),
        ],
        logo='https://images.vrt.be/orig/logos/radio2.png',
        epg_id='radio2vlb.be',
        preset=902,
        vod=True,
    ),
    dict(
        id='31',
        name='klara',
        label='Klara',
        studio='Klara',
        live_stream_id='vualto_klara',
        youtube=[
            dict(label='Klara', url='https://www.youtube.com/user/klararadio'),
            dict(label='Iedereen klassiek', url='https://www.youtube.com/channel/UCgyfqQgt5_K8_zrxHgh_J2w'),
        ],
        logo='https://images.vrt.be/orig/logos/klara.png',
        epg_id='klara.be',
        preset=903,
        vod=True,
    ),
    dict(
        id='41',
        name='stubru',
        label='Studio Brussel',
        studio='Studio Brussel',
        # live_stream='https://stubru.be/live',
        live_stream_id='vualto_stubru',
        youtube=[
            dict(label='Studio Brussel', url='https://www.youtube.com/user/StuBru'),
        ],
        logo='https://images.vrt.be/orig/2019/03/12/1e383cf5-44a7-11e9-abcc-02b7b76bf47f.png',
        epg_id='stubru.be',
        preset=904,
        vod=True,
    ),
    dict(
        id='55',
        name='mnm',
        label='MNM',
        studio='MNM',
        # live_stream='https://mnm.be/kijk/live',
        live_stream_id='vualto_mnm',
        youbube=[
            dict(label='MNM', url='https://www.youtube.com/user/MNMbe'),
        ],
        logo='https://images.vrt.be/orig/logo/mnm/logo_witte_achtergrond.png',
        epg_id='mnm.be',
        preset=905,
        vod=True,
    ),
    dict(
        id='',
        name='vrtnxt',
        label='VRT NXT',
        studio='VRT NXT',
        youtube=[
            dict(label='VRT NXT', url='https://www.youtube.com/channel/UCO-VoGCVzhYVwvQvWYJq4-Q'),
        ],
        vod=True,
    ),
    dict(
        id='',
        name='de-warmste-week',
        label='De Warmste Week',
        studio='De Warmste Week',
        youtube=[
            dict(label='De Warmste Week', url='https://www.youtube.com/channel/UC_PsMpKLAp4hSGSXyUCPtxw'),
        ],
        vod=True,
    ),
    dict(
        id='',
        name='vrt-events1',
        label='VRT Events 1',
        studio='VRT',
        live_stream_id='vualto_events1_geo',
        logo='https://images.vrt.be/orig/logo/vrt.png',
        epg_id='vrtevents1.be',
        preset=851,
        vod=False,
    ),
    dict(
        id='',
        name='vrt-events2',
        label='VRT Events 2',
        studio='VRT',
        live_stream_id='vualto_events2_geo',
        logo='https://images.vrt.be/orig/logo/vrt.png',
        epg_id='vrtevents2.be',
        preset=852,
        vod=False,
    ),
    dict(
        id='',
        name='vrt-events3',
        label='VRT Events 3',
        studio='VRT',
        live_stream_id='vualto_events3_geo',
        logo='https://images.vrt.be/orig/logo/vrt.png',
        epg_id='vrtevents3.be',
        preset=853,
        vod=False,
    ),
]

FEATURED = [
    # Tijdsgerelateerd
    dict(name='Exclusief online', id='exclusief-online', msgctxt=30100),
    dict(name='Volledig seizoen', id='volledig-seizoen', msgctxt=30101),
    dict(name='Volledige reeks', id='volledige-reeks', msgctxt=30102),
    dict(name='Uit het archief', id='uit-het-archief', msgctxt=30103),
    # Inhoudsgerelateerd
    dict(name='Kortfilm', id='kortfilm', msgctxt=30120),
    # Thema
    dict(name='Kies19', id='kies-19', msgctxt=30128),
    dict(name='Klimaat', id='klimaat', msgctxt=30129),
    dict(name='De warmste week', id='de-warmste-week', msgctxt=30130),
]

RELATIVE_DATES = [
    dict(id='2-days-ago', offset=-2, msgctxt=30330, permalink=False),
    dict(id='yesterday', offset=-1, msgctxt=30331, permalink=True),
    dict(id='today', offset=0, msgctxt=30332, permalink=True),
    dict(id='tomorrow', offset=1, msgctxt=30333, permalink=True),
    dict(id='in-2-days', offset=2, msgctxt=30334, permalink=False),
]
