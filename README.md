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


## Tests
Tests are run using `pytest`. All tests will be run as part of the CICD but can also be run locally. 

### Integration Tests
The integration tests require a local instance of DynamoDB to be running. This can be done using docker:

```
docker pull amazon/dynamodb-local
docker run amazon/dyamodb-local -p 8000:8000
```

With the local DB running, run the following command:

```
pytest ./tests/integration
```


## The Database
The property service is responsible for providing 2 main sets of data for Revlet; property data and review data. There is a 1 to many relationship between properties and reviews. 

Initially the plan was to have a separate service responsible for managing review data, however this would involve more database calls and higher hosting costs. DynamoDB also doesnt support JOIN functionality, meaning retrieving all the reviews for a specific property gets a little more complicated.

Instead, reviews are included within the property service database using a [Global Secondary Index with Query](https://www.alexdebrie.com/posts/dynamodb-one-to-many/#secondary-index--the-query-api-action) structure. The database includes 2 keys; 1 for the property ID and 1 defining the type of data being returned from the request (metadata or review). This allows the database to be structured in first normal form and reduce data duolication.

Properties are added to the database with a key of PROPERTY# and reviews added with a key of REVIEW#. Both will include a `reviewIndexPK` and `reviewIndexSK`, attributes used to become the PK and SK of the global secondary index.

This leverages DynamoDBs concept of item collections where items can share the same key but then identified by a composite key. All items with the same partition key will be stored together.