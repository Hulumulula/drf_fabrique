FROM python:3.10.8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /FabricaResheniy

COPY ./requierment.txt requierment.txt
RUN pip install -r requierment.txt

COPY . /FabricaResheniy

EXPOSE 8000
EXPOSE 5555

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
