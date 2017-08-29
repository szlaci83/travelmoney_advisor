import json

def currencies():
    json_data = json.loads(open('currency_list.json').read())
    print(json_data["USD"]["PLN"])


currencies()