FROM python:3.11-bullseye
COPY requirements_dev.txt /app/
WORKDIR /app
RUN pip install -r requirements_dev.txt
COPY . .
CMD ["python3", "src/tanks/main.py"]