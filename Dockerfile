ARG platform=linux/amd64
FROM --platform=${platform} python:3.9
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y default-mysql-client
WORKDIR /app
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY  ./ /app
CMD [ "python", "main.py" ]