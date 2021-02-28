FROM python:3.9.1-alpine
# Update & Install dependencies
RUN apk update
RUN apk add --no-cache --update \
    openssl \
    ca-certificates \
    bzip2-dev \
    zlib-dev \
    readline-dev \
    build-base \
    linux-headers
RUN apk add cmake
RUN python -m pip install --upgrade pip
RUN apk --update add gcc libgcc musl-dev jpeg-dev zlib-dev
COPY ./requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt
RUN python -m pip install balticlsc==1.0.1
# Run the module API
WORKDIR app
COPY __init__.py module/__init__.py
COPY content module/content
ENV FLASK_APP='/app/module/content/processing.py'
RUN echo $FLASK_APP
# Expose the Flask port number 80 to the host
EXPOSE 80
ENTRYPOINT ["flask", "run", "--host=0.0.0.0", "--port=80"]
