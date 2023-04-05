FROM python:3.8
EXPOSE 80
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPy . .
CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:create_app()"]