from flask import Flask

from subscription_services import SubscriptionService

flask_app = Flask(__name__)


@flask_app.route("/")
def home():
    return ("<br>" * 2).join(["/billing: run billing", "/forecasts: send forecasts"])


@flask_app.route("/billing")
def run_billing():
    SubscriptionService().run_billing()
    return "Billing"


@flask_app.route("/forecasts")
def send_forecasts():
    SubscriptionService().send_forecasts()
    return "Forecasts"
