# CONTRIBUTING

## How to run the Dockerfile locally


`docker run -dp 5000:5000 -w /app -v "${pwd}:/app" IMAGE_NAME sh -c "flask run --host 0.0.0.0"`


## How to run redis workers

`docker run -w /app IMAGE_NAME sh -c "rq worker -u REDIS_URL emails"`
