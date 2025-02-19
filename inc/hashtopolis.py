#!/bin/env python3
import base64
import requests
import json
import os
from datetime import datetime, timedelta
import inc.algorithms as algorithms

def submit_request(htserver, request_json_data):
    # Make a POST web request to Hashtopolis using APIv1 to submit the new hashlist wih 'Content-Type: application/json' header.
    # If the request is successful, then Hashtopolis will return a JSON object with the new hashlist ID.
    # Example: {"section":"hashlist","request":"createHashlist","response":"OK","hashlistId":198}
    # If the request is not successful, then Hashtopolis will return a JSON object with an error message.
    # Example: {"section":"hashlist","request":"createHashlist","response":"ERROR","message":"Invalid hashlist format!"}
    request_json_data = json.dumps(request_json_data)
    ht_api_url = htserver + '/api/user.php'
    try:
        request = requests.post(ht_api_url, data=request_json_data, headers={'Content-Type': 'application/json'})
    except requests.exceptions.ConnectionError as error_code:
        print('Failed to connect to the Hashtopolis server. Error: %s' % error_code)
        return
    if request.status_code == 200 and 'OK' in request.text:
        return json.loads(request.text)
    if request.status_code != 200 or 'OK' not in request.text:
        # Set the error log name with the current epoch timestamp
        error_log_name = 'hashtopolis_submit_request_error_log_%s.txt' % (datetime.now().timestamp())
        with open(error_log_name, 'w') as error_log:
            error_log.write(str("Status: "  + str(request.status_code) + '\n'))
            error_log.write(str("Text: "    + str(request.text)        + '\n'))
            error_log.write(str("Content: " + str(request.content)     + '\n'))
            error_log.write(str("JSONData:" + str(request_json_data)   + '\n'))
        error_log.close()
        #error_data = '\n ErrorCode: %s, ErrorText: %s, ErrorContent: %s, ErrorLog: %s' % (
        #     str(request.status_code), str(request.text), str(request.content), error_log_name)
        error_data  = '\n ErrorCode   : %s' % (str(request.status_code))
        error_data += '\n ErrorContent: %s' % (str(request.content))
        error_data += '\n ErrorText   : %s' % (str(request.text))
        error_data += '\n ErrorLog    : %s' % (error_log_name)
        print(error_data)
        return None

def create_new_hashlist(htserver, accesskey, hashliststring, hashisSecret, hashlist_name, hashtype,
                        isSalted=False, isHexSalt=False, separator=':', format=0):
    # Create a JSON object with all the required information.
    # Example submit new Hashlist JSON.
    # {
    # "section": "hashlist",
    # "request": "createHashlist",
    # "name": "API Hashlist",
    # "isSalted": false,
    # "isSecret": true,
    # "isHexSalt": false,
    # "separator": ":",
    # "format": 0,
    # "hashtypeId": 22000,
    # "accessGroupId": 1,
    # "data": "$(base64 -w 0 hash.hc22000)",
    # "useBrain": false,
    # "brainFeatures": 0,
    # "accessKey": "mykey"
    # }

    # Trying to get 'notes' to work, but not so far.
    # notes='',

    # Check if the hashliststring is longer than "maxHashlistSize" lines limit.
    # Use the get_server_config function to get the "maxHashlistSize" value from the server.
    maxHashlistSize = int(get_server_config(htserver, accesskey, 'maxHashlistSize'))
    # Count the number of new lines in the hashliststring.
    size = hashliststring.count('\n')
    # print(size)
    if size > maxHashlistSize:
        print('The hashlist is too large. The maximum size is %s lines.' % maxHashlistSize)
        return None
    # Encode the hash variable to base64.
    hashliststring = str(hashliststring)
    hash = base64.b64encode(hashliststring.encode()).decode()

    # Get the server configuration values for hashcat brain.
    hashcatBrainEnabled = get_server_config(htserver, accesskey, 'hashcatBrainEnable')
    useBrain = False
    # If hashcatBrainEnabled is 1 (enabled), and useBrain is True, then set useBrain to 'true'.
    if hashcatBrainEnabled:
        # Check if the "hashtype" number is in the algorithms.slowalgs list.
        if int(hashtype) in algorithms.slowalgs:
            useBrain = True

    request_json_data = {
    "section": "hashlist",
    "request": "createHashlist",
    "name": "%s" % hashlist_name,
    "isSalted": isSalted,
    "isSecret": hashisSecret,
    "isHexSalt": False,
    "separator": ":",
    "format": 0,
    "hashtypeId": hashtype,
    "accessGroupId": 1,
    "data": "%s" % hash,
    "useBrain": useBrain,
    "brainFeatures":  3,
    # "notes": str(notes),
    'accessKey': "%s" % accesskey
    }
    return submit_request(htserver, request_json_data)

def create_prince_task(htserver, accesskey, hashlistId):
    # createTask
    # Create a new task (one example with files and one without).
    # {
    # "section": "task",
    # "request": "createTask",
    # "name": "API Task",
    # "hashlistId": 1,
    # "attackCmd": "#HL# -a 0 -r dive.rule example.dict",
    # "chunksize": 600,
    # "statusTimer": 5,
    # "benchmarkType": "speed",
    # "color": "5D5D5D",
    # "isCpuOnly": false,
    # "isSmall": false,
    # "skip": 0,
    # "crackerVersionId": 2,
    # "files": [
    # 1,
    # 2
    # ],
    # "priority": 100,
    # "maxAgents": 4,
    # "preprocessorId": 0,
    # "preprocessorCommand": "",
    # "accessKey": "mykey"
    # }
    # {
    # "section": "task",
    # "request": "createTask",
    # "name": "API Task BF",
    # "hashlistId": 1,
    # "attackCmd": "#HL# -a 3 ?l?l?l?l?l?l",
    # "chunksize": 600,
    # "statusTimer": 5,
    # "benchmarkType": "speed",
    # 12
    # "color": "5D5D5D",
    # "isCpuOnly": false,
    # "isSmall": true,
    # "skip": 0,
    # "crackerVersionId": 2,
    # "files": [],
    # "priority": 99,
    # "maxAgents": 4,
    # "preprocessorId": 0,
    # "preprocessorCommand": "",
    # "accessKey": "mykey"
    # }
    # {
    # "section": "task",
    # "request": "createTask",
    # "response": "OK",
    # "taskId": 101
    # }
    # prince_cmd = "google-10000-english-usa_firstUp+SpaceAtEnd.txt --pw-min=5 --elem-cnt-min=2 --elem-cnt-max=6 -s %s" % hashlistId
    prince_cmd = 'google-10000-english-usa_firstUp+SpaceAtEnd.txt --elem-cnt-min=3 --elem-cnt-max=3 --pw-min=8'
    task_name = "%s_PrinceTask" % hashlistId
    request_json_data = {
    "section": "task",
    "request": "createTask",
    "name": task_name,
    "hashlistId": hashlistId,
    "attackCmd": '-a0 #HL# -j "%3  Dp" -r passphrase-rule1_v2.rule -r Fordyv3.rule',
    "chunksize": 1200,
    "statusTimer": 30,
    "benchmarkType": "runtime",
    "color": "5D5D5D",
    "isCpuOnly": 0,
    "isSmall": 1,
    "skip": 0,
    "crackerBinaryTypeId": 1,
    "crackerVersionId": 4,
    "files": [ 346, 347, 314 ],
    "priority": 0,
    "maxAgents": 1,
    "usePreprocessor": 1,
    "preprocessorId": 1,
    "preprocessorCommand": prince_cmd,
    "skipKeyspace": 0,
    "enforcePipe": 1,
    "accessKey": accesskey
    }
    return submit_request(htserver, request_json_data)

def create_prince_task_names(htserver, accesskey, hashlistId):
    name = "PrinceNames-%s" % hashlistId
    requests_json_data = {
    "section": "task",
    "request": "createTask",
    "name": name,
    "attack": "-a0 #HL# -r Fordyv3.rule",
    "chunksize": 1200,
    "color": "3DD2FF",
    "benchmarkType": "speed",
    "statusTimer": 30,
    "priority": 0,
    "maxAgents": 1,
    "isCpuOnly": 'false',
    "isSmall": 'true',
    "isArchived": 'true',
    "skipKeyspace": 0,
    "hashlistId": hashlistId,
    "usePreprocessor": 'true',
    "preprocessorId": 1,
    "preprocessorCommand": "Names_v1.txt --elem-cnt-min=2 --elem-cnt-max=2 --pw-min=8 --pw-max=20 --save-pos-disable",
    "files": [
        {
            "fileId": 271,
            "filename": "Names_v1.txt",
            "size": 2278105
        },
        {
            "fileId": 346,
            "filename": "Fordyv3.rule",
            "size": 3489890
        }
    ],
}

def create_task(htserver, accesskey, tastname, hashlistId, attackCmd, crackerVersionId,
                files, isCpuOnly=1, isSmall=1, priority=0, maxAgents=0, chunksize=0, staticChunking=0,
                benchmarkType=0, preprocessorId='', preprocessorCommand='', color='5D5D5D'):
    # createTask
    # Create a new task (one example with files and one without).
    # {
    # "section": "task",
    # "request": "createTask",
    # "name": "API Task",
    # "hashlistId": 1,
    # "attackCmd": "#HL# -a 0 -r dive.rule example.dict",
    # "chunksize": 600,
    # "statusTimer": 5,
    # "benchmarkType": "speed",
    # "color": "5D5D5D",
    # "isCpuOnly": false,
    # "isSmall": false,
    # "skip": 0,
    # "crackerVersionId": 2,
    # "files": [
    # 1,
    # 2
    # ],
    # "priority": 100,
    # "maxAgents": 4,
    # "preprocessorId": 0,
    # "preprocessorCommand": "",
    # "accessKey": "mykey"
    # }
    # {
    # "section": "task",
    # "request": "createTask",
    # "name": "API Task BF",
    # "hashlistId": 1,
    # "attackCmd": "#HL# -a 3 ?l?l?l?l?l?l",
    # "chunksize": 600,
    # "statusTimer": 5,
    # "benchmarkType": "speed",
    # "color": "5D5D5D",
    # "isCpuOnly": false,
    # "isSmall": true,
    # "skip": 0,
    # "crackerVersionId": 2,
    # "files": [],
    # "priority": 99,
    # "maxAgents": 4,
    # "preprocessorId": 0,
    # "preprocessorCommand": "",
    # "accessKey": "mykey"
    # }
    # {
    # "section": "task",
    # "request": "createTask",
    # "response": "OK",
    # "taskId": 101
    # }

    setChunk = True
    # If chunkSize is zero, get the default value from the server.
    if chunksize == 0:
        chunksize = get_server_config(htserver, accesskey, 'chunktime')
        # "staticChunking"
        # 0 = No - Use Dynamic
        # 1 = Fixed chunk size
        # 2 = Fixed number of chunks
        staticChunking = 0
        setChunk = False

    if setChunk:
        # Confirm chunkSize is an integer.
        chunksize = int(chunksize)
        # Confirm staticChunking is an integer and is a value of 1 or 2.
        staticChunking = int(staticChunking)
        if staticChunking != 1 and staticChunking != 2:
            staticChunking = 0

    statusTimer = get_server_config(htserver, accesskey, 'statustimer')
    if benchmarkType == 1:
        benchmarkType = 'runtime'
    else:
        benchmarkType = 'speed'

    if isCpuOnly == 2:
        isCpuOnly = True
    else:
        isCpuOnly = False

    if isSmall == 2:
        isSmall = True
    else:
        isSmall = False

    if color == str("null") or color == '' or color == 'null' or color == 'None' or color == None or color == 'none':
        color = '5D5D5D'

    request_json_data = {
    "section": "task",
    "request": "createTask",
    "name": tastname,
    "hashlistId": int(hashlistId),
    "attackCmd": attackCmd,
    "chunksize": chunksize,
    "staticChunking": staticChunking,
    "statusTimer": statusTimer,
    "benchmarkType": benchmarkType,
    "color": color,
    "isCpuOnly": isCpuOnly,
    "isSmall": isSmall,
    "skip": 0,
    "crackerVersionId": crackerVersionId,
    "files": files,
    "priority": priority,
    "maxAgents": maxAgents,
    "preprocessorId": preprocessorId,
    "preprocessorCommand": preprocessorCommand,
    "accessKey": accesskey
    }
    print(json.dumps(request_json_data, indent=4))
    return submit_request(htserver, request_json_data)

def create_superhashlist(htserver, accesskey, hashlistIds, name):
    # createSuperhashlist
    # Create a new superhashlist out of existing hashlists.
    # {
    # "section": "superhashlist",
    # "request": "createSuperhashlist",
    # "name": "New Superhashlist",
    # "hashlists": [
    # 1,
    # 2
    # ],
    # "accessKey": "mykey"
    # }
    # {
    # "section": "superhashlist",
    # "request": "createSuperhashlist",
    # "response": "OK"
    # }
    request_json_data = {
    "section": "superhashlist",
    "request": "createSuperhashlist",
    "name": name,
    "hashlists": hashlistIds,
    "accessKey": accesskey
    }
    return submit_request(htserver, request_json_data)

def start_supertask(htserver, accessKey, supertaskId, hashlistId, crackerVersionId):
    # runSupertask
    # Create a supertask out of a configured preconfigured task collection.
    # {
    # "section": "task",
    # "request": "runSupertask",
    # "hashlistId": 1,
    # "supertaskId": 1,
    # "crackerVersionId": 2,
    # "accessKey": "mykey"
    # }
    # {
    # "section": "task",
    # "request": "runSupertask",
    # "response": "OK"
    # }
    request_json_data = {
    "section": "task",
    "request": "runSupertask",
    "hashlistId": hashlistId,
    "supertaskId": supertaskId,
    "crackerVersionId": crackerVersionId,
    "accessKey": accessKey
    }
    return submit_request(htserver, request_json_data)

def get_server_config(htserver, accessKey, configItem):
    # getConfig
    # Get the type and specific value of a config item. The following config types exist:
    # string basically everything is accepted as string
    # email similar to string, except that it’s tested if it is a valid email
    # number all kind of numeric value
    # checkbox boolean value (true or false)
    # {
    # "section": "config",
    # "request": "getConfig",
    # "configItem": "hashlistAlias",
    # "accessKey": "mykey"
    # }
    # {
    # "section": "config",
    # "request": "getConfig",
    # "response": "OK",
    # "item": "hashlistAlias",
    # "configType": "string",
    # "value": "#HL#"
    # }
    request_json_data = {
    "section": "config",
    "request": "getConfig",
    "configItem": configItem,
    "accessKey": accessKey
    }
    config = submit_request(htserver, request_json_data)
    # If config is not empty, return the value of the config item.
    if config:
        return config['value']

def get_cracker_version(htserver, accessKey):
    # getCracker
    # Get detailed informations of cracker, especially all available versions.
    # {
    # "section": "cracker",
    # "request": "getCracker",
    # "crackerTypeId": 1,
    # "accessKey": "mykey"
    # }
    # {
    # "section": "cracker",
    # "request": "getCracker",
    # "response": "OK",
    # "crackerTypeId": 1,
    # "crackerTypeName": "hashcat",
    # "crackerVersions": [
    # {
    # "versionId": 1,
    # "version": "4.1.0",
    # "downloadUrl": "https:\/\/hashcat.net\/files\/hashcat-4.1.0.7z",
    # "binaryBasename": "hashcat"
    # },
    # {
    # "versionId": 3,
    # "version": "4.1.1",
    # "downloadUrl": "https:\/\/hashcat.net\/beta\/hashcat-4.1.1-15.7z",
    # "binaryBasename": "hashcat"
    # }
    # ]
    # }
    request_json_data = {
    "section": "cracker",
    "request": "getCracker",
    "crackerTypeId": 1,
    "accessKey": accessKey
    }
    return submit_request(htserver, request_json_data)

def get_active_hashlists(htserver, accessKey):
    # listsHashlists
    # List all hashlists (excluding superhashlists);
    # {
    # "section": "hashlist",
    # "request": "listHashlists",
    # "accessKey": "mykey"
    # }
    # {
    # "section": "hashlist",
    # "request": "listHashlists",
    # "response": "OK",
    # "hashlists": [
    # {
    # "hashlistId": 1,
    # "hashtypeId": 0,
    # "name": "Hashcat Example",
    # "format": 0,
    # "hashCount": 6494
    # },
    # {
    # "hashlistId": 3,
    # "hashtypeId": 14800,
    # "name": "iTunes test for splitting",
    # "format": 0,
    # "hashCount": 1
    # },
    # {
    # "hashlistId": 4,
    # "hashtypeId": 6242,
    # "name": "truecrypt test",
    # "format": 2,
    # "hashCount": 1
    # }
    # ]
    # }
    #     "isArchived": "true",

    # Get all existing Hashlists that start with the name 'HashMaster_*'.
    request_json_data = {
    "section": "hashlist",
    "request": "listHashlists",
    "accessKey": accessKey,
    }
    return submit_request(htserver, request_json_data)

def get_archived_hashlists(htserver, accessKey):
    request_json_data = {
    "section": "hashlist",
    "request": "listHashlists",
    "accessKey": accessKey,
    "isArchived": "true"
    }
    return submit_request(htserver, request_json_data)

def get_all_hashlists(htserver, accessKey):
    # This function will return all active and archived hashlists.
    hashlists = get_active_hashlists(htserver, accessKey)
    archived_hashlists = get_archived_hashlists(htserver, accessKey)
    if archived_hashlists:
        # Add all values from the archived_hashlists "hashlists" to the hashlists "hashlists".
        hashlists['hashlists'] += archived_hashlists['hashlists']
    return hashlists

def get_a_file(htserver, accessKey, fileId):
    # getFile
    # Get detailed informations of a file and also get a link to download it.
    # {
    # "section": "file",
    # 37
    # "request": "getFile",
    # "fileId": 1,
    # "accessKey": "mykey"
    # }
    # {
    # "section": "file",
    # "request": "getFile",
    # "response": "OK",
    # "fileId": 1,
    # "fileType": 0,
    # "filename": "example.dict",
    # "isSecret": true,
    # "size": 1080240,
    # "url": "getFile.php?file=1&apiKey=mykey"
    # }
    request_json_data = {
    "section": "file",
    "request": "getFile",
    "fileId": fileId,
    "accessKey": accessKey
    }
    file_data = submit_request(htserver, request_json_data)
    # Use the returned URL to get just the contents of the file and store it in a variable.
    file_url = htserver + '/' + file_data['url']
    try:
        request = requests.get(file_url)
    except requests.exceptions.ConnectionError as error_code:
        print('Failed to connect to the Hashtopolis server. Error: %s' % error_code)
        return
    if request.status_code == 200:
        return request.text
    if request.status_code != 200:
        print('Error: %s' % request.text)

def get_cracked_hashes(htserver, accesskey, hashlistId):
    # getCracked
    # Retrieve all cracked hashes of a given hashlist.
    # {
    # "section": "hashlist",
    # "request": "getCracked",
    # "hashlistId": "1",
    # "accessKey": "mykey"
    # }
    # {
    # "section": "hashlist",
    # "request": "getCracked",
    # "response": "OK",
    # "cracked": [
    # {
    # "hash": "098f6bcd4621d373cade4e832627b4f6",
    # "plain": "test",
    # "crackpos": "634721"
    # },
    # {
    # "hash": "5f4dcc3b5aa765d61d8327deb882cf99",
    # "plain": "password",
    # "crackpos": "608529"
    # }
    # ]
    # }
    request_json_data = {
    "section": "hashlist",
    "request": "getCracked",
    "hashlistId": hashlistId,
    "accessKey": accesskey
    }
    return submit_request(htserver, request_json_data)

def get_task(htserver, accesskey, taskId):
    # getTask
    # Get the details for a specific task. Note that this request can only be done with tasks or subtasks, but not with supertasks.
    # {
    # "section": "task",
    # "request": "getTask",
    # "taskId": 7587,
    # "accessKey": "mykey"
    # }
    # {
    # "section": "task",
    # "request": "getTask",
    # "response": "OK",
    # "taskId": 7587,
    # "name": "testing",
    # "attack": "#HL# -a 0 top10000.txt -r dive.rule",
    # "chunksize": 600,
    # "color": null,
    # "benchmarkType": "speed",
    # "statusTimer": 5,
    # "priority": 0,
    # "maxAgents": 4,
    # "isCpuOnly": false,
    # "isSmall": false,
    # "skipKeyspace": 0,
    # "keyspace": 10000,
    # "dispatched": 10000,
    # "hashlistId": 1,
    # "imageUrl": "http:\/\/localhost\/hashtopolis\/src\/api\/taskimg.php?task=7587",
    # "files": [
    # {
    # "fileId": 2,
    # "filename": "dive.rule",
    # "size": 887155
    # },
    # {
    # "fileId": 3653,
    # "filename": "top10000.txt",
    # "size": 76508
    # }
    # ],
    # "speed": 0,
    # "searched": 10000,
    # "chunkIds": [
    # 31
    # ],
    # "agents": [
    # {
    # "agentId": 2,
    # "benchmark": "0",
    # "speed": 0
    # }
    # ],
    # "isComplete": false,
    # "usePreprocessor": false,
    # "preprocessorId": 0,
    # "preprocessorCommand": ""
    # }
    request_json_data = {
    "section": "task",
    "request": "getTask",
    "taskId": taskId,
    "accessKey": accesskey
    }
    return submit_request(htserver, request_json_data)

def get_task_details(htserver, accesskey, taskid):
    # getTask
    # Get the details for a specific task. Note that this request can only be done with tasks or subtasks, but not with supertasks.
    # {
    # "section": "task",
    # "request": "getTask",
    # "taskId": 7587,
    # "accessKey": "mykey"
    # }
    # {
    # "section": "task",
    # "request": "getTask",
    # "response": "OK",
    # "taskId": 7587,
    # "name": "testing",
    # "attack": "#HL# -a 0 top10000.txt -r dive.rule",
    # "chunksize": 600,
    # "color": null,
    # "benchmarkType": "speed",
    # "statusTimer": 5,
    # "priority": 0,
    # "maxAgents": 4,
    # "isCpuOnly": false,
    # "isSmall": false,
    # "skipKeyspace": 0,
    # "keyspace": 10000,
    # "dispatched": 10000,
    # "hashlistId": 1,
    # "imageUrl": "http:\/\/localhost\/hashtopolis\/src\/api\/taskimg.php?task=7587",
    # "files": [
    # {
    # "fileId": 2,
    # "filename": "dive.rule",
    # "size": 887155
    # },
    # {
    # "fileId": 3653,
    # "filename": "top10000.txt",
    # "size": 76508
    # }
    # ],
    # "speed": 0,
    # "searched": 10000,
    # "chunkIds": [
    # 31
    # ],
    # "agents": [
    # {
    # "agentId": 2,
    # "benchmark": "0",
    # "speed": 0
    # }
    # ],
    # "isComplete": false,
    # "usePreprocessor": false,
    # 10
    # "preprocessorId": 0,
    # "preprocessorCommand": ""
    # }
    request_json_data = {
    "section": "task",
    "request": "getTask",
    "taskId": taskid,
    "accessKey": accesskey
    }
    return submit_request(htserver, request_json_data)

def get_all_tasks(htserver, accesskey):
    # listTasks
    # List all tasks on the server. There are two task types:
    # 0 Normal Task
    # 1 Supertask
    # In case it is set in the server configuration, for normal tasks there will be a flag ’isComplete’ be set which denotes if the full
    # keyspace of the task was covered. For tasks, the task Id is returned, for supertasks the taskwrapper Id is returned.
    # {
    # "section": "task",
    # "request": "listTasks",
    # "accessKey": "mykey"
    # }
    # {
    # "section": "task",
    # "request": "listTasks",
    # "response": "OK",
    # "tasks": [
    # {
    # "taskId": 7587,
    # "name": "test 2",
    # "type": 0,
    # "hashlistId": 1,
    # "priority": 5
    # },
    # {
    # "supertaskId": 33,
    # "name": "Increment ?a",
    # "type": 1,
    # "hashlistId": 1,
    # "priority": 3
    # },
    # {
    # "supertaskId": 32,
    # "name": "Supertask Test",
    # "type": 1,
    # "hashlistId": 1,
    # "priority": 0
    # },
    # {
    # "taskId": 7580,
    # "name": "test 1",
    # "type": 0,
    # "hashlistId": 1,
    # "priority": 0
    # }
    # ]
    # }
    request_json_data = {
    "section": "task",
    "request": "listTasks",
    "accessKey": accesskey
    }
    return submit_request(htserver, request_json_data)

def get_all_superhashlists(htserver, accesskey):
    # listSuperhashlists
    # List all superhashlists on the server.
    # {
    # "section": "superhashlist",
    # "request": "listSuperhashlists",
    # "accessKey": "mykey"
    # }
    # {
    # "section": "superhashlist",
    # "request": "listSuperhashlists",
    # "response": "OK",
    # "superhashlists": [
    # {
    # "hashlistId": 2,
    # "hashtypeId": 0,
    # "name": "Test superhashlist",
    # "hashCount": 6494
    # }
    # ]
    # }
    request_json_data = {
    "section": "superhashlist",
    "request": "listSuperhashlists",
    "accessKey": accesskey
    }
    return submit_request(htserver, request_json_data)

def get_preconfigured_supertasks(htserver, accesskey, supertaskId):
    # getSupertask
    # Get detail information of a supertask.
    # {
    # "section": "supertask",
    # "request": "getSupertask",
    # "supertaskId": 2,
    # "accessKey": "mykey"
    # }
    # {
    # "section": "supertask",
    # "request": "getSupertask",
    # "response": "OK",
    # "supertaskId": 2,
    # "name": "Increment ?a",
    # "pretasks": [
    # {
    # "pretaskId": 2,
    # "name": "?a?a?a",
    # "priority": 6
    # },
    # {
    # "pretaskId": 3,
    # "name": "?a?a?a?a",
    # "priority": 5
    # },
    # {
    # "pretaskId": 4,
    # "name": "?a?a?a?a?a",
    # "priority": 4
    # },
    # {
    # "pretaskId": 5,
    # "name": "?a?a?a?a?a?a",
    # "priority": 3
    # },
    # {
    # "pretaskId": 6,
    # "name": "?a?a?a?a?a?a?a",
    # "priority": 2
    # },
    # {
    # "pretaskId": 1,
    # "name": "Test Pre",
    # "priority": 0
    # }
    # ]
    # }
    request_json_data = {
    "section": "supertask",
    "request": "getSupertask",
    "supertaskId": supertaskId,
    "accessKey": accesskey
    }
    request = submit_request(htserver, request_json_data)
    print(json.dumps(request, indent=4))

def get_all_known_plaintext_passwords(htserver, accesskey):
    # Get all known hashlists.
    hashlists = get_all_hashlists(htserver, accesskey)

    # Foreach hashlist, use the get_cracked_hashes function to get the cracked hashes for each hashlist and
    # store the plaintext passwords in a list.
    plaintext_passwords = []
    for hashlist in hashlists['hashlists']:
        cracked_hashes = get_cracked_hashes(htserver, accesskey, hashlist['hashlistId'])
        for hash in cracked_hashes['cracked']:
            plaintext_passwords.append(hash['plain'])

    # Sort and remove duplicates from the list of plaintext passwords.
    plaintext_passwords = sorted(list(set(plaintext_passwords)))

    # Remove any empty strings from the list of plaintext passwords.
    plaintext_passwords = [x for x in plaintext_passwords if x]

    return plaintext_passwords

def get_agent_settings(htserver, accesskey, agentId):
    # get
    # Retrieve all the informations about a specific agent by providing its ID. The last action time is a UNIX timestamp and if the
    # configuration on the server is set to hide the IP of the agents, the value will just be Hidden instead of the IP.
    # {
    # "section": "agent",
    # "request": "get",
    # "agentId": 2,
    # "accessKey": "mykey"
    # }
    # {
    # "section": "agent",
    # "request": "get",
    # "response": "OK",
    # "name": "cracker1",
    # "devices": [
    # "Intel(R) Core(TM) i7-3770 CPU @ 3.40GHz",
    # "NVIDIA Quadro 600"
    # ],
    # "owner": {
    # "userId": 1,
    # "username": "htp"
    # },
    # "isCpuOnly": false,
    # "isTrusted": true,
    # "isActive": true,
    # "token": "0lBfAp7YQh",
    # "extraParameters": "--force",
    # "errorFlag": 2,
    # "lastActivity": {
    # "action": "getTask",
    # "time": 1531316240,
    # "ip": "127.0.0.1"
    # }
    # }
    request_json_data = {
    "section": "agent",
    "request": "get",
    "agentId": agentId,
    "accessKey": accesskey
    }
    return submit_request(htserver, request_json_data)

def list_all_files(htserver, accesskey):
    # listFiles
    # List all available files.
    # {
    # "section": "file",
    # "request": "listFiles",
    # "accessKey": "mykey"
    # }
    # {
    # "section": "file",
    # "request": "listFiles",
    # "response": "OK",
    # "files": [
    # {
    # "fileId": 1,
    # "fileType": 0,
    # "filename": "example.dict"
    # },
    # {
    # "fileId": 2,
    # "fileType": 1,
    # "filename": "dive.rule"
    # },
    # {
    # "fileId": 3,
    # "fileType": 1,
    # "filename": "generated.rule"
    # },
    # {
    # "fileId": 3653,
    # "fileType": 0,
    # "filename": "top10000.txt"
    # },
    # {
    # "fileId": 3654,
    # "fileType": 1,
    # "filename": "toggles4.rule"
    # }
    # ]
    # }
    request_json_data = {
    "section": "file",
    "request": "listFiles",
    "accessKey": accesskey
    }
    return submit_request(htserver, request_json_data)

def list_all_preconfigured_supertasks(htserver, accesskey):
    # listSupertasks
    # Lists the available supertasks on the server which group preconfigured tasks together.
    # {
    # "section": "supertask",
    # "request": "listSupertasks",
    # "accessKey": "mykey"
    # }
    # {
    # "section": "supertask",
    # "request": "listSupertasks",
    # "response": "OK",
    # "supertasks": [
    # {
    # "supertaskId": 1,
    # "name": "Supertask Test"
    # },
    # {
    # "supertaskId": 2,
    # "name": "Increment ?a"
    # }
    # ]
    # }
    request_json_data = {
    "section": "supertask",
    "request": "listSupertasks",
    "accessKey": accesskey
    }
    return submit_request(htserver, request_json_data)

def list_supertask_subtasks(htserver, accesskey, supertaskId):
    # listSubtasks
    # List all subtasks of a given running supertask.
    # {
    # "section": "task",
    # "request": "listSubtasks",
    # "supertaskId": 33,
    # "accessKey": "mykey"
    # }
    # {
    # "section": "task",
    # "request": "listSubtasks",
    # "response": "OK",
    # "subtasks": [
    # {
    # "taskId": 7582,
    # "name": "?a?a?a",
    # "priority": 0
    # },
    # {
    # "taskId": 7583,
    # "name": "?a?a?a?a",
    # "priority": 0
    # },
    # {
    # "taskId": 7584,
    # "name": "?a?a?a?a?a",
    # "priority": 0
    # },
    # {
    # "taskId": 7585,
    # "name": "?a?a?a?a?a?a",
    # "priority": 0
    # }
    # ]
    # }
    request_json_data = {
    "section": "task",
    "request": "listSubtasks",
    "supertaskId": supertaskId,
    "accessKey": accesskey
    }
    return submit_request(htserver, request_json_data)

def list_server_config(htserver, accessKey):
    # listConfig
    # List all currently known config values.
    # {
    # "section": "config",
    # "request": "listConfig",
    # "accessKey": "mykey"
    # }
    # {
    # "section": "config",
    # "request": "listConfig",
    # "response": "OK",
    # 44
    # "items": [
    # {
    # "item": "agenttimeout",
    # "configSectionId": "1",
    # "itemDescription": "Time in seconds the server will consider a client inactive or timed out."
    # },
    # ...
    # ...
    # {
    # "item": "benchtime",
    # "configSectionId": "1",
    # "itemDescription": "Time in seconds an agent should benchmark a task"
    # }
    # ]
    # }
    request_json_data = {
    "section": "config",
    "request": "listConfig",
    "accessKey": accessKey
    }
    return submit_request(htserver, request_json_data)

def list_all_agents(htserver, accesskey):
    # listAgents
    # List all agents with some basic informations.
    # {
    # "section": "agent",
    # "request": "listAgents",
    # "accessKey": "mykey"
    # }
    # {
    # "section": "agent",
    # "request": "listAgents",
    # "response": "OK",
    # "agents": [
    # {
    # "agentId": "2",
    # "name": "cracker1",
    # "devices": [
    # "Intel(R) Core(TM) i7-3770 CPU @ 3.40GHz",
    # "NVIDIA Quadro 600"
    # ]
    # }
    # ]
    # }
    request_json_data = {
    "section": "agent",
    "request": "listAgents",
    "accessKey": accesskey
    }
    return submit_request(htserver, request_json_data)

def set_agent_extra_param(htserver, accesskey, agentId, value):
    # setExtraParams
    # Set agent specific command line parameters for the agent which are included in the cracker command line call on the agent.
    # {
    # "section": "agent",
    # "request": "setExtraParams",
    # "extraParameters": "-d 1,2",
    # "agentId": 2,
    # "accessKey": "mykey"
    # }
    # {
    # "section": "agent",
    # "request": "setExtraParams",
    # "response": "OK"
    # }
    request_json_data = {
    "section": "agent",
    "request": "setExtraParams",
    "extraParameters": value,
    "agentId": agentId,
    "accessKey": accesskey
    }
    return submit_request(htserver, request_json_data)

def set_agent_active(htserver, accesskey, agentId, state):
    #     setActive
    # Set an agent active/inactive.
    # {
    # "section": "agent",
    # "request": "setActive",
    # "active": false,
    # "agentId": 2,
    # "accessKey": "mykey"
    # }
    # {
    # "section": "agent",
    # "request": "setActive",
    # "response": "OK"
    # }
    request_json_data = {
    "section": "agent",
    "request": "setActive",
    "active": state,
    "agentId": agentId,
    "accessKey": accesskey
    }
    return submit_request(htserver, request_json_data)

def set_all_file_not_secret(htserver, accesskey):
    # setSecret
    # Set if an existing file is secret or not.
    # {
    # "section": "file",
    # "request": "setSecret",
    # "fileId": 1,
    # "isSecret": false,
    # "accessKey": "mykey"
    # }
    # {
    # "section": "file",
    # "request": "setSecret",
    # "response": "OK"
    # }
    # Get all file IDs.
    files = list_all_files(htserver, accesskey)
    for file in files['files']:
        request_json_data = {
        "section": "file",
        "request": "setSecret",
        "fileId": file['fileId'],
        "isSecret": False,
        "accessKey": accesskey
        }
        submit_request(htserver, request_json_data)

def set_preconfig_task_as_cpu_only(htserver, accesskey, pretaskId, state):
    # setPretaskCpuOnly
    # Set if a preconfigured task is a CPU only task or not.
    # {
    # "section": "pretask",
    # "request": "setPretaskCpuOnly",
    # "pretaskId": 1,
    # "isCpuOnly": true,
    # "accessKey": "mykey"
    # }
    # {
    # "section": "pretask",
    # "request": "setPretaskCpuOnly",
    # "response": "OK"
    # }
    request_json_data = {
    "section": "pretask",
    "request": "setPretaskCpuOnly",
    "pretaskId": pretaskId,
    "isCpuOnly": state,
    "accessKey": accesskey
    }
    return submit_request(htserver, request_json_data)

def set_task_as_cpu_only(htserver, accesskey, taskId, state):
    # setTaskCpuOnly
    # Set if a task is a CPU only task or not.
    # {
    # "section": "task",
    # "request": "setTaskCpuOnly",
    # "taskId": 7580,
    # "isCpuOnly": false,
    # "accessKey": "mykey"
    # }
    # {
    # "section": "task",
    # "request": "setTaskCpuOnly",
    # "response": "OK"
    # }
    # Confirm state is a boolean value.
    if state == 'true':
        state = True
    else:
        state = False

    request_json_data = {
    "section": "task",
    "request": "setTaskCpuOnly",
    "taskId": taskId,
    "isCpuOnly": state,
    "accessKey": accesskey
    }
    return submit_request(htserver, request_json_data)

def archive_supertask(htserver, accesskey, supertaskId):
    # archiveSupertask
    # Archive a supertask (including all subtasks).
    # {
    # "section": "task",
    # "request": "archiveSupertask",
    # "supertaskId": 54,
    # "accessKey": "mykey"
    # }
    # {
    # "section": "task",
    # "request": "archiveSupertask",
    # "response": "OK"
    # }
    request_json_data = {
    "section": "task",
    "request": "archiveSupertask",
    "supertaskId": supertaskId,
    "accessKey": accesskey
    }
    return submit_request(htserver, request_json_data)

def import_precracked_hashes(htserver, accesskey, hashlistId, filename):
    import_precracked_hashes_process_file_in_memory(htserver, accesskey, hashlistId, filename, chunk_size_mb=10)

def import_precracked_hashes_process_chunk(htserver, accesskey, hashlistId, lines):
    # importCracked
    # Add some cracked hashes from an external source for this hashlist. The data must be base64 (using UTF-8) encoded.
    # {
    # "section": "hashlist",
    # "request": "importCracked",
    # "hashlistId": 5,
    # "separator": ":",
    # "data": "JDJ5JDEyJDcwMElMNlZ4TGwyLkEvS2NISmJEYmVKMGFhcWVxYUdrcHhlc0FFZC5jWFBQUU4vWjNVN1c2OnRlc3Q=",
    # "accessKey": "mykey"
    # }
    # {
    # "section": "hashlist",
    # "request": "importCracked",
    # "response": "OK",
    # "linesProcessed": 1,
    # "newCracked": 1,
    # "alreadyCracked": 0,
    # "invalidLines": 0,
    # "notFound": 0,
    # "processTime": 0,
    # "tooLongPlains": 0
    # }
    """
    Sends a chunk of lines to the server via the API.

    Args:
        lines (list): List of lines to send as a chunk.
    """
    data_lines = ''.join(lines)
    data_lines = base64.b64encode(data_lines.encode()).decode()
    request_json_data = {
    "section": "hashlist",
    "request": "importCracked",
    "hashlistId": hashlistId,
    "separator": ":",
    "data": data_lines,
    "accessKey": accesskey
    }
    return submit_request(htserver, request_json_data)

def import_precracked_hashes_process_file_in_memory(htserver, accesskey, hashlistId, file_path, chunk_size_mb):
    """
    Processes a large text file in memory, sending 100 MB chunks to an API
    without creating intermediate files.

    Args:
        file_path (str): Path to the large text file.
        chunk_size_mb (int): Size of each chunk in MB.
    """
    print('Processing file: %s' % file_path)
    chunk_size_bytes = chunk_size_mb * 1024 * 1024
    current_chunk_size = 0
    chunk_lines = []
    new_cracked = 0
    lines_processed = 0
    already_cracked = 0
    invalid_lines = 0
    not_found = 0
    too_long_plains = 0
    chunk_prcess_seconds_time = 60
    # Get the size of the file in bytes
    file_size = os.path.getsize(file_path)
    # Divide the file size by the chunk size to get the number of chunks
    number_of_chunks = file_size / chunk_size_bytes
    total_process_time = number_of_chunks * chunk_prcess_seconds_time
    if total_process_time > 60 and total_process_time < 3600:
        total_process_time = total_process_time / 60
        print('Total Process Time: %d minutes' % total_process_time)
    if total_process_time > 3600:
        total_process_time = total_process_time / 3600
        print('Total Process Time: %d hours' % total_process_time)

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line_size = len(line.encode('utf-8'))
            if current_chunk_size + line_size > chunk_size_bytes and chunk_lines:
                # Process the current chunk
                returned_data = import_precracked_hashes_process_chunk(htserver, accesskey, hashlistId, chunk_lines)
                # Example Return Data
                # {'section': 'hashlist', 'request': 'importCracked', 'response': 'OK', 'linesProcessed': 234564, 'newCracked': 0, 'alreadyCracked': 1, 'invalidLines': 0, 'notFound': 234563, 'processTime': 60, 'tooLongPlains': 0}
                # Take the data with numbers and ADD them to a new running value to keep track of the progress.
                new_cracked += returned_data['newCracked']
                lines_processed += returned_data['linesProcessed']
                already_cracked += returned_data['alreadyCracked']
                invalid_lines += returned_data['invalidLines']
                not_found += returned_data['notFound']
                too_long_plains += returned_data['tooLongPlains']
                chunk_prcess_seconds_time = returned_data['processTime']
                total_process_time = number_of_chunks * chunk_prcess_seconds_time
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if total_process_time > 60 and total_process_time < 3600:
                    # Convert seconds to minutes and round to 2 decimal places.
                    total_process_time = total_process_time / 60
                    # round total_process_time to 2 decimal places.
                    total_process_time = round(total_process_time, 2)
                    print('%s ::: ChunksRemaining: %s - TimeRemaining: %s minutes - ProcessTime: %d - NewCracks: %s - AlreadyCracked: %s - LinesProcessed: %s - InvalidLines: %s - NotFound: %s - TooLongPlains: %s' % (timestamp, round(number_of_chunks), total_process_time, chunk_prcess_seconds_time, new_cracked, already_cracked, lines_processed, invalid_lines, not_found, too_long_plains), flush=True,end="\r")
                if total_process_time > 3600:
                    total_process_time = total_process_time / 3600
                    total_process_time = round(total_process_time, 2)
                    print('%s ::: ChunksRemaining: %s - TimeRemaining: %s hours - ProcessTime: %d - NewCracks: %s - AlreadyCracked: %s - LinesProcessed: %s - InvalidLines: %s - NotFound: %s - TooLongPlains: %s' % (timestamp, round(number_of_chunks), total_process_time, chunk_prcess_seconds_time, new_cracked, already_cracked, lines_processed, invalid_lines, not_found, too_long_plains), flush=True,end="\r")
                # Minus 1 from number_of_chunks to keep track of the progress.
                number_of_chunks -= 1
                # Reset for the next chunk
                current_chunk_size = 0
                chunk_lines = []

            # Add the line to the current chunk
            chunk_lines.append(line)
            current_chunk_size += line_size

        # Process any remaining lines in the final chunk
        if chunk_lines:
            import_precracked_hashes_process_chunk(htserver, accesskey, hashlistId, chunk_lines)

def import_preconfigured_task(htserver, accesskey, cracker_version, hashlistId, file_path):
    # Open a text file containing preconfigured tasks in json format. Take the vaules and create the tasks using the create_task function.
    # Below is an example task exported from Hashtopolis.
    # {
    #     "section": "task",
    #     "request": "getTask",
    #     "response": "OK",
    #     "taskId": 6403,
    #     "name": "438_PrinceEuropean_lang",
    #     "attack": "-a0 #HL# -r Fordyv3.rule",
    #     "chunksize": 1200,
    #     "color": "5D5D5D",
    #     "benchmarkType": "speed",
    #     "statusTimer": 30,
    #     "priority": 0,
    #     "maxAgents": 1,
    #     "isCpuOnly": false,
    #     "isSmall": true,
    #     "isArchived": false,
    #     "skipKeyspace": 0,
    #     "keyspace": 8781803656627426,
    #     "dispatched": 8781803656627426,
    #     "hashlistId": 438,
    #     "imageUrl": "http://ht.tdcme.loc/api/taskimg.php?task=6403",
    #     "usePreprocessor": true,
    #     "preprocessorId": 1,
    #     "preprocessorCommand": "European_lang_v1.txt --elem-cnt-min=3 --elem-cnt-max=3 --pw-min=8",
    #     "files": [
    #         {
    #             "fileId": 291,
    #             "filename": "European_lang_v1.txt",
    #             "size": 24491788
    #         },
    #         {
    #             "fileId": 346,
    #             "filename": "Fordyv3.rule",
    #             "size": 3489890
    #         },
    #         {
    #             "fileId": 347,
    #             "filename": "passphrase-rule1_v2.rule",
    #             "size": 55
    #         }
    #     ],
    #     "speed": 3219289620,
    #     "searched": 0,
    #     "chunkIds": [
    #         15445
    #     ],
    #     "agents": [
    #         {
    #             "agentId": 11,
    #             "benchmark": "0",
    #             "speed": 3219289620
    #         }
    #     ],
    #     "isComplete": false,
    #     "workPossible": false
    # }
    # Open the file and read the contents.
    with open(file_path, 'r', encoding='utf-16') as file:
        data = file.read()
        task = json.loads(data)
        new_task_name = "%s_%s" % (str(hashlistId), str(task['name']))

        if str(task['benchmarkType']) == str('runtime'):
            benchmarkType = 1
        else:
            benchmarkType = 2

        if task['isCpuOnly'] == True or task['isCpuOnly'] == 'true':
            isCpuOnly = 2
        else:
            isCpuOnly = 1

        if task['isSmall'] == True or task['isSmall'] == 'true':
            isSmall = 2
        else:
            isSmall = 1

        #  Confirm task['staticChunking'] if staticChunking exists and is between 0 and 2.
        if 'staticChunking' not in task:
            task['staticChunking'] = 0

        if 'staticChunking' in task:
            if task['staticChunking'] == '':
                task['staticChunking'] = 0
            else:
                if int(task['staticChunking']) < 0 or int(task['staticChunking']) > 2:
                    task['staticChunking'] = 0

        # Take all the values in the task['files'] list and create a new list of file ids only.
        files = []
        for file in task['files']:
            files.append(file['fileId'])
        # create_task(htserver, accesskey, tastname, hashlistId, attackCmd, crackerVersionId,
        #         files, isCpuOnly=1, isSmall=1, priority=0, maxAgents=0, chunkSize=0, staticChunking=0,
        #         benchmarkType=0, preprocessorId='', preprocessorCommand='', color='5D5D5D'):
        create_task(htserver, accesskey, new_task_name, hashlistId, task['attack'], cracker_version,
                    files, isCpuOnly=isCpuOnly, isSmall=isSmall, priority=task['priority'], maxAgents=task['maxAgents'],
                    chunksize=task['chunksize'], staticChunking=task['staticChunking'],
                    benchmarkType=benchmarkType, preprocessorId=task['preprocessorId'],
                    preprocessorCommand=task['preprocessorCommand'], color=task['color'])

def export_left_hashes(htserver, accesskey, hashlistId):
    # exportLeft
    # Generates a left list with all hashes which are not cracked. The response returns informations about the created file. This only
    # works for plaintext hashlists!
    # {
    # "section": "hashlist",
    # "request": "exportLeft",
    # "hashlistId": 1,
    # "accessKey": "mykey"
    # }
    # {
    # "section": "hashlist",
    # "request": "exportLeft",
    # "response": "OK",
    # "fileId": 7569,
    # "filename": "Leftlist_1_19-07-2018_14-49-02.txt"
    # }
    request_json_data = {
    "section": "hashlist",
    "request": "exportLeft",
    "hashlistId": hashlistId,
    "accessKey": accesskey
    }
    return submit_request(htserver, request_json_data)

def delete_task(htserver, accesskey, taskId):
    # deleteTask
    # Completely delete a task.
    # {
    # "section": "task",
    # "request": "deleteTask",
    # "taskId": 7580,
    # "accessKey": "mykey"
    # }
    # {
    # "section": "task",
    # "request": "deleteTask",
    # "response": "OK"
    # }
    request_json_data = {
    "section": "task",
    "request": "deleteTask",
    "taskId": taskId,
    "accessKey": accesskey
    }
    return submit_request(htserver, request_json_data)

def delete_supertask(htserver, accesskey, supertaskId):
    # deleteSupertask
    # Delete a running supertask. This includes all contained subtasks.
    # {
    # "section": "task",
    # "request": "deleteSupertask",
    # "supertaskId": 43,
    # "accessKey": "mykey"
    # }
    # {
    # "section": "task",
    # "request": "deleteSupertask",
    # "response": "OK"
    # }
    request_json_data = {
    "section": "task",
    "request": "deleteSupertask",
    "supertaskId": supertaskId,
    "accessKey": accesskey
    }
    return submit_request(htserver, request_json_data)

def delete_preconfigured_task(htserver, accesskey, pretaskId):
    # deletePretask
    # Deletes a preconfigured task. This also includes removing it from supertasks if it is used there.
    # {
    # "section": "pretask",
    # "request": "deletePretask",
    # "pretaskId": 1,
    # "accessKey": "mykey"
    # }
    # {
    # "section": "pretask",
    # "request": "deletePretask",
    # "response": "OK"
    # }

    request_json_data = {
    "section": "pretask",
    "request": "deletePretask",
    "pretaskId": pretaskId,
    "accessKey": accesskey
    }
    return submit_request(htserver, request_json_data)

def delete_file(htserver, accesskey, fileId):
    # deleteFile
    # Deletes a file from the server. This is only possible if the file is not used in any task.
    # {
    # "section": "file",
    # "request": "deleteFile",
    # "fileId": 3654,
    # "accessKey": "mykey"
    # }
    # {
    # "section": "file",
    # "request": "deleteFile",
    # "response": "OK"
    # }
    request_json_data = {
    "section": "file",
    "request": "deleteFile",
    "fileId": fileId,
    "accessKey": accesskey
    }
    return submit_request(htserver, request_json_data)

def delete_superhashlist(htserver, accesskey, superhashlistId):
    # deleteSuperhashlist
    # Deletes a superhashlist. But the containing hashlists will not be removed.
    # {
    # "section": "superhashlist",
    # "request": "deleteSuperhashlist",
    # "superhashlistId": 6,
    # "accessKey": "mykey"
    # }
    # {
    # "section": "superhashlist",
    # "request": "deleteSuperhashlist",
    # "response": "OK"
    # }
    request_json_data = {
    "section": "superhashlist",
    "request": "deleteSuperhashlist",
    "superhashlistId": superhashlistId,
    "accessKey": accesskey
    }
    return submit_request(htserver, request_json_data)

def delete_hashlist(htserver, accesskey, hashlistId):
    # DeleteHashlist
    # Delete a hashlist and all according hashes. This will remove a hashlist from the superhashlists it is member of.
    # {
    # "section": "hashlist",
    # "request": "deleteHashlist",
    # "hashlistId": 5,
    # "accessKey": "mykey"
    # }
    # {
    # "section": "hashlist",
    # "request": "deleteHashlist",
    # "response": "OK"
    # }
    request_json_data = {
    "section": "hashlist",
    "request": "deleteHashlist",
    "hashlistId": hashlistId,
    "accessKey": accesskey
    }
    return submit_request(htserver, request_json_data)

def archive_task(htserver, accesskey, taskId):
    # archiveTask
    # Archive a task.
    # {
    # "section": "task",
    # "request": "archiveTask",
    # "taskId": 7601,
    # "accessKey": "mykey"
    # }
    # {
    # "section": "task",
    # "request": "archiveTask",
    # "response": "OK"
    # }
    request_json_data = {
    "section": "task",
    "request": "archiveTask",
    "taskId": taskId,
    "accessKey": accesskey
    }
    return submit_request(htserver, request_json_data)

def upload_file(htserver, accesskey, filename, filedata):
    # addFile
    # There are multiple ways to add a file, either from an URL, from the import directory or inline. The filename is only relevant if
    # it is added inline. Otherwise it will take the original filename. In case of the inline upload, the data must be base64 encoded
    # (using UTF-8).
    # {
    # "section": "file",
    # "request": "addFile",
    # "filename": "api_test_inline.txt",
    # "fileType": 0,
    # "source": "inline",
    # "accessGroupId": 1,
    # "data": "MTIzNA0KNTY3OA0KcGFzc3dvcmQNCmFiYw==",
    # "accessKey": "mykey"
    # }
    # {
    # "section": "file",
    # "request": "addFile",
    # "filename": "doesnt-matter.txt",
    # 39
    # "fileType": 0,
    # "source": "import",
    # "accessGroupId": 1,
    # "data": "otherlist.txt",
    # "accessKey": "mykey"
    # }
    # {
    # "section": "file",
    # "request": "addFile",
    # "filename": "doesnt-matter.txt",
    # "fileType": 1,
    # "source": "url",
    # "accessGroupId": 1,
    # "data": "https://github.com/hashcat/hashcat/raw/master/rules/best64.rule",
    # "accessKey": "mykey"
    # }
    # {
    # "section": "file",
    # "request": "addFile",
    # "response": "OK"
    # }
    # Encode the filedata to base64.
    filedata = base64.b64encode(filedata.encode()).decode()
    request_json_data = {
    "section": "file",
    "request": "addFile",
    "filename": filename,
    "fileType": 0,
    "source": "inline",
    "accessGroupId": 1,
    "data": filedata,
    "accessKey": accesskey
    }
    return submit_request(htserver, request_json_data)

def generate_wordlist_from_hashlist(htserver, accesskey, hashlistId):
    # generateWordlist
    # Generates a wordlist of all plaintexts of the cracked hashes of this hashlist. The response includes the informations about the
    # created file.
    # {
    # "section": "hashlist",
    # "request": "generateWordlist",
    # "hashlistId": 5,
    # "accessKey": "mykey"
    # }
    # {
    # "section": "hashlist",
    # "request": "generateWordlist",
    # "response": "OK",
    # "fileId": 7568,
    # "filename": "Wordlist_5_19.07.2018_14.47.20.txt"
    # }
    request_json_data = {
    "section": "hashlist",
    "request": "generateWordlist",
    "hashlistId": hashlistId,
    "accessKey": accesskey
    }
    return submit_request(htserver, request_json_data)
