# Use the official Python image from the Docker Hub
FROM python:3.12
# Set the working directory inside the container
WORKDIR /python_advanced_diploma

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
#COPY ./app /app
COPY . .
# Expose port 80 to be able to access it externally
EXPOSE 8000

# Command to run the application using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
