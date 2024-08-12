FROM python:3.11.4
RUN apt-get update && apt-get -y install cron vim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x /usr/src/app

CMD ["cron", "-f"]