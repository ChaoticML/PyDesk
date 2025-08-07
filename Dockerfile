FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN pip install uv

COPY requirements.txt .

RUN uv pip install --system --no-cache-dir -r requirements.txt

COPY . .

RUN adduser --system --group pydeskuser
USER pydeskuser

EXPOSE 5001

CMD ["waitress-serve", "--host=0.0.0.0", "--port=5001", "--call", "app:create_app"]