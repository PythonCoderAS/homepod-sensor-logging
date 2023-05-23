FROM python:3.11-slim
LABEL authors="aoyansarkar"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1

# Set work directory
WORKDIR /app

RUN pip install --upgrade pipenv wheel

COPY . /app

# Install dependencies
RUN pipenv sync

# Run the application
CMD ["pipenv", "run", "uvicorn", "server:app" , "--port", "5745"]
EXPOSE 5745
