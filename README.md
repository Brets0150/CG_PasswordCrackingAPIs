# CG_PasswordCrackingAPIs

A collection of Python functions written for APIs of common password cracking tools and websites.

### Files and Directories

- **`hashmaster.py`**: The main script that loads the configuration, parses command-line arguments, and calls functions from the `inc` modules based on the arguments.
- **`config.json`**: Configuration file that contains the application settings and API keys. This file needs to be updated with the user's API keys and details.
- **`default.config.json`**: Default configuration file that provides an example of the required settings.
- **`inc/`**: Directory containing the modules that interact with various APIs.
  - **`algorithms.py`**: Contains lists and dictionaries of supported algorithms.
  - **`hashes_com.py`**: Contains functions to interact with the Hashes.com API.
  - **`hashmob_net.py`**: Contains functions to interact with the HashMob.net API.
  - **`hashtopolis.py`**: Contains functions to interact with the Hashtopolis API.

## Usage

### Configuration

Before running the script, you need to update the `config.json` file with your API keys and details. The `config.json` file should be in the following format:

```json
{
    "app_name": "HashMaster",
    "version": "1.0.0",
    "settings": {
        "hashtopolis": {
            "api_key": "your_hashtopolis_api_key",
            "url": "http://your_hashtopolis_url",
            "cracker_version": 4,
            "hashlist_prefix": "HashMaster_"
        },
        "hashes_com": {
            "api_key": "your_hashes_com_api_key",
            "url": "https://hashes.com",
            "hashlist_prefix": "HC_",
            "high_value_pph_min_usd": 0.50,
            "hash_age_window": 240
        },
        "hashmob_net": {
            "api_key": "your_hashmob_net_api_key",
            "url": "https://hashmob.net",
            "hashlist_prefix": "HM_"
        }
    }
}
```

## Running the Script
To run the script, use the following command:

### Command-Line Options

 - -d, --debug: Run test code.
 -  -hcj, --hashes_com_jobs: Get all jobs from Hashes.com.
 - -hmoj, --hashmob_net_official_jobs: Get all jobs from HashMob.net.
 - -hthl, --hashtopolis_hashlists: Get all hashlist in Hashtopolis.

#### Example Usage
To get all jobs from Hashes.com, run:
```
python3  hashmaster.py  --hashes_com_jobs
```
## Modules
**hashtopolis.py**
Contains functions to interact with the Hashtopolis API, such as creating tasks, submitting requests, getting server configurations, and managing hashlists and tasks.

**hashes_com.py**
Contains functions to interact with the Hashes.com API, such as getting jobs, submitting cracked hashes, converting crypto to USD, and displaying profit and cracked hash history.

**hashmob_net.py**
Contains functions to interact with the HashMob.net API, such as getting user, official, and premium hashlists, downloading hashlist left hashes, submitting cracked hashes, and getting hashlist details.

**algorithms.py**
Contains lists and dictionaries of supported algorithms, including slow algorithms, mixed iteration algorithms, and valid algorithms.

