import os
import json
import boto3

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    try:
        # Extract bucket and key
        bucket_name = event["detail"]["bucket"]["name"]
        object_key = event["detail"]["object"]["key"]

        # Create unique identifier for this ECS task
        started_by = f"{bucket_name}/{object_key}"

        ecs = boto3.client("ecs")

        # List tasks started with this identifier (no other filters!)
        existing_task_arns = ecs.list_tasks(
            cluster=os.environ["ECS_CLUSTER"],
            startedBy=started_by
        ).get("taskArns", [])

        if existing_task_arns:
            # Describe tasks to check if any are RUNNING
            tasks = ecs.describe_tasks(
                cluster=os.environ["ECS_CLUSTER"],
                tasks=existing_task_arns
            ).get("tasks", [])

            running_tasks = [t for t in tasks if t.get("lastStatus") == "RUNNING"]

            if running_tasks:
                print(f"ECS task already running for {started_by}. Skipping new launch.")
                return {
                    "statusCode": 200,
                    "body": "Duplicate event detected. ECS task already running."
                }

        # Launch a new ECS task
        response = ecs.run_task(
            cluster=os.environ["ECS_CLUSTER"],
            launchType="FARGATE",
            taskDefinition=os.environ["ECS_TASK_DEFINITION"],
            startedBy=started_by,
            networkConfiguration={
                "awsvpcConfiguration": {
                    "subnets": json.loads(os.environ["SUBNET_IDS"]),
                    "securityGroups": json.loads(os.environ["SECURITY_GROUP_IDS"]),
                    "assignPublicIp": "DISABLED"
                }
            },
            overrides={
                "containerOverrides": [
                    {
                        "name": os.environ["ECS_CONTAINER_NAME"],
                        "environment": [
                            {"name": "S3_BUCKET", "value": bucket_name},
                            {"name": "S3_KEY", "value": object_key}
                        ]
                    }
                ]
            }
        )

        print("ECS task started:", response)

        return {
            "statusCode": 200,
            "body": "ECS task launched"
        }

    except Exception as e:
        print("Error:", str(e))
        raise e
