## Endpoints

```
GET   /properties
GET   /properties?id={PROPERTY_ID}
POST  /properties
```

## Testing Locally

The service uses `docker-compose` to be tested locally. Ensure the that desired function to test is set in the `Dockerfile` and run `docker-compose build` to build the image and then `docker-compose up` to bring up the container.

Once the container is running, the lambda function call can be simulated with curl commands using the following:

```
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d {}
```

### Secrets
The `docker-compose` script relies on a `.env` file which requires the following secrets to be defined:

- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY


## Deployments
- Deployed using GitHub actions
- Builds and deploys docker image to ECR
- Runs Terraform to provision lambda functions which pulls ECR images