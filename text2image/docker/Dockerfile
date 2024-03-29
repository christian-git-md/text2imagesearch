FROM ubuntu:20.04
RUN apt-get update
RUN apt-get install -y python3-pip
RUN pip install qdrant-client requests fastapi uvicorn python-multipart
COPY entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]