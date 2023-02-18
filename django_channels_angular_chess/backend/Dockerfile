FROM python:3.10

WORKDIR /app/

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY ./ ./

ENV DJANGO_SETTINGS_MODULE=django_chess.settings

RUN ["chmod", "+x", "/app/entrypoint.sh"]
ENTRYPOINT ["/app/entrypoint.sh"]
