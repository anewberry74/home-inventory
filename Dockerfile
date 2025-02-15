# Use Python image for FastAPI
FROM python:3.13.1-slim-bookworm as fastapi

RUN apt-get update && apt-get -y install cron vim iputils-ping
# Set working directory
WORKDIR /app

# Copy FastAPI app
COPY app/ /app/

# Copy FastAPI dependencies
COPY ./requirements.txt /app/requirements.txt
COPY ./crontab /etc/cron.d/crontab

RUN chmod 0644 /etc/cron.d/crontab
RUN /usr/bin/crontab /etc/cron.d/crontab

# Install FastAPI dependencies
RUN pip install --no-cache-dir -r requirements.txt
#RUN service cron start
# Expose port for FastAPI
#EXPOSE 80
#EXPOSE 8000

#COPY  ./nginx/default.conf /etc/nginx/conf.d/default.conf

# Start FastAPI app
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
#CMD ["cron", "-f"]
COPY ./cron-entrypoint.sh  /cron-entrypoint.sh
RUN chmod +x /cron-entrypoint.sh
ENTRYPOINT ["/cron-entrypoint.sh"]






