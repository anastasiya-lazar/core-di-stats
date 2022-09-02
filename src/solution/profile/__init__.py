from dataclasses import dataclass, fields


from core.spi.db_client import DBClientSPI
from solution.sp.sql_base.db_client import DBClientSP


@dataclass
class AppProfile:
    db_client: DBClientSPI = DBClientSP()


profile = AppProfile()


for field in fields(AppProfile):
    assert getattr(profile, field.name), f"app profile do not define {field.name}"
