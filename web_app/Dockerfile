FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Jupyter and VSCode related extensions
RUN pip install jupyter jupyterlab ipykernel

COPY . .

# Expose ports for Jupyter and the web app
EXPOSE 8000 8888

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--no-browser"]