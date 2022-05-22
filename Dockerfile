FROM ubuntu
 
RUN mkdir /app
 
COPY . /app
 
WORKDIR /app
 
RUN apt-get update -yqq
 
RUN apt-get install python3 python3-pip nginx-core nginx uwsgi uwsgi-plugin-python3 -y
 
COPY nginx.conf /etc/nginx/nginx.conf
 
RUN python3 -m pip install --upgrade pip

RUN pip3 install -r requirements.txt
 
ENTRYPOINT nginx -g "daemon on;" && uwsgi --ini uwsgi.ini 