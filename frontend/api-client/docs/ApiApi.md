# ApiApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**apiUsersList**](ApiApi.md#apiuserslist) | **GET** /api/users/ |  |
| [**apiUsersRetrieve**](ApiApi.md#apiusersretrieve) | **GET** /api/users/{id}/ |  |



## apiUsersList

> Array&lt;User&gt; apiUsersList()



### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiUsersListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure HTTP basic authorization: basicAuth
    username: "YOUR USERNAME",
    password: "YOUR PASSWORD",
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new ApiApi(config);

  try {
    const data = await api.apiUsersList();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**Array&lt;User&gt;**](User.md)

### Authorization

[basicAuth](../README.md#basicAuth), [cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiUsersRetrieve

> User apiUsersRetrieve(id)



### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiUsersRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure HTTP basic authorization: basicAuth
    username: "YOUR USERNAME",
    password: "YOUR PASSWORD",
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new ApiApi(config);

  const body = {
    // number | A unique integer value identifying this user.
    id: 56,
  } satisfies ApiUsersRetrieveRequest;

  try {
    const data = await api.apiUsersRetrieve(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **id** | `number` | A unique integer value identifying this user. | [Defaults to `undefined`] |

### Return type

[**User**](User.md)

### Authorization

[basicAuth](../README.md#basicAuth), [cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

