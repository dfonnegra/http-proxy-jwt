# HTTP PROXY for castlabs

The project consists of a proxy endpoint that appends a JWT token to a remote service, 
In this case "https://postman-echo.com/post/", with the following claims:

- iat - Timestamp of the request as specified by the specification
- jti- A cryptographic nonce that should be unique
- payload - A json payload of the structure: `{"user": "username", "date": "todays date"}`

On the other hand, the server counts the number of requests since last build and the uptime.

## Build
Building the project is really simple

`$ git clone https://github.com/dfonnegra/http-proxy-jwt.git && cd http-proxy-jwt && make build`

## Run
To run the project

`$ make run`

## Usage
The RESTful API is built with FastAPI and contains 3 endpoints:
- /login: To log as an user, which is required before using the / endpoint. To login you must execute

    ```curl -X POST "http://localhost:13139/token" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "username=castlabs&password=insane-safe-password"```
    
    which aunthenticates to the server with the OAuth2 authentication protocol. This will return a schema:
    
    `{
      "access_token": "token",
      "token_type": "bearer"  
    }` 
- /: This is the proxy endpoint, to execute it, you must send the authorization token returned with the /login endpoint:

    `curl -X POST "http://localhost:13139/" -H "accept: application/json" -H "Authorization: Bearer token" -d ""`

- /status: This status page shows the time since the container was run for the first time and the number of calls to the
/ endpoint in that time.


