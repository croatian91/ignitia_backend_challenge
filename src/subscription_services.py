import os
from datetime import timedelta

from sqlalchemy import and_, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

from exceptions import BillingUpdateException
from models import Forecast, Subscription
import celery_tasks


class SubscriptionService:
    """
    Handle subscriptions
    """

    def _get_session(self) -> "Session":
        """
        Get a session
        """
        engine = create_engine("postgresql://postgres:postgres@db/ignitia", echo=True)
        return sessionmaker(bind=engine)()

    def update_current_service_id_and_billing_date(
        self, msisdn: str, service_id: int
    ) -> None:
        try:
            session = self._get_session()
            sub = session.query(Subscription).get(msisdn)
            sub.current_service_id = service_id
            # suppose week-ends are counted
            sub.next_billing_date = func.now() + timedelta(days=service_id)
            session.commit()
        except Exception as e:
            raise BillingUpdateException(e)

    def run_billing(self) -> None:
        """
        Charge every subscribers
        """
        session = self._get_session()
        q = session.query(Subscription).filter(
            and_(
                Subscription.service_id > 0,
                func.date(Subscription.next_billing_date) == func.date(func.now()),
            )
        )

        # send billing for each subscription
        for sub in q:
            celery_tasks.send_billing.delay(sub.msisdn, sub.service_id)

    def send_forecasts(self) -> None:
        session = self._get_session()
        q = session.query(Forecast, Subscription).filter(
            and_(
                Subscription.current_service_id > 0,
                Subscription.lid == Forecast.gid,
            )
        )

        for forecast, subscription in q:
            text = f"{forecast.fcat24}\n{forecast.fcat48}"
            celery_tasks.send_message.delay(subscription.msisdn, text)
