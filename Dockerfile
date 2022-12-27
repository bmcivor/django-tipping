FROM python:3.11.1-slim-buster as build-stage

WORKDIR /app

COPY tipping/requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

FROM build-stage as production

CMD ["python", "manage.py", "runserver"]


FROM production as test

CMD ["pytest", "-v"]
