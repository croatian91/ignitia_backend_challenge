# IGNITIA BACKEND CHALLENGE

### Installation

> This project requires Docker installed and running

```sh
$ git clone https://github.com/croatian91/ignitia_backend_challenge.git
$ cd ignitia_backend_challenge
$ docker-compose -f "docker-compose.yml" up -d --build
```

> Wait for database initialisation. Subscriptions processing is done automatically and takes up to 25 seconds

:rocket:

### URLS

- Billing: [http://0.0.0.0:5000/billing](http://0.0.0.0:5000/billing)
- Forecasts: [http://0.0.0.0:5000/forecasts](http://0.0.0.0:5000/forecasts)
