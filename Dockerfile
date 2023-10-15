FROM python:3.11.2

WORKDIR /app

COPY etl.sh config.py extract.py transform.py requirements.txt /app/

RUN pip install -r requirements.txt
RUN chmod +x etl.sh

CMD [ "/app/etl.sh"]