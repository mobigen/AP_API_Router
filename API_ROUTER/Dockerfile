FROM python:3.9.15

COPY . /API_ROUTER
WORKDIR /API_ROUTER
RUN pip install -r ./requirements.txt

ENV APP_ENV=local

EXPOSE 8000
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app"]