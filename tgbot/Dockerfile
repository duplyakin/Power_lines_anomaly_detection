FROM python:3.8.2-buster

USER root
WORKDIR /root

# DEFAULT CONFIG ENVIRONMENT
# You can run container with another value of CFG_TYPE env var
ENV CFG_TYPE prod


WORKDIR /root/tgbot

# python packages
ADD requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .

WORKDIR /root/tgbot/src
RUN chmod 777 main.py

CMD ["python3", "/root/tgbot/src/main.py"]