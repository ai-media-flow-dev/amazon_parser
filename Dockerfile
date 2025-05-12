FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    wget \
    git \
    vim \
    locales \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

COPY pyproject.toml /app/
COPY uv.lock /app/
RUN uv sync --locked

COPY ./amazon_parser /app/amazon_parser

EXPOSE 8000
RUN uv run amazon_parser/manage.py migrate
CMD ["uv", "run", "amazon_parser/manage.py", "runserver", "0.0.0.0:8000"]
# CMD ["uv", "--version"]
# CMD ["ls", "-la"]
