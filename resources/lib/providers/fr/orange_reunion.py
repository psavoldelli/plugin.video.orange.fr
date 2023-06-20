# -*- coding: utf-8 -*-
"""Orange Réunion"""
from lib.provider_templates import OrangeTemplate

class OrangeReunionProvider(OrangeTemplate):
    """Orange Réunion provider"""

    # pylint: disable=line-too-long
    def __init__(self) -> None:
        super().__init__(
            endpoint_users = 'https://mediation-tv.orange.fr/all/live/v3/applications/PC/users/me',
            endpoint_stream_info = 'https://mediation-tv.orange.fr/all/live/v3/applications/PC/users/me/channels/{channel_id}/stream?terminalModel=WEB_PC',
            endpoint_streams = 'https://mediation-tv.orange.fr/all/live/v3/applications/PC/channels?mco=ORE',
            endpoint_programs = 'https://mediation-tv.orange.fr/all/live/v3/applications/PC/programs?period={period}&mco=ORE'
        )
