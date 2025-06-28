FROM python:3.11-slim
# creating a working directorate

WORKDIR /app
 
#Requirements loading
COPY requirements.txt .
RUN apt-get update -y && apt-get upgrade -y && apt-get install -y build-essential && rm -fr /var/lib/apt/lists/*
RUN pip install -r requirements.txt



#Loading the rest components
COPY fastapi_app.py .


#Loading and managing the entrypoint.sh permitions
COPY entrypoint.sh .
#managing perms
RUN chmod +x entrypoint.sh

#Copy the rest of application files 
COPY . .

ENTRYPOINT ["./entrypoint.sh"]