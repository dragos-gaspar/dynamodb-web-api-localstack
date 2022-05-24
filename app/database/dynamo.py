import os
from typing import Any

from botocore.exceptions import ClientError
from localstack_client import session as boto3


OP_MAP = {
    'lt': '<',
    'lte': '<=',
    'gt': '>',
    'gte': '>='
}


def get_localstack_resource(service: str) -> Any:
    """
    Get a localstack-client resource using the endpoint
    set in the AWS_ENDPOINT environment variable.

    :param service: name of the localstack resource
    :return: localstack resource instance
    """

    aws_endpoint = os.getenv('AWS_ENDPOINT')

    if aws_endpoint is None:
        boto3_session = boto3.Session()
    else:
        boto3_session = boto3.Session(localstack_host=aws_endpoint)

    return boto3_session.resource(service)


def convert_to_dot_notation(obj: Any, parent: str = '') -> dict:
    """
    Takes a dictionary tree structure and returns the leaves
    identified by the path taken to them in dot notation.

    :param obj: dictionary
    :param parent: optional prefix; used for recursion
    :return: dictionary containing {path: value} pairs
    """

    if parent == '':
        separator = ''
    else:
        separator = '.'

    if isinstance(obj, dict):
        out = {}
        for k in obj:
            out.update(convert_to_dot_notation(obj[k], parent + separator + k))
    elif isinstance(obj, list):
        out = {}
        for i in range(len(obj)):
            out.update(convert_to_dot_notation(obj[i], parent + f"[{str(i)}]"))
    else:
        return {parent: obj}

    return out


def construct_update_syntax(method: str, fields: dict):
    update_expression = f'{method} '
    expression_attribute_values = {}

    ids = list(range(len(fields.keys())))

    for i, path in zip(ids, fields):
        update_expression += path + f' = :{str(i)}'
        if i < max(ids):
            update_expression += ', '

        expression_attribute_values.update({f':{i}': fields[path]})

    return update_expression, expression_attribute_values


def construct_query_syntax(method: str, fields: dict):

    keys = list(fields.keys())
    vals = list(fields.values())

    key_expression = f'{keys[0]} = :0 AND {keys[1]} {OP_MAP[method]} :1'
    expression_attribute_values = {
        ':0': vals[0],
        ':1': vals[1]
    }

    return key_expression, expression_attribute_values


class DynamodbClient:
    def __init__(self):
        print("Initializing dynamodb client...")

        try:
            self.dynamo = get_localstack_resource('dynamodb')

            from .schema import schema
            self.schema = schema
            for table in schema:
                try:
                    self.dynamo.create_table(**table)
                    print(f"Created table {table.get('TableName')}")
                except ClientError as error:
                    if error.response["Error"]["Code"] == "ResourceInUseException":
                        pass
                    else:
                        raise ClientError from error

            self.init = True

        except Exception as error:
            print(f'ERROR: {type(error)} {error}')

    def check_if_table_exists(self, table_name):
        try:
            self.dynamo.meta.client.describe_table(TableName=table_name)
            return True
        except self.dynamo.meta.client.exceptions.ResourceNotFoundException:
            return False

    def get_tables_names(self):
        table_names = {"tables": [table.name for table in list(self.dynamo.tables.all())]}
        return table_names

    def print_table(self, table_name: str):
        table = self.dynamo.Table(table_name)
        response = table.scan()
        items = response["Items"]

        while "LastEvaluatedKey" in response:
            response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            items.extend(response["Items"])

        return items

    def insert(self, table_name: str, item: dict):
        try:
            self.dynamo.meta.client.describe_table(TableName=table_name)
        except self.dynamo.meta.client.exceptions.ResourceNotFoundException:
            # return error
            return

        table = self.dynamo.Table(table_name)
        table.put_item(Item=item)

    def query_table(self, table_name: str, query: dict):
        if not self.check_if_table_exists(table_name):
            return f"No such table {table_name}"

        table = self.dynamo.Table(table_name)
        response = table.get_item(Key=query)

        return response.get("Item")

    def query_gsi(self, table_name: str, query: dict, cond: str):
        if not self.check_if_table_exists(table_name):
            return f"No such table {table_name}"

        table = self.dynamo.Table(table_name)

        key_expression, expression_attribute_values = construct_query_syntax(cond, query)

        response = table.query(
            IndexName='PublisherIndex',
            KeyConditionExpression=key_expression,
            ExpressionAttributeValues=expression_attribute_values
        )

        return response.get("Items")

    def query_lsi(self, table_name: str, query: dict, cond: str):
        if not self.check_if_table_exists(table_name):
            return f"No such table {table_name}"

        table = self.dynamo.Table(table_name)

        key_expression, expression_attribute_values = construct_query_syntax(cond, query)

        response = table.query(
            IndexName='ArtistSoldIndex',
            KeyConditionExpression=key_expression,
            ExpressionAttributeValues=expression_attribute_values
        )

        return response.get("Items")

    def update_entry(self, table_name: str, query: dict):
        if not self.check_if_table_exists(table_name):
            return f"No such table {table_name}"

        table = self.dynamo.Table(table_name)

        # Get table schema
        table_schema = table.key_schema

        # Split key and update attributes
        schema_keys = [k["AttributeName"] for k in table_schema]
        keys = {key: query[key] for key in schema_keys}
        updates = query.copy()
        for k in keys:
            del updates[k]

        # Construct API update syntax
        update_expression, expression_attribute_values = construct_update_syntax('set', updates)

        response = table.update_item(
            Key=keys,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW"
        )

        return f"Updated {response['Attributes']}"

    def delete_entry(self, table_name: str, query: dict):
        try:
            self.dynamo.meta.client.describe_table(TableName=table_name)
        except self.dynamo.meta.client.exceptions.ResourceNotFoundException:
            # return error
            return

        table = self.dynamo.Table(table_name)
        response = table.delete_item(Key=query)

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return {"Successfully deleted entry": query}
        else:
            return f"Error {response['ResponseMetadata']['HTTPStatusCode']}"
