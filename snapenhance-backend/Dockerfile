#using official Python image
FROM python:3.9

#set up the working directory
WORKDIR /app

# copy the files
COPY . .

#install dependencies
RUN pip install -r requirements.txt

#expose port
EXPOSE 5000

#run Flask app
CMD ["python", "app.py"]
