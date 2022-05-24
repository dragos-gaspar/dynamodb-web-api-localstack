schema = [
    {
        "TableName": "Music",
        "KeySchema": [
            {"AttributeName": "Artist", "KeyType": "HASH"},
            {"AttributeName": "SongTitle", "KeyType": "RANGE"},
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "PublisherIndex",
                "KeySchema": [
                    {"AttributeName": "Publisher", "KeyType": "HASH"},
                    {"AttributeName": "CopiesSold", "KeyType": "SORT"}
                ],
                "Projection": {
                    "ProjectionType": "ALL"
                },
                "ProvisionedThroughput": {"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
            }
        ],
        "LocalSecondaryIndexes": [
            {
                'IndexName': "ArtistSoldIndex",
                'KeySchema': [
                    {'AttributeName': 'Artist', 'KeyType': 'HASH'},
                    {'AttributeName': 'CopiesSold', 'KeyType': 'RANGE'},
                ],
                "Projection": {
                    "ProjectionType": "ALL"
                },
            }
        ],
        "AttributeDefinitions": [
            {"AttributeName": "Artist", "AttributeType": "S"},
            {"AttributeName": "SongTitle", "AttributeType": "S"},
            {"AttributeName": "Publisher", "AttributeType": "S"},
            {"AttributeName": "CopiesSold", "AttributeType": "N"},
        ],
        "ProvisionedThroughput": {"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
    }
]
