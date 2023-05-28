FROM python

WORKDIR /home/app

RUN apt-get update
RUN apt install curl -y
RUN apt-get install -y iputils-ping
RUN apt-get install -y iproute2

COPY requirements.txt /dependencies/requirements.txt
RUN pip install -r /dependencies/requirements.txt

COPY . /home/app

CMD streamlit run --server.port $PORT Get_around_tool.py