# -*- coding: utf-8 -*-
"""Orange France"""
from lib.provider_templates import OrangeTemplate

class OrangeFranceProvider(OrangeTemplate):
    """Orange France provider"""

    # pylint: disable=line-too-long
    def __init__(self) -> None:
        super().__init__(
            endpoint_users = 'https://mediation-tv.orange.fr/all/live/v3/applications/PC/users/me',
            endpoint_stream_info = 'https://mediation-tv.orange.fr/all/live/v3/applications/PC/users/me/channels/{channel_id}/stream?terminalModel=WEB_PC',
            endpoint_streams = 'https://mediation-tv.orange.fr/all/live/v3/applications/PC/channels?mco=OFR',
            endpoint_programs = 'https://rp-ott-mediation-tv.woopic.com/api-gw/live/v3/applications/PC/programs?period={period}&mco=OFR'
        )
