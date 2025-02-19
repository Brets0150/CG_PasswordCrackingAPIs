#!/bin/env python3
import os
import json
import argparse
import inc.hashtopolis as hashtopolis
import inc.hashes_com as hashes_com
import inc.hashmob_net as hashmob_net
import inc.algorithms as algorithms

# Core HashMaster Functions

def load_config():
    # Check the directory this script is in for a file called "config.json" and read the contents of the file to get all the app settings and make then global variables.
    # Example config.json file:
    #     {
    #     "app_name": "HashMaster",
    #     "version": "1.0.0",
    #     "settings": {
    #         "debug_mode": true,
    #         "Hashtopolis": {
    #             "url": "http://10.100.100.200:80",
    #             "api_key": "abcd1234"
    #         },
    #         "hashes_com": {
    #             "api_key": "abcd1234",
    #             "url": "https://hashes.com"
    #         }
    #     }
    # }
    # Load the config file to get get all the settings and make them global variables. Check that config.json exists in the same directory as this script and contains no errors.
    try:
        global config
        # Get the full directory path of the script
        script_dir = os.path.dirname(os.path.realpath(__file__))
        os.chdir(script_dir)
        # The config file full path is the script directory path plus the file name "config.json"
        config_file = "%s/config.json" % (script_dir)
        ## print("Loading config file: %s" % (config_file))
        with open(config_file, "r") as f:
            config = json.load(f)
            return config
    except FileNotFoundError:
        print("Error: config.json file not found.")
        os._exit()
    except json.JSONDecodeError:
        print("Error: config.json file is not a valid JSON file.")
        os._exit()

def debug():
    print("Debugging")
    ###################################################
    # Test Code Here
    # print(json.dumps(, indent=4))
    ###################################################

def main():
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(
        description='A tool to manage hashes and cracking tasks in Hashtopolis for Hashes.com or HashMob.net.',
        )

    # General HashMaster functions
    parser.add_argument('-d',      '--debug',
                        action='store_true',
                        help='Run Test Code',
                        required=False
                        )

    # Hashes.com functions
    parser.add_argument('-hcj',      '--hashes_com_jobs',
                        action='store_true',
                        help='Get all jobs from Hashes.com',
                        required=False
                        )

    # HashMob.net functions
    parser.add_argument('-hmoj',      '--hashmob_net_official_jobs',
                        action='store_true',
                        help='Get all jobs from HashMob.net',
                        required=False
                        )

    # Hashtopolis functions
    parser.add_argument('-hthl',      '--hashtopolis_hashlists',
                        action='store_true',
                        help='Get all hashlist in Hashtopolis',
                        required=False
                        )

    # Parse the command-line arguments
    args = parser.parse_args()
    ###################################################
    # If the -d flag is set, call the debug function
    if args.debug:
        debug()

    # If the -hcj flag is set, call the hashes_com.get_jobs() function
    if args.hashes_com_jobs:
        # get_jobs(hashes_com_url, api_key, algorithm_id, created_at=None, min_price_per_hash=None)
        print(
            json.dumps(
                hashes_com.get_jobs(
                    config["settings"]["hashes_com"]["url"],
                    config["settings"]["hashes_com"]["api_key"],
                    1000,
                    min_price_per_hash=float(0.01)
                ),
                indent=4
            )
        )

    # If the -hmoj flag is set, call the hashmob_net.get_official_jobs() function
    if args.hashmob_net_official_jobs:
        # get_official_hashlists(hashmob_url)
        print(
            json.dumps(
                hashmob_net.get_official_hashlists(
                    config["settings"]["hashmob_net"]["url"]
                ),
                indent=4
            )
        )

    # If the -hthl flag is set, call the hashtopolis.get_all_hashlists() function
    if args.hashtopolis_hashlists:
        # get_all_hashlists(htserver, accessKey)
        print(
            json.dumps(
                hashtopolis.get_all_hashlists(
                    config["settings"]["hashtopolis"]["url"],
                    config["settings"]["hashtopolis"]["api_key"]
                ),
                indent=4
            )
        )

if __name__ == "__main__":
    load_config()
    main()
    exit()
