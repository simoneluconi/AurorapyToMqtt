FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN rm requirements.txt

COPY ./app .

CMD [ "python", "-u", "./AuroraComm.py" ]