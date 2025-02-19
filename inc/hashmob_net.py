#!/bin/env python3
import base64
import requests
import json

def submit_request_post(url, request_json_data, files, api_key=None):
    # Make a POST web request to Hashtopolis using APIv1 to submit the new hashlist wih 'Content-Type: application/json' header.
    # If the request is successful, then Hashtopolis will return a JSON object with the new hashlist ID.
    # Example: {"section":"hashlist","request":"createHashlist","response":"OK","hashlistId":198}
    # If the request is not successful, then Hashtopolis will return a JSON object with an error message.
    # Example: {"section":"hashlist","request":"createHashlist","response":"ERROR","message":"Invalid hashlist format!"}
    # request_json_data = json.loads(request_json_data)
    try:
        default_headers = requests.utils.default_headers()
        default_headers['api-key'] = api_key
        # print(json.dumps(request_json_data, indent=4))
        response = requests.post(url, json=request_json_data, files=files, headers=default_headers)
        if response.status_code == 200:
            return response.text
        else:
            print("Error: %s" % (response.text))
            return None
    except requests.exceptions.ConnectionError as error_code:
        print('Failed to connect to the Hashmob.net server. Error: %s' % error_code)
        return None
    except requests.exceptions.RequestException as error_code:
        print('Error: %s' % error_code)
        return None
    except FileNotFoundError:
        print("Error: File not found.")
        return None
    except Exception as error_code:
        print('Error: %s' % error_code)
        return None

def submit_request_get(url):
    # Make a GET web request to Hashtopolis using APIv1 to retrieve a JSON object with all hashlists.
    # If the request is successful, then Hashtopolis will return a JSON object with all hashlists.
    # Example: [{"id":198,"name":"hashlist1","hashType":0,"hashCount":0,"progress":0,"visibility":0,"creator":"admin","created":"2021-06-04T22:56:41.000000Z","updated":"2021-06-04T22:56:41.000000Z","official":0}]
    # If the request is not successful, then Hashtopolis will return a JSON object with an error message.
    # Example: {"section":"hashlist","request":"getHashlists","response":"ERROR","message":"Invalid request!"}
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print("Error: %s" % (response.text))
            return None
    except requests.exceptions.ConnectionError as error_code:
        print('Failed to connect to the Hashmob.net server. Error: %s' % error_code)
        return None
    except requests.exceptions.RequestException as error_code:
        print('Error: %s' % error_code)
        return None
    except FileNotFoundError:
        print("Error: File not found.")
        return None
    except Exception as error_code:
        print('Error: %s' % error_code)
        return None

def filter_hashlists_by_hashtype(hashlists, target_hash_type_number):
    filtered_hashlists = []
    # For each hashlist, print the hashlist name and the number of found hashes
    if hashlists:
        # hashlists = json.loads(hashlists)
        for hashlist in hashlists:
            # Check if the hashlist is null
            if hashlist:
                if hashlist['hash_type'] == target_hash_type_number:
                    # Get the number of hashes left to crack by subtracting the number of found hashes from the total number of hashes
                    hashes_left = hashlist['total_hashes'] - hashlist['found_hashes']
                    hashlist['left_to_crack'] = hashes_left
                    filtered_hashlists.append(hashlist)
    return filtered_hashlists

def display_hashlists(hashlists):
    # For each hashlist, print the hashlist name and the number of found hashes
    for hashlist in hashlists:
        print("ListType %s, HashListID: %s, HashType: %s, TotalHashes: %s, Found Hashes: %s, LeftToCrack: %s, Hashlist: %s" % \
            (hashlist['list_type'], hashlist['id'], hashlist['hash_type'], hashlist['total_hashes'], hashlist['found_hashes'], hashlist['left_to_crack'], hashlist['name']))

def get_user_hashlists(hashmob_url):
    # URL: "/api/v2/hashlist"
    # List all processed hashlists
    # Returns a JSON object with all hashlists
    # Example returned data:
    #     [
    #   {
    #     "id": 1155,
    #     "name": "The Ancient Greek villager database",
    #     "hash_type": 120,
    #     "found_hashes": 1258900,
    #     "total_hashes": 3512235,
    #     "progress": 100,
    #     "visibility": 2,
    #     "created_at": "2021-05-11T09:20:16.000000Z",
    #     "updated_at": "2021-06-04T22:56:41.000000Z",
    #     "official": 1,
    #     "notes": "This particular list makes use of the pepper: \"GreekKings\" and two salts: \"alpha\" and \"beta\". They are in the format of: sha1($pepper.$pass.$salt)",
    #     "algorithms": [
    #       {
    #         "algorithm": "sha1($salt.$pass)",
    #         "hash_type": "120",
    #         "found": 1258900
    #       }
    #     ],
    #     "creator_name": "Alexander The Great",
    #     "algorithm": "sha1($salt.$pass)"
    #   }
    # ]
    hashmob_url = hashmob_url + '/api/v2/hashlist'
    hashlists = json.loads(submit_request_get(hashmob_url))
    for hashlist in hashlists:
        hashlist['list_type'] = 'user'
    return hashlists

def get_official_hashlists(hashmob_url):
    hashmob_url = hashmob_url + '/api/v2/hashlist/official'
    hashlists = json.loads(submit_request_get(hashmob_url))
    # For each hashlist add the value of 'official' to the hashlist
    for hashlist in hashlists:
        hashlist['list_type'] = "official"
    return hashlists

def get_premium_hashlists(hashmob_url):
    hashmob_url = hashmob_url + '/api/v2/hashlist/premium'
    hashlists = json.loads(submit_request_get(hashmob_url))
    # For each hashlist add the value of 'premium' to the hashlist
    for hashlist in hashlists:
        hashlist['list_type'] = "premium"
    return hashlists

def get_all_hashlists(hashmob_url, target_hash_type_number):
    all_hashlist_jsons = []
    hashlist_json = get_user_hashlists(hashmob_url)
    if hashlist_json:
        all_hashlist_jsons.append(hashlist_json)
    hashlist_json = get_official_hashlists(hashmob_url)
    if hashlist_json:
        all_hashlist_jsons.append(hashlist_json)
    hashlist_json = get_premium_hashlists(hashmob_url)
    if hashlist_json:
        all_hashlist_jsons.append(hashlist_json)
    # Filter all_hashlist_jsons by target_hash_type_number, create a list of hashlists with the target_hash_type_number.
    target_hashlists = []
    for hashlist_json in all_hashlist_jsons:
        # hashlists = json.loads(hashlist_json)
        hashlists = hashlist_json
        for hashlist in hashlists:
            if hashlist['hash_type'] == target_hash_type_number:
                target_hashlists.append(hashlist)
    return target_hashlists

def download_hashlist_left_hashes(hashmob_url, hashlistid):
    hashmob_url = "%s/api/v2/hashlist/%s/left" % (hashmob_url, hashlistid)
    return submit_request_get(hashmob_url)

def submit_cracked_hashes(hashmob_url, hashmob_api_key, found_hashes, hash_type_number):
    # URL: "/api/v2/submit"
    # Submit founds for hashes
    # Example request data:
    #{
    #   "algorithm": 1000,
    #   "founds": [
    #     "539f58ccb6d2ec23f01a11090101da28:Working.Yeti2",
    #     "396059a932c697260648a193560c41a6:Sitocheader1",
    #     "98887c5f8d484bbd4df6fe030e258db8:habikonteeth"
    #   ]
    # }
    hashmob_url = "%s/api/v2/submit" % hashmob_url
    request_json_data = {
        "algorithm": hash_type_number,
        "founds": []
    }
    # Foreach line in the found_hashes string, add the line to the request_json_data['founds'] list
    for line in found_hashes.splitlines():
        request_json_data['founds'].append(line)
    return submit_request_post(hashmob_url, request_json_data, None, hashmob_api_key)

def download_found_hashes(hashmob_url, hashlistid, hash_type_number):
    hashmob_url = "%s/api/v2/hashlist/%s/found/%s" % (hashmob_url, hashlistid, hash_type_number)
    return submit_request_get(hashmob_url)

def get_hashlist_details(hashmob_url, hashlistid):
    hashmob_url = "%s/api/v2/hashlist/%s" % (hashmob_url, hashlistid)
    return submit_request_get(hashmob_url)