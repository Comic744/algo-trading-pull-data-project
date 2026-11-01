
FROM python:3.14.4-slim


# where the code is
WORKDIR /app

RUN mkdir data

COPY  requirements.txt .
# to run commands such as downloading content from requirement.txt
RUN pip install -r requirements.txt

COPY stock-pull.py .

# env variables 
ENV PYTHONUNBUFFERED=1
ENV DB_PATH=/app/data/stocks.db

# command to actually start the container
CMD [ "python", "/app/stock-pull.py" ]



# IN TERMINAL

# CREATE/BUILD IMAGE
# docker build -t image_name path/Dockerfile
# docker build -t stock-pull .

# BUILD CONTAINER
# docker run --rm stock-pull        --rm tells Docker to delete the container automatically as soon as it exits.
# docker run --mount type=bind,src=<host-path>,dst=<container-path>
# OR
# docker run -v <host-path>:<container-path> SIMPLER
#RUNNING VERSION 
# docker run --rm stock-pull -v $(pwd)/data:/app/data
# docker run --rm -v $(pwd)/data:/app/data stock-pull  #root level
# docker run --rm -v $(pwd)/data:/app/data --user $(id -u):$(id -g) stock-pull # user level
