FROM python:3.10-slim

WORKDIR /src

COPY . .

RUN apt-get update && apt-get install -y cron && apt-get install make

RUN pip install --upgrade pip 

RUN pip install -r requirements.txt

RUN chmod a+x crontab

RUN crontab crontab

CMD ["cron","-f", "-l", "2"]
