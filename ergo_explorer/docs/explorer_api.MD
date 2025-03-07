- transactions
- boxes
- assets
- epochs
- addresses
- blocks
- getgetApiV1TransactionsP1
- getgetApiV1TransactionsByinputsscripttemplatehashP1
- getgetApiV1TransactionsByglobalindexStream
- getgetApiV1BoxesUnspentBylastepochsStream
- getgetApiV1BoxesUnspentByglobalindexStream
- getgetApiV1BoxesUnspentStream
- getgetApiV1BoxesByergotreetemplatehashP1Stream
- getgetApiV1BoxesUnspentByergotreetemplatehashP1Stream
- getgetApiV1BoxesUnspentBytokenidP1
- getgetApiV1BoxesBytokenidP1
- getgetApiV1BoxesP1
- getgetApiV1BoxesByergotreeP1
- getgetApiV1BoxesByergotreetemplatehashP1
- getgetApiV1BoxesUnspentByergotreeP1
- getgetApiV1BoxesUnspentByergotreetemplatehashP1
- getgetApiV1BoxesByaddressP1
- getgetApiV1BoxesUnspentUnconfirmedByaddressP1
- getgetApiV1BoxesUnspentByaddressP1
- getgetApiV1BoxesByglobalindexStream
- postpostApiV1BoxesUnspentSearchUnion
- postpostApiV1BoxesUnspentSearch
- postpostApiV1BoxesSearch
- getgetApiV1Tokens
- getgetApiV1TokensSearch
- getgetApiV1TokensBysymbolP1
- getgetApiV1TokensP1
- getgetApiV1Assets
- getgetApiV1AssetsSearchBytokenid
- getgetApiV1EpochsParams
- getgetApiV1AddressesP1Transactions
- getgetApiV1AddressesP1BalanceConfirmed
- getgetApiV1AddressesP1BalanceTotal
- getgetApiV1Blocks
- getgetApiV1BlocksP1
- getgetApiV1BlocksHeaders
- getgetApiV1BlocksByglobalindexStream
- getgetApiV1BlocksStreamSummary
- postpostApiV1MempoolTransactionsSubmit
- getgetApiV1MempoolTransactionsByaddressP1
- getgetApiV1MempoolBoxesUnspent
- getgetApiV1Info
- getgetApiV1Networkstate
- getgetApiV1Networkstats
- postpostApiV1ErgotreeConvert

[Documentation Powered by ReDoc](https://github.com/Redocly/redoc)

# Ergo Explorer API v1 (1.0)

Download OpenAPI specification: [Download](https://api.ergoplatform.com/api/v1/docs/openapi)

# transactions

Transactions methods

# boxes

Boxes methods

# assets

Assets methods

# epochs

Epochs methods

# addresses

Addresses methods

# blocks

Blocks methods

## getApiV1TransactionsP1

##### path Parameters

|     |     |
| --- | --- |
| p1<br>required | string |

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| id<br>required | string<br>Transaction ID |
| blockId<br>required | string<br>ID of the corresponding header |
| inclusionHeight<br>required | integer<br>Height of the block the transaction was included in |
| timestamp<br>required | integer <int64> <br>Timestamp the transaction got into the network |
| index<br>required | integer<br>Index of a transaction inside a block |
| globalIndex<br>required | integer <int64> <br>global index of a transaction in the blockchain |
| numConfirmations<br>required | integer<br>Number of transaction confirmations |
| inputs | Array of objects (InputInfo) |
| dataInputs | Array of objects (DataInputInfo) |
| outputs | Array of objects (OutputInfo) |
| size<br>required | integer<br>Transaction size in bytes |

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/transactions/{p1}

https://api.ergoplatform.com/api/v1/transactions/{p1}

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"id": "string",
"blockId": "string",
"inclusionHeight": 0,
"timestamp": 0,
"index": 0,
"globalIndex": 0,
"numConfirmations": 0,
"inputs":
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"spendingProof": "string",\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"outputGlobalIndex": 0,\
"outputCreatedAt": 0,\
"outputSettledAt": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],
"dataInputs":
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"ergoTree": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],
"outputs":
[\
{\
"boxId": "string",\
"transactionId": "string",\
"blockId": "string",\
"value": 0,\
"index": 0,\
"globalIndex": 0,\
"creationHeight": 0,\
"settlementHeight": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"},\
"spentTransactionId": "string",\
"mainChain": true}],
"size": 0}`

## getApiV1TransactionsByinputsscripttemplatehashP1

##### path Parameters

|     |     |
| --- | --- |
| p1<br>required | string |

##### query Parameters

|     |     |
| --- | --- |
| offset | integer >= 0 |
| limit | integer \[ 1 .. 500 \] |
| sortDirection | string |

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| items | Array of objects (TransactionInfo) <br>Items in selection |
| total<br>required | integer<br>Total qty of items |

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/transactions/byInputsScriptTemplateHash/{p1}

https://api.ergoplatform.com/api/v1/transactions/byInputsScriptTemplateHash/{p1}

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"items":
[\
{\
"id": "string",\
"blockId": "string",\
"inclusionHeight": 0,\
"timestamp": 0,\
"index": 0,\
"globalIndex": 0,\
"numConfirmations": 0,\
"inputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"spendingProof": "string",\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"outputGlobalIndex": 0,\
"outputCreatedAt": 0,\
"outputSettledAt": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"dataInputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"ergoTree": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"outputs":\
[\
{\
"boxId": "string",\
"transactionId": "string",\
"blockId": "string",\
"value": 0,\
"index": 0,\
"globalIndex": 0,\
"creationHeight": 0,\
"settlementHeight": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"},\
"spentTransactionId": "string",\
"mainChain": true}],\
"size": 0}],
"total": 0}`

## getApiV1TransactionsByglobalindexStream

Get a stream of transactions ordered by global index

##### query Parameters

|     |     |
| --- | --- |
| minGix<br>required | integer <int64>  >= 0 <br>Min global index (in blockchain) of the TX |
| limit<br>required | integer <= 500 |

### Responses

**200**

##### Response Schema: application/json

One of

- Nil
- TransactionInfo

|
|

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/transactions/byGlobalIndex/stream

https://api.ergoplatform.com/api/v1/transactions/byGlobalIndex/stream

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Example

Nil

Copy
Expand all  Collapse all

`{ }`

## getApiV1BoxesUnspentBylastepochsStream

##### query Parameters

|     |     |
| --- | --- |
| lastEpochs<br>required | integer <= 1536 |

### Responses

**200**

##### Response Schema: application/json

One of

- Nil
- OutputInfo

|
|

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/boxes/unspent/byLastEpochs/stream

https://api.ergoplatform.com/api/v1/boxes/unspent/byLastEpochs/stream

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Example

Nil

Copy
Expand all  Collapse all

`{ }`

## getApiV1BoxesUnspentByglobalindexStream

Get a stream of unspent outputs ordered by global index

##### query Parameters

|     |     |
| --- | --- |
| minGix<br>required | integer <int64>  >= 0 <br>Min global index (in blockchain) of an on-chain entity |
| limit<br>required | integer <= 500 |

### Responses

**200**

##### Response Schema: application/json

One of

- Nil
- OutputInfo

|
|

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/boxes/unspent/byGlobalIndex/stream

https://api.ergoplatform.com/api/v1/boxes/unspent/byGlobalIndex/stream

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Example

Nil

Copy
Expand all  Collapse all

`{ }`

## getApiV1BoxesUnspentStream

##### query Parameters

|     |     |
| --- | --- |
| minHeight<br>required | integer >= 0 |
| maxHeight<br>required | integer >= 1 |

### Responses

**200**

##### Response Schema: application/json

One of

- Nil
- OutputInfo

|
|

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/boxes/unspent/stream

https://api.ergoplatform.com/api/v1/boxes/unspent/stream

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Example

Nil

Copy
Expand all  Collapse all

`{ }`

## getApiV1BoxesByergotreetemplatehashP1Stream

Get a stream of unspent outputs by a hash of the given ErgoTreeTemplate

##### path Parameters

|     |     |
| --- | --- |
| p1<br>required | string |

##### query Parameters

|     |     |
| --- | --- |
| minHeight<br>required | integer >= 0 |
| maxHeight<br>required | integer >= 1 |

### Responses

**200**

##### Response Schema: application/json

One of

- Nil
- OutputInfo

|
|

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/boxes/byErgoTreeTemplateHash/{p1}/stream

https://api.ergoplatform.com/api/v1/boxes/byErgoTreeTemplateHash/{p1}/stream

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Example

Nil

Copy
Expand all  Collapse all

`{ }`

## getApiV1BoxesUnspentByergotreetemplatehashP1Stream

##### path Parameters

|     |     |
| --- | --- |
| p1<br>required | string |

##### query Parameters

|     |     |
| --- | --- |
| minHeight<br>required | integer >= 0 |
| maxHeight<br>required | integer >= 1 |

### Responses

**200**

##### Response Schema: application/json

One of

- Nil
- OutputInfo

|
|

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/boxes/unspent/byErgoTreeTemplateHash/{p1}/stream

https://api.ergoplatform.com/api/v1/boxes/unspent/byErgoTreeTemplateHash/{p1}/stream

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Example

Nil

Copy
Expand all  Collapse all

`{ }`

## getApiV1BoxesUnspentBytokenidP1

##### path Parameters

|     |     |
| --- | --- |
| p1<br>required | string |

##### query Parameters

|     |     |
| --- | --- |
| offset | integer >= 0 |
| limit | integer \[ 1 .. 100 \] |
| sortDirection | string |

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| items | Array of objects (TransactionInfo) <br>Items in selection |
| total<br>required | integer<br>Total qty of items |

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/boxes/unspent/byTokenId/{p1}

https://api.ergoplatform.com/api/v1/boxes/unspent/byTokenId/{p1}

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"items":
[\
{\
"id": "string",\
"blockId": "string",\
"inclusionHeight": 0,\
"timestamp": 0,\
"index": 0,\
"globalIndex": 0,\
"numConfirmations": 0,\
"inputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"spendingProof": "string",\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"outputGlobalIndex": 0,\
"outputCreatedAt": 0,\
"outputSettledAt": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"dataInputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"ergoTree": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"outputs":\
[\
{\
"boxId": "string",\
"transactionId": "string",\
"blockId": "string",\
"value": 0,\
"index": 0,\
"globalIndex": 0,\
"creationHeight": 0,\
"settlementHeight": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"},\
"spentTransactionId": "string",\
"mainChain": true}],\
"size": 0}],
"total": 0}`

## getApiV1BoxesBytokenidP1

##### path Parameters

|     |     |
| --- | --- |
| p1<br>required | string |

##### query Parameters

|     |     |
| --- | --- |
| offset | integer >= 0 |
| limit | integer \[ 1 .. 100 \] |

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| items | Array of objects (TransactionInfo) <br>Items in selection |
| total<br>required | integer<br>Total qty of items |

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/boxes/byTokenId/{p1}

https://api.ergoplatform.com/api/v1/boxes/byTokenId/{p1}

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"items":
[\
{\
"id": "string",\
"blockId": "string",\
"inclusionHeight": 0,\
"timestamp": 0,\
"index": 0,\
"globalIndex": 0,\
"numConfirmations": 0,\
"inputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"spendingProof": "string",\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"outputGlobalIndex": 0,\
"outputCreatedAt": 0,\
"outputSettledAt": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"dataInputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"ergoTree": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"outputs":\
[\
{\
"boxId": "string",\
"transactionId": "string",\
"blockId": "string",\
"value": 0,\
"index": 0,\
"globalIndex": 0,\
"creationHeight": 0,\
"settlementHeight": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"},\
"spentTransactionId": "string",\
"mainChain": true}],\
"size": 0}],
"total": 0}`

## getApiV1BoxesP1

##### path Parameters

|     |     |
| --- | --- |
| p1<br>required | string |

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| boxId<br>required | string<br>Id of the box |
| transactionId<br>required | string<br>Id of the transaction that created the box |
| blockId<br>required | string<br>Id of the block a box included in |
| value<br>required | integer <int64> <br>Value of the box in nanoERG |
| index<br>required | integer<br>Index of the output in a transaction |
| globalIndex<br>required | integer <int64> <br>Global index of the output in the blockchain |
| creationHeight<br>required | integer<br>Height at which the box was created |
| settlementHeight<br>required | integer<br>Height at which the box got fixed in blockchain |
| ergoTree<br>required | string<br>Serialized ergo tree |
| ergoTreeConstants<br>required | string |
| ergoTreeScript<br>required | string |
| address<br>required | string<br>An address derived from ergo tree |
| assets | Array of objects (AssetInstanceInfo) |
| additionalRegisters<br>required | object |
| spentTransactionId | string<br>Id of the transaction this output was spent by |
| mainChain<br>required | boolean |

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/boxes/{p1}

https://api.ergoplatform.com/api/v1/boxes/{p1}

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"boxId": "string",
"transactionId": "string",
"blockId": "string",
"value": 0,
"index": 0,
"globalIndex": 0,
"creationHeight": 0,
"settlementHeight": 0,
"ergoTree": "string",
"ergoTreeConstants": "string",
"ergoTreeScript": "string",
"address": "string",
"assets":
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],
"additionalRegisters":
{
"property1": "string",
"property2": "string"},
"spentTransactionId": "string",
"mainChain": true}`

## getApiV1BoxesByergotreeP1

##### path Parameters

|     |     |
| --- | --- |
| p1<br>required | string |

##### query Parameters

|     |     |
| --- | --- |
| offset | integer >= 0 |
| limit | integer \[ 1 .. 500 \] |

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| items | Array of objects (TransactionInfo) <br>Items in selection |
| total<br>required | integer<br>Total qty of items |

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/boxes/byErgoTree/{p1}

https://api.ergoplatform.com/api/v1/boxes/byErgoTree/{p1}

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"items":
[\
{\
"id": "string",\
"blockId": "string",\
"inclusionHeight": 0,\
"timestamp": 0,\
"index": 0,\
"globalIndex": 0,\
"numConfirmations": 0,\
"inputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"spendingProof": "string",\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"outputGlobalIndex": 0,\
"outputCreatedAt": 0,\
"outputSettledAt": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"dataInputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"ergoTree": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"outputs":\
[\
{\
"boxId": "string",\
"transactionId": "string",\
"blockId": "string",\
"value": 0,\
"index": 0,\
"globalIndex": 0,\
"creationHeight": 0,\
"settlementHeight": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"},\
"spentTransactionId": "string",\
"mainChain": true}],\
"size": 0}],
"total": 0}`

## getApiV1BoxesByergotreetemplatehashP1

##### path Parameters

|     |     |
| --- | --- |
| p1<br>required | string |

##### query Parameters

|     |     |
| --- | --- |
| offset | integer >= 0 |
| limit | integer \[ 1 .. 500 \] |

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| items | Array of objects (TransactionInfo) <br>Items in selection |
| total<br>required | integer<br>Total qty of items |

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/boxes/byErgoTreeTemplateHash/{p1}

https://api.ergoplatform.com/api/v1/boxes/byErgoTreeTemplateHash/{p1}

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"items":
[\
{\
"id": "string",\
"blockId": "string",\
"inclusionHeight": 0,\
"timestamp": 0,\
"index": 0,\
"globalIndex": 0,\
"numConfirmations": 0,\
"inputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"spendingProof": "string",\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"outputGlobalIndex": 0,\
"outputCreatedAt": 0,\
"outputSettledAt": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"dataInputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"ergoTree": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"outputs":\
[\
{\
"boxId": "string",\
"transactionId": "string",\
"blockId": "string",\
"value": 0,\
"index": 0,\
"globalIndex": 0,\
"creationHeight": 0,\
"settlementHeight": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"},\
"spentTransactionId": "string",\
"mainChain": true}],\
"size": 0}],
"total": 0}`

## getApiV1BoxesUnspentByergotreeP1

##### path Parameters

|     |     |
| --- | --- |
| p1<br>required | string |

##### query Parameters

|     |     |
| --- | --- |
| offset | integer >= 0 |
| limit | integer \[ 1 .. 500 \] |
| sortDirection | string |

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| items | Array of objects (TransactionInfo) <br>Items in selection |
| total<br>required | integer<br>Total qty of items |

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/boxes/unspent/byErgoTree/{p1}

https://api.ergoplatform.com/api/v1/boxes/unspent/byErgoTree/{p1}

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"items":
[\
{\
"id": "string",\
"blockId": "string",\
"inclusionHeight": 0,\
"timestamp": 0,\
"index": 0,\
"globalIndex": 0,\
"numConfirmations": 0,\
"inputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"spendingProof": "string",\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"outputGlobalIndex": 0,\
"outputCreatedAt": 0,\
"outputSettledAt": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"dataInputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"ergoTree": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"outputs":\
[\
{\
"boxId": "string",\
"transactionId": "string",\
"blockId": "string",\
"value": 0,\
"index": 0,\
"globalIndex": 0,\
"creationHeight": 0,\
"settlementHeight": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"},\
"spentTransactionId": "string",\
"mainChain": true}],\
"size": 0}],
"total": 0}`

## getApiV1BoxesUnspentByergotreetemplatehashP1

##### path Parameters

|     |     |
| --- | --- |
| p1<br>required | string |

##### query Parameters

|     |     |
| --- | --- |
| offset | integer >= 0 |
| limit | integer \[ 1 .. 500 \] |

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| items | Array of objects (TransactionInfo) <br>Items in selection |
| total<br>required | integer<br>Total qty of items |

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/boxes/unspent/byErgoTreeTemplateHash/{p1}

https://api.ergoplatform.com/api/v1/boxes/unspent/byErgoTreeTemplateHash/{p1}

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"items":
[\
{\
"id": "string",\
"blockId": "string",\
"inclusionHeight": 0,\
"timestamp": 0,\
"index": 0,\
"globalIndex": 0,\
"numConfirmations": 0,\
"inputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"spendingProof": "string",\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"outputGlobalIndex": 0,\
"outputCreatedAt": 0,\
"outputSettledAt": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"dataInputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"ergoTree": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"outputs":\
[\
{\
"boxId": "string",\
"transactionId": "string",\
"blockId": "string",\
"value": 0,\
"index": 0,\
"globalIndex": 0,\
"creationHeight": 0,\
"settlementHeight": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"},\
"spentTransactionId": "string",\
"mainChain": true}],\
"size": 0}],
"total": 0}`

## getApiV1BoxesByaddressP1

##### path Parameters

|     |     |
| --- | --- |
| p1<br>required | string |

##### query Parameters

|     |     |
| --- | --- |
| offset | integer >= 0 |
| limit | integer \[ 1 .. 500 \] |

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| items | Array of objects (TransactionInfo) <br>Items in selection |
| total<br>required | integer<br>Total qty of items |

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/boxes/byAddress/{p1}

https://api.ergoplatform.com/api/v1/boxes/byAddress/{p1}

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"items":
[\
{\
"id": "string",\
"blockId": "string",\
"inclusionHeight": 0,\
"timestamp": 0,\
"index": 0,\
"globalIndex": 0,\
"numConfirmations": 0,\
"inputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"spendingProof": "string",\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"outputGlobalIndex": 0,\
"outputCreatedAt": 0,\
"outputSettledAt": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"dataInputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"ergoTree": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"outputs":\
[\
{\
"boxId": "string",\
"transactionId": "string",\
"blockId": "string",\
"value": 0,\
"index": 0,\
"globalIndex": 0,\
"creationHeight": 0,\
"settlementHeight": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"},\
"spentTransactionId": "string",\
"mainChain": true}],\
"size": 0}],
"total": 0}`

## getApiV1BoxesUnspentUnconfirmedByaddressP1

##### path Parameters

|     |     |
| --- | --- |
| p1<br>required | string |

##### query Parameters

|     |     |
| --- | --- |
| sortDirection | string |

### Responses

**200**

##### Response Schema: application/json

Array

|     |     |
| --- | --- |
| boxId<br>required | string<br>Id of the box |
| transactionId<br>required | string<br>Id of the transaction that created the box |
| blockId | string<br>Id of the block a box included in |
| value<br>required | integer <int64> <br>Value of the box in nanoERG |
| index<br>required | integer<br>Index of the output in a transaction |
| globalIndex | integer <int64> <br>Global index of the output in the blockchain |
| creationHeight<br>required | integer<br>Height at which the box was created |
| settlementHeight | integer<br>Height at which the box got fixed in blockchain |
| ergoTree<br>required | string<br>Serialized ergo tree |
| address<br>required | string<br>An address derived from ergo tree |
| assets | Array of objects (AssetInstanceInfo) |
| additionalRegisters<br>required | object |
| spentTransactionId | string<br>Id of the transaction this output was spent by |
| mainChain<br>required | boolean |

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/boxes/unspent/unconfirmed/byAddress/{p1}

https://api.ergoplatform.com/api/v1/boxes/unspent/unconfirmed/byAddress/{p1}

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
[\
{\
"boxId": "string",\
"transactionId": "string",\
"blockId": "string",\
"value": 0,\
"index": 0,\
"globalIndex": 0,\
"creationHeight": 0,\
"settlementHeight": 0,\
"ergoTree": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"},\
"spentTransactionId": "string",\
"mainChain": true}]`

## getApiV1BoxesUnspentByaddressP1

##### path Parameters

|     |     |
| --- | --- |
| p1<br>required | string |

##### query Parameters

|     |     |
| --- | --- |
| offset | integer >= 0 |
| limit | integer \[ 1 .. 500 \] |
| sortDirection | string |

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| items | Array of objects (TransactionInfo) <br>Items in selection |
| total<br>required | integer<br>Total qty of items |

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/boxes/unspent/byAddress/{p1}

https://api.ergoplatform.com/api/v1/boxes/unspent/byAddress/{p1}

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"items":
[\
{\
"id": "string",\
"blockId": "string",\
"inclusionHeight": 0,\
"timestamp": 0,\
"index": 0,\
"globalIndex": 0,\
"numConfirmations": 0,\
"inputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"spendingProof": "string",\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"outputGlobalIndex": 0,\
"outputCreatedAt": 0,\
"outputSettledAt": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"dataInputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"ergoTree": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"outputs":\
[\
{\
"boxId": "string",\
"transactionId": "string",\
"blockId": "string",\
"value": 0,\
"index": 0,\
"globalIndex": 0,\
"creationHeight": 0,\
"settlementHeight": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"},\
"spentTransactionId": "string",\
"mainChain": true}],\
"size": 0}],
"total": 0}`

## getApiV1BoxesByglobalindexStream

Get a stream of outputs ordered by global index

##### query Parameters

|     |     |
| --- | --- |
| minGix<br>required | integer <int64>  >= 0 <br>Min global index (in blockchain) of an on-chain entity |
| limit<br>required | integer <= 500 |

### Responses

**200**

##### Response Schema: application/json

One of

- Nil
- OutputInfo

|
|

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/boxes/byGlobalIndex/stream

https://api.ergoplatform.com/api/v1/boxes/byGlobalIndex/stream

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Example

Nil

Copy
Expand all  Collapse all

`{ }`

## postApiV1BoxesUnspentSearchUnion

Search among UTXO set by ergoTreeTemplateHash and tokens. The resulted UTXOs will contain at lest one of the given tokens.

##### query Parameters

|     |     |
| --- | --- |
| offset | integer >= 0 |
| limit | integer \[ 1 .. 500 \] |

##### Request Body schema: application/json

|     |     |
| --- | --- |
| ergoTreeTemplateHash<br>required | string<br>SHA-256 hash of ErgoTree template this box script should have |
| assets | Array of strings<br>IDs of tokens returned boxes should contain |

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| items | Array of objects (TransactionInfo) <br>Items in selection |
| total<br>required | integer<br>Total qty of items |

**400**
Bad request

**404**
Not found

**default**
Unknown error

post/api/v1/boxes/unspent/search/union

https://api.ergoplatform.com/api/v1/boxes/unspent/search/union

### Request samples

- Payload

Content type

application/json

Copy
Expand all  Collapse all

`
{
"ergoTreeTemplateHash": "string",
"assets":
[\
"string"]}`

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"items":
[\
{\
"id": "string",\
"blockId": "string",\
"inclusionHeight": 0,\
"timestamp": 0,\
"index": 0,\
"globalIndex": 0,\
"numConfirmations": 0,\
"inputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"spendingProof": "string",\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"outputGlobalIndex": 0,\
"outputCreatedAt": 0,\
"outputSettledAt": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"dataInputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"ergoTree": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"outputs":\
[\
{\
"boxId": "string",\
"transactionId": "string",\
"blockId": "string",\
"value": 0,\
"index": 0,\
"globalIndex": 0,\
"creationHeight": 0,\
"settlementHeight": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"},\
"spentTransactionId": "string",\
"mainChain": true}],\
"size": 0}],
"total": 0}`

## postApiV1BoxesUnspentSearch

Detailed search among UTXO set

##### query Parameters

|     |     |
| --- | --- |
| offset | integer >= 0 |
| limit | integer \[ 1 .. 500 \] |

##### Request Body schema: application/json

|     |     |
| --- | --- |
| ergoTreeTemplateHash<br>required | string<br>SHA-256 hash of ErgoTree template this box script should have |
| registers | object<br>Pairs of (register ID, register value) this box should contain |
| constants | object<br>Pairs of (constant index, constant value) this box should contain |
| assets | Array of strings<br>IDs of tokens returned boxes should contain |

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| items | Array of objects (TransactionInfo) <br>Items in selection |
| total<br>required | integer<br>Total qty of items |

**400**
Bad request

**404**
Not found

**default**
Unknown error

post/api/v1/boxes/unspent/search

https://api.ergoplatform.com/api/v1/boxes/unspent/search

### Request samples

- Payload

Content type

application/json

Copy
Expand all  Collapse all

`
{
"ergoTreeTemplateHash": "string",
"registers":
{
"property1": "string",
"property2": "string"},
"constants":
{
"property1": "string",
"property2": "string"},
"assets":
[\
"string"]}`

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"items":
[\
{\
"id": "string",\
"blockId": "string",\
"inclusionHeight": 0,\
"timestamp": 0,\
"index": 0,\
"globalIndex": 0,\
"numConfirmations": 0,\
"inputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"spendingProof": "string",\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"outputGlobalIndex": 0,\
"outputCreatedAt": 0,\
"outputSettledAt": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"dataInputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"ergoTree": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"outputs":\
[\
{\
"boxId": "string",\
"transactionId": "string",\
"blockId": "string",\
"value": 0,\
"index": 0,\
"globalIndex": 0,\
"creationHeight": 0,\
"settlementHeight": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"},\
"spentTransactionId": "string",\
"mainChain": true}],\
"size": 0}],
"total": 0}`

## postApiV1BoxesSearch

Detailed search among all boxes in the chain

##### query Parameters

|     |     |
| --- | --- |
| offset | integer >= 0 |
| limit | integer \[ 1 .. 500 \] |

##### Request Body schema: application/json

|     |     |
| --- | --- |
| ergoTreeTemplateHash<br>required | string<br>SHA-256 hash of ErgoTree template this box script should have |
| registers | object<br>Pairs of (register ID, register value) this box should contain |
| constants | object<br>Pairs of (constant index, constant value) this box should contain |
| assets | Array of strings<br>IDs of tokens returned boxes should contain |

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| items | Array of objects (TransactionInfo) <br>Items in selection |
| total<br>required | integer<br>Total qty of items |

**400**
Bad request

**404**
Not found

**default**
Unknown error

post/api/v1/boxes/search

https://api.ergoplatform.com/api/v1/boxes/search

### Request samples

- Payload

Content type

application/json

Copy
Expand all  Collapse all

`
{
"ergoTreeTemplateHash": "string",
"registers":
{
"property1": "string",
"property2": "string"},
"constants":
{
"property1": "string",
"property2": "string"},
"assets":
[\
"string"]}`

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"items":
[\
{\
"id": "string",\
"blockId": "string",\
"inclusionHeight": 0,\
"timestamp": 0,\
"index": 0,\
"globalIndex": 0,\
"numConfirmations": 0,\
"inputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"spendingProof": "string",\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"outputGlobalIndex": 0,\
"outputCreatedAt": 0,\
"outputSettledAt": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"dataInputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"ergoTree": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"outputs":\
[\
{\
"boxId": "string",\
"transactionId": "string",\
"blockId": "string",\
"value": 0,\
"index": 0,\
"globalIndex": 0,\
"creationHeight": 0,\
"settlementHeight": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"},\
"spentTransactionId": "string",\
"mainChain": true}],\
"size": 0}],
"total": 0}`

## getApiV1Tokens

##### query Parameters

|     |     |
| --- | --- |
| offset | integer >= 0 |
| limit | integer \[ 1 .. 500 \] |
| sortDirection | string |
| hideNfts | boolean<br>Default: false<br>Exclude NFTs from result set |

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| items | Array of objects (TransactionInfo) <br>Items in selection |
| total<br>required | integer<br>Total qty of items |

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/tokens

https://api.ergoplatform.com/api/v1/tokens

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"items":
[\
{\
"id": "string",\
"blockId": "string",\
"inclusionHeight": 0,\
"timestamp": 0,\
"index": 0,\
"globalIndex": 0,\
"numConfirmations": 0,\
"inputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"spendingProof": "string",\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"outputGlobalIndex": 0,\
"outputCreatedAt": 0,\
"outputSettledAt": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"dataInputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"ergoTree": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"outputs":\
[\
{\
"boxId": "string",\
"transactionId": "string",\
"blockId": "string",\
"value": 0,\
"index": 0,\
"globalIndex": 0,\
"creationHeight": 0,\
"settlementHeight": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"},\
"spentTransactionId": "string",\
"mainChain": true}],\
"size": 0}],
"total": 0}`

## getApiV1TokensSearch

Search by ID or Symbol of an asset. Note that symbols aren't unique.

##### query Parameters

|     |     |
| --- | --- |
| query<br>required | string >= 3 characters |
| offset | integer >= 0 |
| limit | integer \[ 1 .. 500 \] |

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| items | Array of objects (TransactionInfo) <br>Items in selection |
| total<br>required | integer<br>Total qty of items |

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/tokens/search

https://api.ergoplatform.com/api/v1/tokens/search

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"items":
[\
{\
"id": "string",\
"blockId": "string",\
"inclusionHeight": 0,\
"timestamp": 0,\
"index": 0,\
"globalIndex": 0,\
"numConfirmations": 0,\
"inputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"spendingProof": "string",\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"outputGlobalIndex": 0,\
"outputCreatedAt": 0,\
"outputSettledAt": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"dataInputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"ergoTree": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"outputs":\
[\
{\
"boxId": "string",\
"transactionId": "string",\
"blockId": "string",\
"value": 0,\
"index": 0,\
"globalIndex": 0,\
"creationHeight": 0,\
"settlementHeight": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"},\
"spentTransactionId": "string",\
"mainChain": true}],\
"size": 0}],
"total": 0}`

## getApiV1TokensBysymbolP1

Get all assets with a given Symbol. Note that symbols aren't unique.

##### path Parameters

|     |     |
| --- | --- |
| p1<br>required | string |

### Responses

**200**

##### Response Schema: application/json

Array

|     |     |
| --- | --- |
| id<br>required | string<br>ID of the asset |
| boxId<br>required | string<br>Box ID this asset was issued by |
| emissionAmount<br>required | integer <int64> <br>Number of decimal places |
| name | string<br>Name of the asset |
| description | string<br>Description of the asset |
| type | string<br>Asset type (token standard) |
| decimals | integer<br>Number of decimal places |

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/tokens/bySymbol/{p1}

https://api.ergoplatform.com/api/v1/tokens/bySymbol/{p1}

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
[\
{\
"id": "string",\
"boxId": "string",\
"emissionAmount": 0,\
"name": "string",\
"description": "string",\
"type": "string",\
"decimals": 0}]`

## getApiV1TokensP1

##### path Parameters

|     |     |
| --- | --- |
| p1<br>required | string |

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| id<br>required | string<br>ID of the asset |
| boxId<br>required | string<br>Box ID this asset was issued by |
| emissionAmount<br>required | integer <int64> <br>Number of decimal places |
| name | string<br>Name of the asset |
| description | string<br>Description of the asset |
| type | string<br>Asset type (token standard) |
| decimals | integer<br>Number of decimal places |

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/tokens/{p1}

https://api.ergoplatform.com/api/v1/tokens/{p1}

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"id": "string",
"boxId": "string",
"emissionAmount": 0,
"name": "string",
"description": "string",
"type": "string",
"decimals": 0}`

## getApiV1Assets  Deprecated

Use '/tokens' instead

##### query Parameters

|     |     |
| --- | --- |
| offset | integer >= 0 |
| limit | integer \[ 1 .. 500 \] |
| sortDirection | string |
| hideNfts | boolean<br>Default: false<br>Exclude NFTs from result set |

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| items | Array of objects (TransactionInfo) <br>Items in selection |
| total<br>required | integer<br>Total qty of items |

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/assets

https://api.ergoplatform.com/api/v1/assets

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"items":
[\
{\
"id": "string",\
"blockId": "string",\
"inclusionHeight": 0,\
"timestamp": 0,\
"index": 0,\
"globalIndex": 0,\
"numConfirmations": 0,\
"inputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"spendingProof": "string",\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"outputGlobalIndex": 0,\
"outputCreatedAt": 0,\
"outputSettledAt": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"dataInputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"ergoTree": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"outputs":\
[\
{\
"boxId": "string",\
"transactionId": "string",\
"blockId": "string",\
"value": 0,\
"index": 0,\
"globalIndex": 0,\
"creationHeight": 0,\
"settlementHeight": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"},\
"spentTransactionId": "string",\
"mainChain": true}],\
"size": 0}],
"total": 0}`

## getApiV1AssetsSearchBytokenid

##### query Parameters

|     |     |
| --- | --- |
| query<br>required | string >= 5 characters |
| offset | integer >= 0 |
| limit | integer \[ 1 .. 500 \] |

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| items | Array of objects (TransactionInfo) <br>Items in selection |
| total<br>required | integer<br>Total qty of items |

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/assets/search/byTokenId

https://api.ergoplatform.com/api/v1/assets/search/byTokenId

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"items":
[\
{\
"id": "string",\
"blockId": "string",\
"inclusionHeight": 0,\
"timestamp": 0,\
"index": 0,\
"globalIndex": 0,\
"numConfirmations": 0,\
"inputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"spendingProof": "string",\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"outputGlobalIndex": 0,\
"outputCreatedAt": 0,\
"outputSettledAt": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"dataInputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"ergoTree": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"outputs":\
[\
{\
"boxId": "string",\
"transactionId": "string",\
"blockId": "string",\
"value": 0,\
"index": 0,\
"globalIndex": 0,\
"creationHeight": 0,\
"settlementHeight": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"},\
"spentTransactionId": "string",\
"mainChain": true}],\
"size": 0}],
"total": 0}`

## getApiV1EpochsParams

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| height<br>required | integer |
| storageFeeFactor<br>required | integer |
| minValuePerByte<br>required | integer |
| maxBlockSize<br>required | integer |
| maxBlockCost<br>required | integer |
| blockVersion<br>required | integer |
| tokenAccessCost<br>required | integer |
| inputCost<br>required | integer |
| dataInputCost<br>required | integer |
| outputCost<br>required | integer |

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/epochs/params

https://api.ergoplatform.com/api/v1/epochs/params

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"height": 0,
"storageFeeFactor": 0,
"minValuePerByte": 0,
"maxBlockSize": 0,
"maxBlockCost": 0,
"blockVersion": 0,
"tokenAccessCost": 0,
"inputCost": 0,
"dataInputCost": 0,
"outputCost": 0}`

## getApiV1AddressesP1Transactions

##### path Parameters

|     |     |
| --- | --- |
| p1<br>required | string |

##### query Parameters

|     |     |
| --- | --- |
| offset | integer >= 0 |
| limit | integer \[ 1 .. 500 \] |
| concise | boolean<br>Default: false<br>Display only address inputs/outputs in transaction |
| fromHeight | integer >= 0 |
| toHeight | integer >= 1 |

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| items | Array of objects (TransactionInfo) <br>Items in selection |
| total<br>required | integer<br>Total qty of items |

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/addresses/{p1}/transactions

https://api.ergoplatform.com/api/v1/addresses/{p1}/transactions

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"items":
[\
{\
"id": "string",\
"blockId": "string",\
"inclusionHeight": 0,\
"timestamp": 0,\
"index": 0,\
"globalIndex": 0,\
"numConfirmations": 0,\
"inputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"spendingProof": "string",\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"outputGlobalIndex": 0,\
"outputCreatedAt": 0,\
"outputSettledAt": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"dataInputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"ergoTree": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"outputs":\
[\
{\
"boxId": "string",\
"transactionId": "string",\
"blockId": "string",\
"value": 0,\
"index": 0,\
"globalIndex": 0,\
"creationHeight": 0,\
"settlementHeight": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"},\
"spentTransactionId": "string",\
"mainChain": true}],\
"size": 0}],
"total": 0}`

## getApiV1AddressesP1BalanceConfirmed

##### path Parameters

|     |     |
| --- | --- |
| p1<br>required | string |

##### query Parameters

|     |     |
| --- | --- |
| minConfirmations | integer |

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| nanoErgs<br>required | integer <int64> <br>Ergo balance |
| tokens | Array of objects (TokenAmount) <br>Tokens balances |

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/addresses/{p1}/balance/confirmed

https://api.ergoplatform.com/api/v1/addresses/{p1}/balance/confirmed

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"nanoErgs": 0,
"tokens":
[\
{\
"tokenId": "string",\
"amount": 0,\
"decimals": 0,\
"name": "string",\
"tokenType": "string"}]}`

## getApiV1AddressesP1BalanceTotal

##### path Parameters

|     |     |
| --- | --- |
| p1<br>required | string |

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| confirmed<br>required | object (Balance) |
| unconfirmed<br>required | object (Balance) |

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/addresses/{p1}/balance/total

https://api.ergoplatform.com/api/v1/addresses/{p1}/balance/total

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"confirmed":
{
"nanoErgs": 0,
"tokens":
[\
{\
"tokenId": "string",\
"amount": 0,\
"decimals": 0,\
"name": "string",\
"tokenType": "string"}]},
"unconfirmed":
{
"nanoErgs": 0,
"tokens":
[\
{\
"tokenId": "string",\
"amount": 0,\
"decimals": 0,\
"name": "string",\
"tokenType": "string"}]}}`

## getApiV1Blocks

##### query Parameters

|     |     |
| --- | --- |
| offset | integer >= 0 |
| limit | integer \[ 1 .. 500 \] |
| sortBy | string |
| sortDirection | string |

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| items | Array of objects (TransactionInfo) <br>Items in selection |
| total<br>required | integer<br>Total qty of items |

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/blocks

https://api.ergoplatform.com/api/v1/blocks

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"items":
[\
{\
"id": "string",\
"blockId": "string",\
"inclusionHeight": 0,\
"timestamp": 0,\
"index": 0,\
"globalIndex": 0,\
"numConfirmations": 0,\
"inputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"spendingProof": "string",\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"outputGlobalIndex": 0,\
"outputCreatedAt": 0,\
"outputSettledAt": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"dataInputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"ergoTree": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"outputs":\
[\
{\
"boxId": "string",\
"transactionId": "string",\
"blockId": "string",\
"value": 0,\
"index": 0,\
"globalIndex": 0,\
"creationHeight": 0,\
"settlementHeight": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"},\
"spentTransactionId": "string",\
"mainChain": true}],\
"size": 0}],
"total": 0}`

## getApiV1BlocksP1

##### path Parameters

|     |     |
| --- | --- |
| p1<br>required | string |

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| block<br>required | object (FullBlockInfo) <br>Full block info |
| references<br>required | object (BlockReferencesInfo) <br>References to previous and next (if exists) blocks |

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/blocks/{p1}

https://api.ergoplatform.com/api/v1/blocks/{p1}

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"block":
{
"header":
{
"id": "string",
"parentId": "string",
"version": 0,
"height": 0,
"epoch": 0,
"difficulty": "string",
"adProofsRoot": "string",
"stateRoot": "string",
"transactionsRoot": "string",
"timestamp": 0,
"nBits": 0,
"size": 0,
"extensionHash": "string",
"powSolutions":
{
"pk": "string",
"w": "string",
"n": "string",
"d": "string"},
"votes":
{
"_1": 0,
"_2": 0,
"_3": 0}},
"blockTransactions":
[\
{\
"id": "string",\
"headerId": "string",\
"inclusionHeight": 0,\
"timestamp": 0,\
"index": 0,\
"confirmationsCount": 0,\
"inputs":\
[\
{\
"id": "string",\
"value": 0,\
"index": 0,\
"spendingProof": "string",\
"transactionId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"address": "string"}],\
"dataInputs":\
[\
{\
"id": "string",\
"value": 0,\
"index": 0,\
"transactionId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"address": "string"}],\
"outputs":\
[\
{\
"id": "string",\
"txId": "string",\
"value": 0,\
"index": 0,\
"creationHeight": 0,\
"ergoTree": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"},\
"spentTransactionId": "string",\
"mainChain": true}]}],
"extension":
{
"headerId": "string",
"digest": "string",
"fields":
{
"property1": "string",
"property2": "string"}},
"adProofs": "string"},
"references":
{
"previousId": "string",
"nextId": "string"}}`

## getApiV1BlocksHeaders

##### query Parameters

|     |     |
| --- | --- |
| offset | integer >= 0 |
| limit | integer \[ 1 .. 500 \] |
| sortBy | string |
| sortDirection | string |

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| items | Array of objects (TransactionInfo) <br>Items in selection |
| total<br>required | integer<br>Total qty of items |

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/blocks/headers

https://api.ergoplatform.com/api/v1/blocks/headers

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"items":
[\
{\
"id": "string",\
"blockId": "string",\
"inclusionHeight": 0,\
"timestamp": 0,\
"index": 0,\
"globalIndex": 0,\
"numConfirmations": 0,\
"inputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"spendingProof": "string",\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"outputGlobalIndex": 0,\
"outputCreatedAt": 0,\
"outputSettledAt": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"dataInputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"ergoTree": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"outputs":\
[\
{\
"boxId": "string",\
"transactionId": "string",\
"blockId": "string",\
"value": 0,\
"index": 0,\
"globalIndex": 0,\
"creationHeight": 0,\
"settlementHeight": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"},\
"spentTransactionId": "string",\
"mainChain": true}],\
"size": 0}],
"total": 0}`

## getApiV1BlocksByglobalindexStream

Get a stream of blocks ordered by global index (height)

##### query Parameters

|     |     |
| --- | --- |
| minGix<br>required | integer <int64>  >= 0 <br>Min global index (in blockchain) of an on-chain entity |
| limit<br>required | integer <= 500 |

### Responses

**200**

##### Response Schema: application/json

One of

- Nil
- BlockInfo

|
|

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/blocks/byGlobalIndex/stream

https://api.ergoplatform.com/api/v1/blocks/byGlobalIndex/stream

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Example

Nil

Copy
Expand all  Collapse all

`{ }`

## getApiV1BlocksStreamSummary

Get a stream of block summaries ordered by global index (height)

##### query Parameters

|     |     |
| --- | --- |
| offset | integer >= 0 |
| limit | integer \[ 1 .. 1536 \] |
| sortBy | string |
| sortDirection | string |

### Responses

**200**

##### Response Schema: application/json

One of

- Nil
- BlockSummaryV1

|
|

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/blocks/stream/summary

https://api.ergoplatform.com/api/v1/blocks/stream/summary

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Example

Nil

Copy
Expand all  Collapse all

`{ }`

## postApiV1MempoolTransactionsSubmit

##### Request Body schema: application/json

|
|

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| id<br>required | string<br>Id of submitted transaction |

**400**
Bad request

**404**
Not found

**default**
Unknown error

post/api/v1/mempool/transactions/submit

https://api.ergoplatform.com/api/v1/mempool/transactions/submit

### Request samples

- Payload

Content type

application/json

Copy
Expand all  Collapse all

`{ }`

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"id": "string"}`

## getApiV1MempoolTransactionsByaddressP1

##### path Parameters

|     |     |
| --- | --- |
| p1<br>required | string |

##### query Parameters

|     |     |
| --- | --- |
| offset | integer >= 0 |
| limit | integer \[ 1 .. 2147483647 \] |

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| items | Array of objects (TransactionInfo) <br>Items in selection |
| total<br>required | integer<br>Total qty of items |

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/mempool/transactions/byAddress/{p1}

https://api.ergoplatform.com/api/v1/mempool/transactions/byAddress/{p1}

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"items":
[\
{\
"id": "string",\
"blockId": "string",\
"inclusionHeight": 0,\
"timestamp": 0,\
"index": 0,\
"globalIndex": 0,\
"numConfirmations": 0,\
"inputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"spendingProof": "string",\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"outputGlobalIndex": 0,\
"outputCreatedAt": 0,\
"outputSettledAt": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"dataInputs":\
[\
{\
"boxId": "string",\
"value": 0,\
"index": 0,\
"outputBlockId": "string",\
"outputTransactionId": "string",\
"outputIndex": 0,\
"ergoTree": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"}}],\
"outputs":\
[\
{\
"boxId": "string",\
"transactionId": "string",\
"blockId": "string",\
"value": 0,\
"index": 0,\
"globalIndex": 0,\
"creationHeight": 0,\
"settlementHeight": 0,\
"ergoTree": "string",\
"ergoTreeConstants": "string",\
"ergoTreeScript": "string",\
"address": "string",\
"assets":\
[\
{\
"tokenId": "string",\
"index": 0,\
"amount": 0,\
"name": "string",\
"decimals": 0,\
"type": "string"}],\
"additionalRegisters":\
{\
"property1": "string",\
"property2": "string"},\
"spentTransactionId": "string",\
"mainChain": true}],\
"size": 0}],
"total": 0}`

## getApiV1MempoolBoxesUnspent

Get a stream of unspent outputs

### Responses

**200**

##### Response Schema: application/json

One of

- Nil
- OutputInfo

|
|

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/mempool/boxes/unspent

https://api.ergoplatform.com/api/v1/mempool/boxes/unspent

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Example

Nil

Copy
Expand all  Collapse all

`{ }`

## getApiV1Info  Deprecated

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| lastBlockId<br>required | string<br>Modifier ID |
| height<br>required | integer |
| maxBoxGix<br>required | integer <int64> |
| maxTxGix<br>required | integer <int64> |
| params<br>required | object (EpochInfo) |

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/info

https://api.ergoplatform.com/api/v1/info

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"lastBlockId": "string",
"height": 0,
"maxBoxGix": 0,
"maxTxGix": 0,
"params":
{
"height": 0,
"storageFeeFactor": 0,
"minValuePerByte": 0,
"maxBlockSize": 0,
"maxBlockCost": 0,
"blockVersion": 0,
"tokenAccessCost": 0,
"inputCost": 0,
"dataInputCost": 0,
"outputCost": 0}}`

## getApiV1Networkstate

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| lastBlockId<br>required | string<br>Modifier ID |
| height<br>required | integer |
| maxBoxGix<br>required | integer <int64> |
| maxTxGix<br>required | integer <int64> |
| params<br>required | object (EpochInfo) |

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/networkState

https://api.ergoplatform.com/api/v1/networkState

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"lastBlockId": "string",
"height": 0,
"maxBoxGix": 0,
"maxTxGix": 0,
"params":
{
"height": 0,
"storageFeeFactor": 0,
"minValuePerByte": 0,
"maxBlockSize": 0,
"maxBlockCost": 0,
"blockVersion": 0,
"tokenAccessCost": 0,
"inputCost": 0,
"dataInputCost": 0,
"outputCost": 0}}`

## getApiV1Networkstats

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| uniqueAddressesNum<br>required | integer <int64> |

**400**
Bad request

**404**
Not found

**default**
Unknown error

get/api/v1/networkStats

https://api.ergoplatform.com/api/v1/networkStats

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"uniqueAddressesNum": 0}`

## postApiV1ErgotreeConvert

##### Request Body schema: application/json

|     |     |
| --- | --- |
| hashed<br>required | string<br>Hashed value of ergo script |

### Responses

**200**

##### Response Schema: application/json

|     |     |
| --- | --- |
| constants<br>required | string<br>Constants use in ergo script |
| script<br>required | string<br>Human readable ergo script |

**400**
Bad request

**404**
Not found

**default**
Unknown error

post/api/v1/ergotree/convert

https://api.ergoplatform.com/api/v1/ergotree/convert

### Request samples

- Payload

Content type

application/json

Copy
Expand all  Collapse all

`
{
"hashed": "string"}`

### Response samples

- 200
- 400
- 404
- default

Content type

application/json

Copy
Expand all  Collapse all

`
{
"constants": "string",
"script": "string"}`