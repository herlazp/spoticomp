FROM python:3.8

# Set the working directory
WORKDIR /workspace

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the project files
COPY . .

# Expose the port for the application
EXPOSE 8050

# Define the command to run the application
CMD ["python", "app.py"]
