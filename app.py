# WHY: Import Flask to create web server
from flask import Flask, render_template, jsonify

# WHY: boto3 is AWS SDK for Python
# Lets us talk to AWS services
import boto3

# WHY: os reads environment variables
import os

# WHY: load_dotenv reads our .env file
from dotenv import load_dotenv

# WHY: This will reads the .env file
load_dotenv()

# WHY: Create Flask app
app = Flask(__name__)
print("Testing")

# WHY: Create AWS session using our credentials
# This authenticates all our AWS API calls
session = boto3.Session(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)
@app.route("/test")
def test():
    sts = session.client("sts")
    identity = sts.get_caller_identity()

    return {
        "Account": identity["Account"],
        "Arn": identity["Arn"],
        "UserId": identity["UserId"]
    }

# ─────────────────────────────────────
# FUNCTION: Get EC2 Instances
# WHY: Fetches all EC2 instances from AWS
# Returns their ID, type, and state
# ─────────────────────────────────────
def get_ec2_instances():
    try:
        # WHY: Create EC2 client to talk to EC2 service
        ec2 = session.client("ec2")

        # WHY: describe_instances() fetches ALL instances
        response = ec2.describe_instances()
        instances = []

        # WHY: Loop through reservations to get instances
        # AWS groups instances in "Reservations"
        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                # WHY: Extract only what we need to display
                instances.append({
                    "id": instance["InstanceId"],
                    "type": instance["InstanceType"],
                    "state": instance["State"]["Name"],
                    # WHY: Some instances have no public IP
                    # so we use "N/A" as default
                    "public_ip": instance.get("PublicIpAddress", "N/A"),
                    "region": os.getenv("AWS_REGION")
                })
        return instances
    except Exception as e:
        # WHY: If anything goes wrong return empty list
        # App won't crash - just shows 0 instances
        print(f"EC2 Error: {e}")
        return []

# ─────────────────────────────────────
# FUNCTION: Get S3 Buckets
# WHY: Fetches all S3 buckets from AWS
# ─────────────────────────────────────
def get_s3_buckets():
    try:
        # WHY: S3 is global so no region needed
        s3 = session.client("s3")
        response = s3.list_buckets()
        buckets = []

        for bucket in response["Buckets"]:
            buckets.append({
                "name": bucket["Name"],
                # WHY: Format date to readable string
                "created": bucket["CreationDate"].strftime("%Y-%m-%d")
            })
        return buckets
    except Exception as e:
        print(f"S3 Error: {e}")
        return []

# ─────────────────────────────────────
# FUNCTION: Get RDS Databases
# WHY: Fetches all RDS database instances
# ─────────────────────────────────────
def get_rds_instances():
    try:
        rds = session.client("rds")
        response = rds.describe_db_instances()
        databases = []

        for db in response["DBInstances"]:
            databases.append({
                "id": db["DBInstanceIdentifier"],
                "engine": db["Engine"],
                "status": db["DBInstanceStatus"],
                "size": db["DBInstanceClass"]
            })
        return databases
    except Exception as e:
        print(f"RDS Error: {e}")
        return []

# ─────────────────────────────────────
# FUNCTION: Get Lambda Functions
# WHY: Fetches all Lambda functions
# ─────────────────────────────────────
def get_lambda_functions():
    try:
        lambda_client = session.client("lambda")
        response = lambda_client.list_functions()
        functions = []

        for fn in response["Functions"]:
            functions.append({
                "name": fn["FunctionName"],
                "runtime": fn["Runtime"],
                "memory": fn["MemorySize"],
                "last_modified": fn["LastModified"]
            })
        return functions
    except Exception as e:
        print(f"Lambda Error: {e}")
        return []

# ─────────────────────────────────────
# ROUTE: Homepage
# WHY: Loads the dashboard HTML page
# Passes all AWS data to the template
# ─────────────────────────────────────
@app.route("/")
def index():
    # WHY: Fetch all resources when page loads
    ec2 = get_ec2_instances()
    s3 = get_s3_buckets()
    rds = get_rds_instances()
    lambdas = get_lambda_functions()

    # WHY: Pass data to HTML template
    # Template uses this data to display
    return render_template("index.html",
        ec2_instances=ec2,
        s3_buckets=s3,
        rds_instances=rds,
        lambda_functions=lambdas,
        # WHY: Pass counts for summary cards
        ec2_count=len(ec2),
        s3_count=len(s3),
        rds_count=len(rds),
        lambda_count=len(lambdas)
    )

# ─────────────────────────────────────
# ROUTE: API endpoint
# WHY: Returns raw JSON data
# Useful for refreshing without reload
# ─────────────────────────────────────
@app.route("/api/resources")
def api_resources():
    return jsonify({
        "ec2": get_ec2_instances(),
        "s3": get_s3_buckets(),
        "rds": get_rds_instances(),
        "lambda": get_lambda_functions()
    })

# WHY: Start Flask server
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 3000)),
        # WHY: debug=True shows errors and
        # auto restarts when code changes
        debug=True
    )
