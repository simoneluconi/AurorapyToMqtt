FROM python:3-slim

ARG USERNAME=worker
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

RUN pip install --upgrade pip
    
USER worker
WORKDIR /home/worker

COPY --chown=worker:worker requirements.txt ./
RUN pip install --user --no-cache-dir -r requirements.txt
RUN rm requirements.txt

ENV PATH="/home/worker/.local/bin:${PATH}"

COPY --chown=worker:worker ./app ./app

CMD [ "python", "-u", "./app/AuroraComm.py" ]
