FROM python:3-slim-bullseye

RUN pip install --upgrade pip

RUN groupadd --gid 1000 worker \
    && useradd --uid 1000 --gid 1000 -m worker \
    
USER worker
WORKDIR /home/worker

COPY --chown=worker:worker requirements.txt ./
RUN pip install --user --no-cache-dir -r requirements.txt
RUN rm requirements.txt

ENV PATH="/home/worker/.local/bin:${PATH}"

COPY --chown=worker:worker ./app ./app

CMD [ "python", "-u", "./app/AuroraComm.py" ]
