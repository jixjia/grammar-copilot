import logging
import json
from azure.data.tables import TableServiceClient, TableClient
from datetime import datetime 
from . import config

# Logging
logging.basicConfig(level=logging.WARNING)

def create_entity(row_key, data):

    table_service_client  = TableServiceClient.from_connection_string(conn_str=config.TABLE_STORAGE_CONNECTION_STRING)
    table_client = table_service_client.get_table_client(table_name=config.TABLE_NAME)
    
    entity = {
        u'PartitionKey': datetime.now().strftime('%Y%m%d'),
        u'RowKey': row_key,
        u'data': data    
    }
    
    try:
        table_client.create_entity(entity=entity)
        return True
    
    except Exception as e:
        logging.error(f'[azuretable_error] {e.args}')
        return False

def retrieve_entity(table_name, query_filter):
    try:
        table_client = TableClient.from_connection_string(
            conn_str=config.TABLE_STORAGE_CONNECTION_STRING, 
            table_name=table_name
            )

        entities = table_client.query_entities(query_filter=query_filter, select=["RowKey", "data"])
        results = []
        for entity in entities:
            object_id = entity['RowKey']
            data = json.loads((entity['data']))
            results.append({'object_id': object_id, 'data': data})
        
        return results
    except Exception as e:
        logging.error(f'[azuretable_error] {e.args}')