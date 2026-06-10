FROM python:3.13-slim
EXPOSE 8000
WORKDIR /app
COPY main.py main.py
RUN pip install "fastapi[standard]"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
