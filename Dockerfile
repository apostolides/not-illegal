FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN apk add --no-cache ffmpeg

RUN mkdir /etc/cron
RUN echo '*/5 * * * * find /app -name "*.m4a" -mmin +5 -delete' > /etc/cron/crontab
RUN crontab /etc/cron/crontab

CMD crond -f

CMD [ "fastapi", "run", "main.py" ]
