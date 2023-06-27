FROM python:3.10

ENV PATH="/scripts:${PATH}"
ENV PYTHONBUFFERED=1

RUN apt update && apt install stockfish

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /app
COPY ./app /app
WORKDIR /app
COPY ./scripts /scripts

RUN chmod +x /scripts/*

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

RUN adduser user
RUN chown -R user:user /vol
RUN chown -R user:user /app/db
RUN chmod -R 755 /vol/web
USER user

CMD ["entrypoint.sh"]