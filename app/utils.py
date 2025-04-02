"""This module defines some repeated functions throughout the project."""
import boto3
import json
import googlemaps


def get_secret(secret_name, region_name):
    """Fetch secret value from AWS Secrets Manager"""
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        response = client.get_secret_value(SecretId=secret_name)
        if 'SecretString' in response:
            return json.loads(response['SecretString'])  # Returns a dictionary
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        return None
