FROM python:3.9-buster

# Set the working directory
RUN mkdir -p /app
WORKDIR /app

# Deactivate some unneeded python features
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system deps
RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get --no-install-recommends -y install git -y

# Install the package manager
RUN pip install 'poetry>=1.0'

# Clone repository
RUN git clone https://github.com/LeGmask/pidioul.git ./

# Install stuff
RUN poetry install
