FROM python:3.8-slim-buster

MAINTAINER Brandon Spendlove <brandon.spendlove@veesix-networks.co.uk>

# Leverage Docker layer caching
COPY ./requirements.txt /app/requirements.txt

# Install requirements
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

# Change Workdirectory
WORKDIR /app
COPY . /app

# Set Entrypoint
ENTRYPOINT [ "python3" ]
CMD [ "app.py" ]