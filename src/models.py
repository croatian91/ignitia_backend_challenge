from geoalchemy2 import Geometry
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import DATE, DOUBLE_PRECISION, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Forecast(Base):
    __tablename__ = "forecasts"

    gid = Column(Integer, primary_key=True)
    geom = Column(Geometry("POINT", srid=4326))
    fcat24 = Column(DOUBLE_PRECISION)
    fcat48 = Column(DOUBLE_PRECISION)

    def __repr__(self):
        return "Forecast #{}, fcat24:{}, fcat48:{}".format(
            self.gid, self.fcat24, self.fcat48
        )


class Subscription(Base):
    __tablename__ = "subscriptions"

    msisdn = Column(String, primary_key=True)
    service_id = Column(Integer, nullable=False)
    current_service_id = Column(Integer, nullable=False, default=0)
    geom = Column(Geometry("POINT", srid=4326))
    lid = Column(Integer, ForeignKey("forecasts.gid"))
    sub_date = Column(TIMESTAMP, nullable=False)
    unsub_date = Column(TIMESTAMP)
    next_billing_date = Column(DATE, nullable=False, default=func.now())

    def __init__(self, **kwargs):
        self.msisdn = kwargs.pop("msisdn")
        self.service_id = kwargs.pop("service_id")
        self.geom = kwargs.pop("geom")
        self.lid = kwargs.pop("lid")
        self.sub_date = kwargs.pop("sub_date")

    def __repr__(self):
        return "Subscription #{}, lid:{}, sub_date:{}, unsub_date:{}, next_billing_date:{}".format(
            self.msisdn,
            self.lid,
            self.sub_date,
            self.unsub_date,
            self.next_billing_date,
        )
