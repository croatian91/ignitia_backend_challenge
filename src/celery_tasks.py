import json
import logging
import os

import requests
from celery import group
from eventlet import Timeout
from flask import Flask
from requests.exceptions import RequestException

from celery_config import make_celery
from exceptions import BillingUpdateException
import subscription_services

flask_app = Flask(__name__)
flask_app.config.update(
    CELERY_BROKER_URL=os.environ["CELERY_BROKER"],
    CELERY_RESULT_BACKEND=os.environ["CELERY_BACKEND"],
)

celery = make_celery(flask_app)


@celery.task()
def post_data(url: str, payload: dict) -> dict:
    """
    Post Data
    """
    headers = {
        "Content-Type": "application/json",
        "Auth-key": os.environ["AUTH_KEY"],
    }
    res = requests.post(url, data=json.dumps(payload), headers=headers)
    return res.json()


@celery.task(max_retries=3)
def send_billing(msisdn: str, service_id: int) -> None:
    """
    API call for billing
    """
    url = "https://test.ignitia.se/sms/billing"
    payload = {"msisdn": msisdn, "service_id": service_id}

    try:
        result = post_data.delay(url, payload)
        data = result.wait()

        if data["status"] == "failure":
            logging.warn(f"Subscriber: {msisdn} with status failure")
            return

        subscription_services.update_current_service_id_and_billing_date(
            msisdn, service_id
        )
        logging.info(f"Billing for subscriber: {msisdn} with success")

    except BillingUpdateException as e:
        logging.error(e)
    except RequestException as e:
        raise send_billing.retry(exc=e)


@celery.task(max_retries=5)
def send_message(msisdn: str, text: str) -> None:
    """
    API call for sending a message
    """
    urls = [f"https://test.ignitia.se/sms/send/srv{i}" for i in range(1, 4)]
    payload = {"msisdn": msisdn, "text": text}
    # use the endpoints in parallel
    try:
        with Timeout(1, False):
            subtasks = group(post_data.s(url, payload) for url in urls)
            subtasks.delay()
    except RequestException as e:
        raise send_message.retry(exc=e)
