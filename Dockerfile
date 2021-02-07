FROM python:3.9
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=src/app.py
ENV FLASK_RUN_HOST=0.0.0.0
WORKDIR /code
COPY requirements.txt .
RUN pip install -r requirements.txt
EXPOSE 5000
COPY src .
CMD ["flask", "run"]