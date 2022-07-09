# Use an official Python 3.7 runtime as a parent image
FROM python:3.7

# Install vim
RUN apt-get update && \
    apt-get -y install vim

# Add Backend directory as api
ADD ./Backend /home/api

# Make api as a working directory
WORKDIR /home/api

# Install any needed packages specified in requirements.txt
RUN pip install -r /home/api/requirements.txt

# reload docker whenver there is a change in any file
COPY . /api

# Run app.py when the container launches
ENTRYPOINT [ "python" ]

CMD [ "app.py" ]
