FROM node:24.14.1-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev

COPY package.json package-lock.json ./
RUN npm install

COPY . .
RUN npm run build

RUN uv run python manage.py migrate --noinput

EXPOSE 8000

ENV CONTAINERISED=1

CMD ["uv", "run", "manage.py", "runserver", "0.0.0.0:8000"]
