FROM python:3.10.10-bullseye

# poetryのPATHを$PATHに追加
ENV PATH /root/.local/bin:$PATH

RUN mkdir /app

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
COPY pyproject.toml .

# poetryのインストール
RUN apt-get update \
    && apt-get install -y curl \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && . /root/.profile

# poetryを使用してパッケージのインストール
RUN pip install --upgrade pip \
    && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install

# Add the current directory contents into the container at /app
COPY . .

ENV GOOGLE_APPLICATION_CREDENTIALS=/app/serviceAccoutKey.json

# Make port 8080 available to the world outside this container
ENV PORT 8080
EXPOSE $PORT

# Run main.py when the container launches
CMD ["python", "main.py"]
