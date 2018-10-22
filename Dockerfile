FROM python:3.6-alpine3.6

RUN apk add --update alpine-sdk
RUN pip3 install vibora
RUN pip3 install requests

ENV PYTHONPATH "${PYTHONPATH}:/usr/app/"

WORKDIR /usr/app
COPY . .

RUN ["chmod", "+x", "/usr/app/api/run.py"]
CMD ["python", "/usr/app/api/run.py"]


