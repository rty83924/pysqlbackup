ARG platform=linux/amd64
FROM --platform=${platform} python:3.9
ENV PYTHONUNBUFFERED=1
RUN set -eux; \
# gpg: key 3A79BD29: public key "MySQL Release Engineering <mysql-build@oss.oracle.com>" imported
	key='859BE8D7C586F538430B19C2467B942D3A79BD29'; \
	export GNUPGHOME="$(mktemp -d)"; \
	gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "$key"; \
	mkdir -p /etc/apt/keyrings; \
	gpg --batch --export "$key" > /etc/apt/keyrings/mysql.gpg; \
	gpgconf --kill all; \
	rm -rf "$GNUPGHOME"
ENV MYSQL_MAJOR 8.0
ENV MYSQL_VERSION 8.0.29-1debian11
RUN echo 'deb [ signed-by=/etc/apt/keyrings/mysql.gpg ] http://repo.mysql.com/apt/debian/ bullseye mysql-8.0' > /etc/apt/sources.list.d/mysql.list
RUN apt-get update \
    && apt-get install -y mysql-community-client
WORKDIR /app
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY  ./ /app
CMD [ "python", "main.py" ]