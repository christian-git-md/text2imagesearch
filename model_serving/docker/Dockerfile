FROM pytorch/pytorch:1.10.0-cuda11.3-cudnn8-runtime
RUN pip install pip install 'transformers[torch]' fastapi uvicorn python-multipart
COPY entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]