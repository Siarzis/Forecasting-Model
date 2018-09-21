# Use an official Python runtime as a parent image
FROM python:2.7-slim

# Set the working directory to /Prediction1
WORKDIR /Prediction1

# Copy the current directory contents into the container at /Prediction1
COPY . /Prediction1

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME Pred

# Run SplitDatasets.py when the container launches
CMD ["python", "SplitDatasets.py"]