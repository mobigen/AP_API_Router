FROM python:3.9.15

RUN apt-get update
RUN apt-get upgrade -y \
    && apt-get install git -y

RUN git clone https://github.com/mobigen/AP_API_Router.git
WORKDIR /AP_API_Router

RUN git checkout -b common-web origin/common-web
RUN pip install -r requirements.txt
RUN python common_web/manage.py makemigrations; exit 0 \
    && python common_web/manage.py migrate

EXPOSE 8000

ENTRYPOINT [ "python", "common_web/manage.py", "runserver", "0.0.0.0:8000"]