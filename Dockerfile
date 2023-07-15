FROM python:3-slim

ARG USERNAME=test
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

RUN pip install --upgrade pip
    
USER $USERNAME
WORKDIR /home/$USERNAME

COPY --chown=$USERNAME:$USERNAME requirements.txt ./
RUN pip install --user --no-cache-dir -r requirements.txt
RUN rm requirements.txt

ENV PATH="/home/${USERNAME}/.local/bin:${PATH}"

COPY --chown=$USERNAME:$USERNAME ./app ./app

CMD [ "python", "-u", "./app/AuroraComm.py" ]
