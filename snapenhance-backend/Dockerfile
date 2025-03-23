FROM python:3.9

WORKDIR /app

RUN apt-get update && apt-get install -y libgl1-mesa-glx

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV PORT=5000
EXPOSE $PORT

# Run Flask app
CMD ["python", "app.py"]