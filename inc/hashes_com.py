import requests
import pandas as pd
from tabulate import tabulate
from datetime import datetime, timedelta

def get_jobs(hashes_com_url, api_key, algorithm_id, created_at=None, min_price_per_hash=None):
    # Function that will perform a https request to "https://hashes.com/en/api/jobs?key=<APIkey>" to get the list of jobs and put the returned JSON in a variable.
    # Then use the Aglorithm ID to filter the jobs and return the list of jobs that match the Algorithm ID.
    # if a created_at date is provided, it will filter the jobs that were created after the provided date.
    # Example responce below:
    #     "success": true,
    #     "list": [
    #         {
    #             "id": 5,
    #             "createdAt": "2023-01-19 18:06:19",
    #             "lastUpdate": "2023-01-19 19:21:10",
    #             "algorithmName": "MD5",
    #             "algorithmId": 0,
    #             "totalHashes": 1,
    #             "foundHashes": 0,
    #             "leftHashes": 1,
    #             "currency": "XMR",
    #             "pricePerHash": "0.00595300",
    #             "pricePerHashUsd": "1.000",
    #             "maxCracksNeeded": 1,
    #             "leftList": "\/unfound\/5-1674174070-a97166c4-unfound.txt"
    #         },
    #         {
    #             "id": 6,
    #             "createdAt": "2023-01-19 18:10:39",
    #             "lastUpdate": "2023-01-19 19:21:10",
    #             "algorithmName": "MD5",
    #             "algorithmId": 0,
    #             "totalHashes": 1,
    #             "foundHashes": 0,
    #             "leftHashes": 1,
    #             "currency": "LTC",
    #             "pricePerHash": "0.00000010",
    #             "pricePerHashUsd": "0.000",
    #             "maxCracksNeeded": 1,
    #             "leftList": "\/unfound\/6-1674174070-532062d5-unfound.txt"
    #         }
    #     ]
    # }
    # Use the loaded config json to get the hashess.com api key

    url = "%s/en/api/jobs?key=%s" % (hashes_com_url, api_key)
    response = requests.get(url)
    jobs = response.json()
    if jobs['success'] == True:
        jobs_list = jobs['list']
        if created_at:
            jobs_list = [job for job in jobs_list if job['algorithmId'] == algorithm_id and datetime.strptime(job['createdAt'], "%Y-%m-%d %H:%M:%S") >= created_at]
        else:
            jobs_list = [job for job in jobs_list if job['algorithmId'] == algorithm_id]

        # If a min_price_per_hash is provided, then filter the jobs that have a pricePerHashUsd greater than or equal to the min_price_per_hash.
        if min_price_per_hash:
            jobs_list = [job for job in jobs_list if float(job['pricePerHashUsd']) >= min_price_per_hash]

        return jobs_list
    else:
        print("Error: %s" % (jobs['error']))
        return None

def submit_cracked_hashes(hashes_com_url, api_key, found_hashes_file, algorithm_id):
    # Function that will perform a https request to "https://hashes.com/en/api/founds" with the following parameters:
    # Example: curl -X POST -H "Content-type: multipart/form-data" -F "key=0ebb2b263f694af6095de96e4aac7d59" -F "algo=2811" -F "userfile=@/home/root/founds.txt" https://hashes.com/en/api/founds
    url = "%s/en/api/founds" % (hashes_com_url)
    data = {
        "key": api_key,
        "algo": algorithm_id
    }
    files = {
        "userfile": ("founds.txt", open(found_hashes_file, "rb"))
    }
    try:
        response = requests.post(url, data=data, files=files)
        if response.status_code == 200:
            return response.text
        else:
            print("Error: %s" % (response.text))
            return None
    except requests.exceptions.ConnectionError as error_code:
        print('Failed to connect to the Hashes.com server. Error: %s' % error_code)
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

def to_usd(value, currency):
     # Converts crypto to USD values using the Kraken API. I took this from 'https://github.com/PlumLulz/hashes.com-cli/blob/master/hashes.py'
	if currency != "credits":
		url = "https://api.kraken.com/0/public/Ticker?pair=%susd" % (currency)
		resp = requests.get(url).json()
		#currentprice = resp['USD']
		if currency.upper() == "BTC":
			currentprice = resp['result']['XXBTZUSD']['a'][0]
		elif currency.upper() == "XMR":
			currentprice = resp['result']['XXMRZUSD']['a'][0]
		elif currency.upper() == "LTC":
			currentprice = resp['result']['XLTCZUSD']['a'][0]
		converted = "${0:.3f}".format(float(value) * float(currentprice))
		return {"currentprice": currentprice, "converted": converted}
	else:
		return {"currentprice": None, "converted": "N/A"}

def get_cracked_hash_history(hashes_com_url, api_key):
    # Function that will perform a request to "https://hashes.com/en/api/uploads?key=0ebb2b263f694af6095de96e4aac7d59" toget a JSON of all the cracked hashes.
    url = "%s/en/api/uploads?key=%s" % (hashes_com_url, api_key)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error: %s" % (response.text))
        return None

def get_profit(hashes_com_url, api_key):
    # Function that will perform a request to "https://hashes.com/en/api/profit?key=0ebb2b263f694af6095de96e4aac7d59" to get the profitability of the user.
    # curl https://hashes.com/en/api/profit?key=0ebb2b263f694af6095de96e4aac7d59
    url = "%s/en/api/profit?key=%s" % (hashes_com_url, api_key)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error: %s" % (response.text))
        return None

def display_profit(hashes_com_url, api_key):
    profit = get_profit(hashes_com_url, api_key)
    # Get the total BTC, XMR, and LTC values from the list and convert them to USD using the to_usd function.
    total_btc = profit['currency']['BTC']
    total_xmr = profit['currency']['XMR']
    total_ltc = profit['currency']['LTC']
    total_btc_usd = to_usd(total_btc, 'BTC')['converted']
    total_xmr_usd = to_usd(total_xmr, 'XMR')['converted']
    total_ltc_usd = to_usd(total_ltc, 'LTC')['converted']
    # Print the total BTC, XMR, and LTC values in USD.
    print("Total BTC: %s" % total_btc_usd)
    print("Total XMR: %s" % total_xmr_usd)
    print("Total LTC: %s" % total_ltc_usd)

def display_cracked_hash_history(hashes_com_url, api_key, days):
    # Example input JSON:
    # {
    #     "success": true,
    #     "list": [
    #         {
    #             "id": 512142,
    #             "btc": "0.0000011305",
    #             "xmr": "0",
    #             "ltc": "0.0000095",
    #             "date": "2024-09-10 21:49:28",
    #             "totalHashes": 1,
    #             "validHashes": 2,
    #             "status": "Processed",
    #             "algorithm": "NTLM",
    #             "algorithmId": 1000
    #         },
    #         {
    #             "id": 524342,
    #             "btc": "0.0000770165",
    #             "xmr": "0",
    #             "ltc": "0.00022857",
    #             "date": "2024-10-03 10:49:58",
    #             "totalHashes": 28,
    #             "validHashes": 49,
    #             "status": "Processed",
    #             "algorithm": "NTLM",
    #             "algorithmId": 1000
    #         }
    #     ]
    # }
    # Function that will display the last X number of days of cracked hashes.
    crack_history = get_cracked_hash_history(hashes_com_url, api_key)
    # Only use the last X number of days of cracked hashes.
    if days:
        crack_history['list'] = [item for item in crack_history['list'] if datetime.strptime(item['date'], "%Y-%m-%d %H:%M:%S") >= datetime.now() - timedelta(days=days)]

    if crack_history:
        # Convert the BTC, XMR, and LTC values to USD using the to_usd function and add the converted values to the list item as new keys; 'btc_usd', 'xmr_usd', 'ltc_usd'.
        for item in crack_history['list']:
            item['btc_usd'] = to_usd(item['btc'], 'BTC')['converted']
            item['xmr_usd'] = to_usd(item['xmr'], 'XMR')['converted']
            item['ltc_usd'] = to_usd(item['ltc'], 'LTC')['converted']
        # Use Pandas to Display each list item in a table format, with the following columns: Date, ID, Algorithm, Status, Total Hashes, Valid Hashes, BTC, XMR, LTC. Sort the table by Date.
        # Example:  Date                ID      Algorithm   Status      Total Hashes    Valid Hashes    BTC             XMR     LTC
        #           2024-09-10 21:49:28 512142  NTLM        Processed   1               2               0.0000011305    0       0.0000095
        #           2024-10-03 10:49:58 524342  NTLM        Processed   28              49              0.0000770165    0       0.00022857
        columns = ['date', 'status', 'algorithm', 'totalHashes', 'validHashes', 'btc', 'btc_usd', 'xmr', 'xmr_usd', 'ltc' , 'ltc_usd']
        df = pd.DataFrame(crack_history['list'], columns=columns)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(by='date')
        print(tabulate(df, headers='keys', tablefmt='psql'))

        # Get the total BTC, XMR, and LTC values from the list and convert them to USD using the to_usd function.
        total_btc = sum([float(item['btc']) for item in crack_history['list']])
        total_xmr = sum([float(item['xmr']) for item in crack_history['list']])
        total_ltc = sum([float(item['ltc']) for item in crack_history['list']])
        total_btc_usd = to_usd(total_btc, 'BTC')['converted']
        total_xmr_usd = to_usd(total_xmr, 'XMR')['converted']
        total_ltc_usd = to_usd(total_ltc, 'LTC')['converted']
        # Print the total BTC, XMR, and LTC values in USD.
        print("Total BTC: %s" % total_btc_usd)
        print("Total XMR: %s" % total_xmr_usd)
        print("Total LTC: %s" % total_ltc_usd)