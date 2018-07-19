FROM python:3
RUN mkdir /api
WORKDIR /api
COPY /api ./api
COPY run.py .
RUN pip install redis
CMD python3 run.py -p 8000
