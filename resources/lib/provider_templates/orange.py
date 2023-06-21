# -*- coding: utf-8 -*-
"""Orange Template"""
from dataclasses import dataclass
from datetime import date, datetime, timedelta
import json
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from lib.providers.provider_interface import ProviderInterface
from lib.utils import get_drm, get_global_setting, log, LogLevel, random_ua

@dataclass
class OrangeTemplate(ProviderInterface):
    """This template helps creating providers based on the Orange architecture"""
    chunks_per_day: int = 2

    def __init__(
        self,
        endpoint_users: str,
        endpoint_stream_info: str,
        endpoint_streams: str,
        endpoint_programs: str
    ) -> None:
        self.endpoint_users = endpoint_users
        self.endpoint_stream_info = endpoint_stream_info
        self.endpoint_streams = endpoint_streams
        self.endpoint_programs = endpoint_programs

    def get_stream_info(self, channel_id: int) -> dict:
        req = Request(self.endpoint_stream_info.format(channel_id=channel_id), headers={
            'User-Agent': random_ua(),
            'Host': urlparse(self.endpoint_stream_info).netloc
        })

        try:
            with urlopen(req) as res:
                stream_info = json.loads(res.read())
        except HTTPError as error:
            if error.code == 403:
                return False

        drm = get_drm()
        license_server_url = None
        for system in stream_info.get('protectionData'):
            if system.get('keySystem') == drm.value:
                license_server_url = system.get('laUrl')

        headers = f'Content-Type=&User-Agent={random_ua()}&Host={urlparse(license_server_url).netloc}'
        post_data = 'R{SSM}'
        response = ''

        stream_info = {
            'path': stream_info['url'],
            'mime_type': 'application/xml+dash',
            'manifest_type': 'mpd',
            'drm': drm.name.lower(),
            'license_type': drm.value,
            'license_key': f'{license_server_url}|{headers}|{post_data}|{response}'
        }

        log(stream_info, LogLevel.DEBUG)
        return stream_info

    def get_streams(self) -> list:

        """Get the user rights"""
        reqUser = Request(self.endpoint_users, headers={
            'User-Agent': random_ua(),
            'Host': urlparse(self.endpoint_users).netloc
        })
        
        with urlopen(reqUser) as resUser:
            users = json.loads(resUser.read())
        
        user_bouquets = users['bouquets']

        """Get the channels"""
        req = Request(self.endpoint_streams, headers={
            'User-Agent': random_ua(),
            'Host': urlparse(self.endpoint_streams).netloc
        })

        with urlopen(req) as res:
            channels = json.loads(res.read())

        streams = []

        user_channels = [x for x in channels if x['nomadismAllowed'] & any(x in user_bouquets for x in x['bouquets']) ]

        log(f'Initial channel {len(user_channels)} and final user selection: {len(user_channels)}', LogLevel.INFO)
        
        for channel in user_channels:
            channel_id: str = channel['id']
            streams.append({
                'id': channel_id,
                'name': channel['name'],
                'preset': channel['zappingNumber'],
                'logo': channel['logos']['square'].replace('%2F/', '%2F') if 'square' in channel['logos'] else None,
                'stream': f'plugin://plugin.video.orange.fr/channel/load/{channel_id}'
            })

        return streams

    def get_epg(self) -> dict:
        start_day = datetime.timestamp(
            datetime.combine(
                date.today() - timedelta(days=int(get_global_setting('epg.pastdaystodisplay'))),
                datetime.min.time()
            )
        )

        days_to_display = int(get_global_setting('epg.futuredaystodisplay')) \
            + int(get_global_setting('epg.pastdaystodisplay'))

        chunk_duration = 24 * 60 * 60 / self.chunks_per_day
        programs = []

        for chunk in range(0, days_to_display * self.chunks_per_day):
            programs.extend(self._get_programs(
                period_start=(start_day + chunk_duration * chunk) * 1000,
                period_end=(start_day + chunk_duration * (chunk + 1)) * 1000
            ))

        epg = {}

        for program in programs:
            if not program['channelId'] in epg:
                epg[program['channelId']] = []

            if program['programType'] != 'EPISODE':
                title = program['title']
                subtitle = None
                episode = None
            else:
                title = program['season']['serie']['title']
                subtitle = program['title']
                season_number = program['season']['number']
                episode_number = program['episodeNumber'] if 'episodeNumber' in program else None
                episode = f'S{season_number}E{episode_number}'

            image = None
            if isinstance(program['covers'], list):
                for cover in program['covers']:
                    if cover['format'] == 'RATIO_16_9':
                        image = program['covers'][0]['url']

            epg[program['channelId']].append({
                'start': datetime.fromtimestamp(program['diffusionDate']).astimezone().replace(microsecond=0).isoformat(),
                'stop': (datetime.fromtimestamp(program['diffusionDate'] + program['duration']).astimezone()).isoformat(),
                'title': title,
                'subtitle': subtitle,
                'episode': episode,
                'description': program['synopsis'],
                'genre': program['genre'] if program['genreDetailed'] is None else program['genreDetailed'],
                'image': image
            })

        return epg

    def _get_programs(self, period_start: int = None, period_end: int = None) -> list:
        """Returns the programs for today (default) or the specified period"""
        try:
            period = f'{int(period_start)},{int(period_end)}'
        except ValueError:
            period = 'today'

        req = Request(self.endpoint_programs.format(period=period), headers={
            'User-Agent': random_ua(),
            'Host': urlparse(self.endpoint_programs).netloc
        })

        with urlopen(req) as res:
            return json.loads(res.read())

    