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

### Request Body
The lambda is configured to respond to an AWS-PROXY API gateway integration meaning the request needs to follow this structure:

```json
{
  "queryStringParameters": {
    "id": "PROPERTY_ID"
  },
  "headers": {},
  "body": "{\"STRINGIFIED\": \"JSON\"}"
}
```

When passing this body to the curl request, pass it in as a string:

```
'{"queryStringParameters": {"id": "PROPERTY_ID"},"headers": {},"body": "{\"STRINGIFIED\": \"JSON\"}"}'
```

### Secrets
The `docker-compose` script relies on a `.env` file which requires the following secrets to be defined:

- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY


## Deployments
This project is deployed using GitHub Actions executing the following stages:

- Run unit tests
- Publish Docker image to ECR
- Plan and Apply Terraform

Publishing to ECR and Terraform Apply will only run on master branches.
