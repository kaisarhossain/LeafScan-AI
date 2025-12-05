## Use the official Python 3.12 image
FROM python:3.12

## Set the working directory to /code
WORKDIR /code

## Copy the current directory contents into the container at /code
COPY ./requirements.txt /code/requirements.txt
#COPY --chown=user ./requirements.txt requirements.txt

## Run requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

#COPY --chown=user . /app
#CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]

## Setting up new user named "user"
RUN useradd user
#RUN useradd -m -u 1000 user
## Switch to the user "user"
USER user

## Set the home directory to user's home directory
#ENV PATH="/home/user/.local/bin:$PATH"
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

## Set the working directory to the user's home directory
WORKDIR $HOME/app

## Copy the current directory contents into the container at $HOME/app
COPY --chown=user . $HOME/app

## Starting the FastAPI App on port 7860
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]