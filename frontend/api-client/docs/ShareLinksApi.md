# ShareLinksApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**shareLinksCreate**](ShareLinksApi.md#sharelinkscreate) | **POST** /api/share-links/ | Create share link |
| [**shareLinksRetrieve**](ShareLinksApi.md#sharelinksretrieve) | **GET** /api/share-links/{id}/ | Get image via share link |



## shareLinksCreate

> ShareLinkCreateResponse shareLinksCreate(shareLinkCreate)

Create share link

Creates a &#x60;Share_Link&#x60; for the given image. Expiry is computed from now plus &#x60;expiry_seconds&#x60;.

### Example

```ts
import {
  Configuration,
  ShareLinksApi,
} from '';
import type { ShareLinksCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure HTTP basic authorization: basicAuth
    username: "YOUR USERNAME",
    password: "YOUR PASSWORD",
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new ShareLinksApi(config);

  const body = {
    // ShareLinkCreate
    shareLinkCreate: ...,
  } satisfies ShareLinksCreateRequest;

  try {
    const data = await api.shareLinksCreate(body);
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
| **shareLinkCreate** | [ShareLinkCreate](ShareLinkCreate.md) |  | |

### Return type

[**ShareLinkCreateResponse**](ShareLinkCreateResponse.md)

### Authorization

[basicAuth](../README.md#basicAuth), [cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`, `application/x-www-form-urlencoded`, `multipart/form-data`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Share link was created. |  -  |
| **400** | Invalid request body or unknown image id. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## shareLinksRetrieve

> shareLinksRetrieve(id)

Get image via share link

Redirects to the image URL referenced by this share link. The path &#x60;id&#x60; is the share link id, not the image id. Responds with 404 if the link does not exist or &#x60;expiry&#x60; is in the past.

### Example

```ts
import {
  Configuration,
  ShareLinksApi,
} from '';
import type { ShareLinksRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure HTTP basic authorization: basicAuth
    username: "YOUR USERNAME",
    password: "YOUR PASSWORD",
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new ShareLinksApi(config);

  const body = {
    // number | A unique integer value identifying this share_ link.
    id: 56,
  } satisfies ShareLinksRetrieveRequest;

  try {
    const data = await api.shareLinksRetrieve(body);
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
| **id** | `number` | A unique integer value identifying this share_ link. | [Defaults to `undefined`] |

### Return type

`void` (Empty response body)

### Authorization

[basicAuth](../README.md#basicAuth), [cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **302** | Redirects to the shared image URL. |  -  |
| **404** | Unknown share link, or the link has expired. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

