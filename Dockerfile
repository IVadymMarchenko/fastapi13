FROM python:3.11
#docker run -it -p 80:80 --name my-con  my-python-app
#docker run -d -it --name jjjr my-python-app
# docker exec -it jjjr /bin/sh

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt
RUN pip install uvicorn


ENTRYPOINT ["uvicorn", "main:app", "--reload"]