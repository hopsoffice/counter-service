FROM python:3.10-slim

WORKDIR /app

# Copy using poetry.lock* in case it doesn't exist yet
COPY ./pyproject.toml ./poetry.lock* /app/

RUN pip install -U pip poetry && poetry install --no-root --no-dev

COPY app.py /app/
EXPOSE 8000

CMD ["poetry", "run", "python", "app.py"]
