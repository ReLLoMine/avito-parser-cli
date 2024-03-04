import dataclasses as dc
import datetime as dt


@dc.dataclass
class Product:
    title: str = ""
    description: str = ""
    url: str = ""
    img: str = ""
    price: float = 0.0
    views: int = 0
    promoted: bool = False
    seller: str = ""
    address: str = ""
    publish_date: str = ""
    ads_id: str = "0"

    def dict(self):
        return self.__dict__
