#using official Python image
FROM python:3.9

#set up the working directory
WORKDIR /app

#install system dependencies
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# copy the files
COPY . .

#install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

#expose port
EXPOSE 5000

#run Flask app
CMD ["python", "app.py"]