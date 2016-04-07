from models import proc_item
from datetime import timedelta
import json

from utils import rent_parser

def fetch_raw_data(minutes_diff=5):
    ret = proc_item.ProcItem.get_latest_items(timedelta(minutes=minutes_diff))
    result = []
    for item in ret:
        data = item.to_dict()
        del data['item_hash']
        data['last_update'] = data['last_update'].isoformat()
        result.append(data)
    return result

def fetch_parsed_for_rent_data(minutes_diff=5):
    data = fetch_raw_data(minutes_diff)
    result = rent_parser.RentParser.parse(data)
    return result
