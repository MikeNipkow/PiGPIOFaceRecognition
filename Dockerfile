FROM python:3

WORKDIR /usr/src/app

RUN apt-get -y update
RUN apt-get install -y --fix-missing \
    cmake \

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./main.py" ]