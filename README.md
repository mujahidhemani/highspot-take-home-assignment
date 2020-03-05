# Highspot Take-Home Coding Exercise
This Flask service will store the contents of a POST request made to an `endpoint` resource. Uses an SQLite 3 database as its backend storage. 

## Requirements
- Docker
- Make

## Python Dependencies
- Flask         Python WSGI web application framework
- healthcheck   Healthcheck library by Runscope
- six           A dependency of healthcheck, for some reason not installed automatically

## Development
If you want to build and run locally for development, you will also need Python 3.7 installed. A dedicated Python virtual environment is highly recommended to isolate Python dependencies from your system's Python installation and from other Python projects

```console
$ python3 -m venv ~/highspot-venv
$ source ~/highspot-venv/bin/activate
```

Once inside your new venv, you should be able to `pip install -r requirements.txt` without any issues. To run locally, within the venv:

```console
(highspot-venv) $ cd highspot/
(highspot-venv) $ python app.py
```

## Makefile
- `all` - Runs `build`, `init-db` and `run`. This is the default target, so when you run `make` in your shell, it will execute this target
- `build` - Builds Docker image
- `init-db` - Creates the database file using `touch`
- `run` - Starts the Docker container, mounts the database file to the container, maps port 8080 to the container
- `stop` - Stops and removes the container
- `rm-db` - Removes the database file ** This is a destructive operation! **
- `clean` - Removes the built Docker image

## Usage
NOTE: Only `Content-Type: application/json` is supported!

1. Use `make` to build and run in Docker
    ```console
    mhemani-m1:highspot-take-home mhemani$ make
    Starting image build...
    Sending build context to Docker daemon  150.5kB
    Step 1/8 : FROM python:3.7-alpine
    ---> 39fb80313465
    Step 2/8 : COPY ./requirements.txt /app/requirements.txt
    ---> Using cache
    ---> 5e799770ba28
    Step 3/8 : WORKDIR /app
    ---> Using cache
    ---> accab5ec336f
    Step 4/8 : RUN pip install -r requirements.txt
    ---> Using cache
    ---> 3b2681b38d43
    Step 5/8 : COPY ./highspot/* /app/
    ---> Using cache
    ---> 2497f9cff421
    Step 6/8 : ENTRYPOINT [ "python" ]
    ---> Using cache
    ---> c6a9b1e14f4a
    Step 7/8 : CMD [ "app.py" ]
    ---> Using cache
    ---> b725d3d31034
    Step 8/8 : EXPOSE 8080
    ---> Using cache
    ---> 762b8ed7c451
    Successfully built 762b8ed7c451
    Successfully tagged highspot:latest
    Creating database file...
    Stopping container...
    highspot
    Removing container...
    highspot
    Starting Docker container
    fee1d987c69d5b159a4606c64af9ed963f1b44e3f25f02f121f473557776e090
    ```
2. Create a unique endpoint resource. You can use a tool like Postman or cURL:
    ```console
    mhemani-m1:highspot-take-home mhemani$ curl -i localhost:8080/api/v1/resources/endpoint/gen
    HTTP/1.0 201 CREATED
    Content-Type: application/json
    Content-Length: 50
    Server: Werkzeug/1.0.0 Python/3.7.4
    Date: Wed, 04 Mar 2020 23:48:41 GMT

    {
        "uri": "/api/v1/resources/endpoint?id=8100"
    }
    ```
3. Send data to be stored, using the unique endpoint resource id returned from step 2:
    ```console
    mhemani-m1:highspot-take-home mhemani$ curl -X POST \
    > -d '{"value":"123"}' \
    > -H "Content-Type:application/json" \
    > localhost:8080/api/v1/resources/endpoint?id=8100
    {
        "request": "{'value': '123'}"
    }
    ```
4. Get data from a specific endpoint:
    ```console
    mhemani-m1:highspot-take-home mhemani$ curl -i localhost:8080/api/v1/resources/endpoint?id=8100
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 48
    Server: Werkzeug/1.0.0 Python/3.7.4
    Date: Thu, 05 Mar 2020 00:07:29 GMT

    {
        "post_data": [
            "{'value': '123'}"
        ]
    }
    ```
5. Get the latest entry POSTed to the service:
    ```console
    mhemani-m1:highspot-take-home mhemani$ curl -i localhost:8080/api/v1/resources/endpoint/latest
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 48
    Server: Werkzeug/1.0.0 Python/3.7.4
    Date: Thu, 05 Mar 2020 00:19:26 GMT

    {
        "post_data": [
            "{'value': '456'}"
        ]
    }
    ```

## Notes
- Flask and SQLite were chosen as the framework and the datastore, as they are very easy to develop and support. Also there are plenty of resources online to assist, if you get stuck
- SQLite requires a trigger to update the timestamp after an UPDATE to a row. This is handled by a trigger in the DB schema
- This container image is based off Alpine Linux. This was chosen to keep the resulting image as small as possible.
- `make` is awesome. This should help developers build and test the service quickly, as they don't have to worry about the underlying Docker commands.
- The database is mounted to the container from local disk. This makes it persistent, otherwise it would be lost when stopping & deleting the container
- The API is structured as `/api/v1/resources/<resource>`. Currently there is just one resource: `endpoint`, but this structure allows a developer to add new resources, with their own methods. It also allows you to increment the version of the API without breaking existing resources.

- Random number generation is used to create the ID of the `endpoint` resource. There is a finite range of numbers in the range (1000-9999), this should be refactored to autoincrement in the DB schema
- The service may not be returning an entirely JSON-friendly response when retriving the latest POST or a particular endpoint's POST data. Some additional tweaking might be required to strip some of the uneccessary quotes from the JSON response. 
- Using SQL language queries from within the web service makes it vulnerable to SQL injection attacks. Either need to add some functionality to sanitize inputs, or refactor using SQLAlchemy to abstract the SQL queries

## TODO
- Fix API responses when retrieving POST body from the database. Looks like there are some unneccessary quotes in the JSON response that need to be stripped/fixed
- Unit tests - This would be really helpful to verify API methods are working as expected
- Protection against SQL injections - Need to sanitize inputs or refactor using something like SQLAlchemy
- Error handling - There is currently no error handling, stack traces are thrown directly to the console
- CI/CD - This should be fairly easy to setup on CircleCI, dependent on unit tests. Ideally this should deploy to a container registry like Docker Hub

