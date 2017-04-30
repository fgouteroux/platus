#!/usr/bin/env python
# coding: utf-8

'''
aws ec2 plugin
--------------
'''
__author__ = "François Gouteroux <francois.gouteroux@gmail.com>"

# Import Python libs
from datetime import datetime

# Import third party libs
import boto3
from flask import current_app as app

def _update_instance_states(client, instance_states, instance_ids=None):
    """Describes the status of one or more instances

    Args:
        client (str): aws ec2 client
        instance_states (dict): instance states
        instance_ids (Optional[str]): aws instances ids

    Returns:
        dict: updated instance states

    Raises:
        n/a: This function didn't raise.

    Usage:
        >>> _update_instance_states(client, instance_states)
    """
    paginator = client.get_paginator('describe_instance_status')

    if instance_ids is not None:
        page_iterator = paginator.paginate(InstanceIds=instance_ids)
    else:
        page_iterator = paginator.paginate()

    for result in page_iterator:
        for item in result["InstanceStatuses"]:

            if item["SystemStatus"]["Status"] != "ok"\
            or item["InstanceStatus"]["Status"] != "ok":

                for instance_state in instance_states:
                    if instance_state["node"] == item["InstanceId"]:
                        instance_state["state"] = "unhealthy"

    return instance_states

def login(region, access_key, secret_key):
    """Login to aws ec2 service

    Args:
        region (str): aws region
        access_key (str]): aws access_key
        secret_key (str): aws secret_key

    Returns:
        botocore.client.EC2: client connection object

    Raises:
        n/a: This function didn't raise.

    Usage:
        >>> login(region="eu-central-1",
                  access_key="azerty123",
                  secret_key="1a2b3c4d5)
    """
    client = boto3.client(
        'ec2',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )

    return client


def check_health(client, data):
    """Check aws ec2 plugin health

    Args:
        botocore.client.EC2: client connection object
        data (dict): data

    Returns:
        status (dict): aws ec2 plugin status.

    Raises:
        RuntimeError: Unable to check aws ec2 plugin health.

    Usage:
        >>> check_health(client, data)
    """
    try:

        # Some AWS operations return results that are incomplete and require
        # subsequent requests in order to attain the entire result set.
        # See http://boto3.readthedocs.io/en/latest/guide/paginators.html and
        # http://boto3.readthedocs.io/en/latest/reference/services/ec2.html#paginators

        operation_parameters = {}
        instance_states = []
        instance_ids = []

        if data.get("ec2_instance_ids", False):
            operation_parameters["InstanceIds"] = data["ec2_instance_ids"]

        if data.get("ec2_filters", False):
            operation_parameters["Filters"] = data["ec2_filters"]

        # Create a reusable Paginator
        paginator = client.get_paginator('describe_instances')

        # Create a PageIterator from the Paginator
        page_iterator = paginator.paginate(**operation_parameters)

        for result in page_iterator:
            if result["Reservations"]:
                for item in result["Reservations"][0]["Instances"]:
                    instance_ids.append(item["InstanceId"])

                    status = {
                        "type": data["type"],
                        "name": data["name"],
                        "node": item["InstanceId"],
                        "checked": str(datetime.now())
                    }
                    for tag in item["Tags"]:
                        if tag and tag["Key"] == "Name":
                            status["nodename"] = tag["Value"]

                    if item["State"]["Name"] == "running":
                        status["state"] = "operational"
                        instance_ids.append(item["InstanceId"])
                    else:
                        status["state"] = "down"

                    instance_states.append(status)

        # If instance state is runnning, perform instance status check
        # http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/monitoring-system-instance-status-check.html
        if instance_ids:
            _update_instance_states(client, instance_states, instance_ids=instance_ids)

        return instance_states

    except Exception as error_msg:
        app.logger.error("aws_ec2 - {0} => {1}".format(data["name"], error_msg))

        return {"type": data["type"],
                "name": data["name"],
                "node": "n/a",
                "state": "unknown",
                "checked": str(datetime.now())
               }
