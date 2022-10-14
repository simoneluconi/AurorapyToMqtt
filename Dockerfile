FROM python:3-alpine

RUN pip install --upgrade pip

RUN apk add build-base

RUN adduser -D worker
USER worker
WORKDIR /home/worker

COPY --chown=worker:worker requirements.txt ./
RUN pip install --user --no-cache-dir -r requirements.txt
RUN rm requirements.txt

ENV PATH="/home/worker/.local/bin:${PATH}"

COPY --chown=worker:worker ./app ./app

CMD [ "python", "-u", "./AuroraComm.py" ]
