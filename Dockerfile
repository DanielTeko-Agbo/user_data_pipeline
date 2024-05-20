FROM python:3.11-slim

WORKDIR /src

COPY . .

RUN apt-get update && apt-get install -y cron

RUN pip install --upgrade pip 

RUN pip install -r requirements.txt

RUN chmod a+x crontab

RUN crontab crontab

CMD ["cron","-f", "-l", "2"]