## ErgoWatch  ```  1.1.0  ```    ``` OAS 3.1 ```

[/openapi.json](https://api.ergo.watch/openapi.json)

ErgoWatch API docs.

Rules of thumb:

- all ERG values expressed in nanoERG
- all token values expressed in integer form
- all timestamps in milliseconds since unix epoch (same as node api)

Some endpoints will accept a `?token_id=` query parameter to return data relating to a given token instead of ERG itself.

ERG/USD data provided by [CoinGecko](https://www.coingecko.com/en/api).

### [status](https://api.ergo.watch/docs\#/status)    Database status

GET[/sync\_height](https://api.ergo.watch/docs#/status/sync_height_sync_height_get)
Sync Height

### [addresses](https://api.ergo.watch/docs\#/addresses)    Address specific data

GET[/addresses/{address}/balance](https://api.ergo.watch/docs#/addresses/address_balance_addresses__address__balance_get)
Address Balance

GET[/addresses/{address}/balance/at/height/{height}](https://api.ergo.watch/docs#/addresses/address_balance_at_height_addresses__address__balance_at_height__height__get)
Address Balance At Height

GET[/addresses/{address}/balance/at/timestamp/{timestamp}](https://api.ergo.watch/docs#/addresses/address_balance_at_timestamp_addresses__address__balance_at_timestamp__timestamp__get)
Address Balance At Timestamp

GET[/addresses/{address}/balance/history](https://api.ergo.watch/docs#/addresses/address_balance_history_addresses__address__balance_history_get)
Address Balance History

### [p2pk](https://api.ergo.watch/docs\#/p2pk)    P2PK address stats

GET[/p2pk/count](https://api.ergo.watch/docs#/p2pk/Number_of_P2PK_addresses_p2pk_count_get)
Number Of P2Pk Addresses

### [contracts](https://api.ergo.watch/docs\#/contracts)    P2S & P2SH address stats

GET[/contracts/count](https://api.ergo.watch/docs#/contracts/get_contract_address_count_contracts_count_get)
Get Contract Address Count

GET[/contracts/supply](https://api.ergo.watch/docs#/contracts/supply_in_contracts_contracts_supply_get)
Supply In Contracts

### [exchanges](https://api.ergo.watch/docs\#/exchanges)    Individual exchange data

GET[/exchanges/tracklist](https://api.ergo.watch/docs#/exchanges/list_tracked_addresses_exchanges_tracklist_get)
List Tracked Addresses

### [lists](https://api.ergo.watch/docs\#/lists)    Rich lists etc.

GET[/lists/addresses/by/balance](https://api.ergo.watch/docs#/lists/rich_list_lists_addresses_by_balance_get)
Rich List

### [utils](https://api.ergo.watch/docs\#/utils)    Sometimes helpful

GET[/utils/height2timestamp/{height}](https://api.ergo.watch/docs#/utils/height_to_timestamp_utils_height2timestamp__height__get)
Height To Timestamp

GET[/utils/timestamp2height/{timestamp}](https://api.ergo.watch/docs#/utils/timestamp_to_height_utils_timestamp2height__timestamp__get)
Timestamp To Height

### [misc](https://api.ergo.watch/docs\#/misc)

GET[/ranking/{p2pk\_address}](https://api.ergo.watch/docs#/misc/P2PK_address_rank_ranking__p2pk_address__get)
P2Pk Address Rank

GET[/sigmausd/state](https://api.ergo.watch/docs#/misc/state_sigmausd_state_get)
State

#### Schemas

AddressBalance

Expand all **object**

AddressRank

Expand all **object**

ExchangeAddressInfo

Expand all **object**

HTTPValidationError

Expand all **object**

RankResponse

Expand all **object**

SigmaUSDState

Expand all **object**

Status

Expand all **object**

ValidationError

Expand all **object**