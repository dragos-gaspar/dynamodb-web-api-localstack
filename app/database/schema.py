schema = [
    {
        "TableName": "Music",
        "KeySchema": [
            {"AttributeName": "Artist", "KeyType": "HASH"},
            {"AttributeName": "SongTitle", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "Artist", "AttributeType": "S"},
            {"AttributeName": "SongTitle", "AttributeType": "S"},
        ],
        "ProvisionedThroughput": {"ReadCapacityUnits": 10, "WriteCapacityUnits": 10},
    }
]
