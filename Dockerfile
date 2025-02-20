FROM python:3.9-slim

RUN apt-get update && apt-get install -y cron
# RUN apt-get install -y cron

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./app .

RUN chmod +x install.sh

CMD ["./install.sh"]