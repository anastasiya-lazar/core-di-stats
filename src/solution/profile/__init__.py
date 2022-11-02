from dataclasses import dataclass, fields
from typing import Callable

import config as conf
from core.spi.db_client import DBClientSPI
from core.spi.stats_message_handler import StatsMessageHandlerSPI
from solution.sp.sql_base.db_client import DBClientSP


@dataclass
class AppProfile:
    get_stats_message_handler: Callable[[], StatsMessageHandlerSPI] = None
    db_client: DBClientSPI = DBClientSP()


profile = AppProfile()

if conf.CLOUD_PROVIDER_TYPE == conf.CloudProvidersTypes.azure:
    from ._azure import *

    profile.get_stats_message_handler = get_stats_message_handler


for field in fields(AppProfile):
    assert getattr(profile, field.name), f"app profile do not define {field.name}"
