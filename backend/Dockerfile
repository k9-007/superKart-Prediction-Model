# Use a minimal Python 3.9 base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy dependency file first to leverage Docker layer caching
COPY requirements.txt .

# Install dependencies without caching to keep the image small
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the application (app.py + serialized model)
COPY . .

# Serve the Flask app with Gunicorn (4 workers) on port 7860.
# - `-w 4`: 4 worker processes
# - `-b 0.0.0.0:7860`: bind to port 7860 on all interfaces
# - `app:superkart_sales_predictor_api`: the Flask instance in app.py
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app:superkart_sales_predictor_api"]
