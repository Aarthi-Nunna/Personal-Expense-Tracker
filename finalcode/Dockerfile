FROM debian:stable
COPY . ./server
WORKDIR /server
RUN apt-get update
RUN apt-get install -y apt-utils
RUN apt install -y build-essential libxml2
RUN apt install -y python3
RUN apt install -y python3-pip
RUN rm -rf /var/lib/apt/lists/*
RUN apt-get update
RUN pip3 install -r requirements.txt
EXPOSE 5000
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]