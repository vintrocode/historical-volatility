from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import pandas as pd
import calendar
import time 


# Initialize gql client
def init_client_v2():
    endpoint='https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2'
    transport=RequestsHTTPTransport(url=endpoint)
    client = Client(transport=transport, fetch_schema_from_transport=True)
    return client

# Get pairs
def get_pairs_v2():
    client = init_client_v2()
    # TODO sort on volume
    query = gql(
        """
        {
            pairs(first: 1000, orderBy: volumeUSD, orderDirection: desc) {
                id,
                token0 {
                    id
                    symbol
                },
                token1 {
                    id
                    symbol
                }
            }
        }
        """)

    result = client.execute(query)
    client.close()
    return result['pairs']


# Get pairDayData
def get_pair_day_data_v2(pair_address, iteration=1):
    """
        Get 100 days worth of data
        If len(result) < 100, you've probably gotten all the data there is
    """
    client = init_client_v2()

    daily_APYs = []
    current_time = calendar.timegm(time.gmtime())

    # Calculate epoch time of date deltas 
    end_date = current_time - (86400000 * iteration) # 1000 days in seconds 



    query = gql(
    """
    query ($address: Bytes!, $enddate: Int!) {
        pairDayDatas(first: 1000, orderBy: date, orderDirection: desc,
        where: {
            pairAddress: $address,
            date_gt: $enddate
    }
    ) {
        date
        token0 {
            symbol
        }
        token1 {
            symbol
        }
        dailyVolumeToken0
        dailyVolumeToken1
        dailyVolumeUSD
        totalSupply
        reserveUSD
    }
    }
    """)
    params = {
        "address": pair_address,
        "enddate": end_date,
        }

    result = client.execute(query, variable_values=params)

    client.close()



    if len(result["pairDayDatas"]) < 1000:

        iteration = 'Done'
        return result['pairDayDatas'], iteration

    else:
        iteration = iteration + 1
        return result['pairDayDatas'], iteration

