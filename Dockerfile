# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install Poetry for Python package management
RUN pip install poetry

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the pyproject.toml file into the container
COPY pyproject.toml /usr/src/app/

# Install dependencies using poetry in a way that doesn't create a virtual environment
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Copy the rest of the application's code
COPY . .

# Run application when the container launches
CMD ["python", "./main.py"]