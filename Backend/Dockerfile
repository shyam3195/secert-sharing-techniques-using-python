# Use an official Python runtime as a parent image
FROM python:3.7

RUN apt-get update && \
    apt-get -y install vim

ADD ./Backend /home/api

WORKDIR /home/api

RUN pip install -r /home/api/requirements.txt
 
# Install any needed packages specified in requirements.txt
COPY . /api

# Run app.py when the container launches
ENTRYPOINT [ "python" ]

CMD [ "app.py" ]
