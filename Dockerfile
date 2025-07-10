FROM python:3.11

#ADD backend.py .

#ADD requirements.txt .

ADD . .

RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0

RUN pip install -r requirements.txt

EXPOSE  5000

CMD [ "python", "./backend.py" ] 