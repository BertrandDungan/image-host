# ImagesApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**imagesRetrieve**](ImagesApi.md#imagesretrieve) | **GET** /api/images/ | List image URLs by user and size |
| [**imagesUpdate**](ImagesApi.md#imagesupdate) | **PUT** /api/images/ | Upload image |



## imagesRetrieve

> ImageGetUrlsResponse imagesRetrieve(imageSize, userId)

List image URLs by user and size

Returns absolute URLs for all images owned by the user at the given size. Medium thumbnails and originals require Premium or Enterprise.

### Example

```ts
import {
  Configuration,
  ImagesApi,
} from '';
import type { ImagesRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure HTTP basic authorization: basicAuth
    username: "YOUR USERNAME",
    password: "YOUR PASSWORD",
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new ImagesApi(config);

  const body = {
    // '200' | '400' | 'original' | Variant size key (matches `ImageSize`).
    imageSize: imageSize_example,
    // number | Owner user ID.
    userId: 56,
  } satisfies ImagesRetrieveRequest;

  try {
    const data = await api.imagesRetrieve(body);
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
| **imageSize** | `200`, `400`, `original` | Variant size key (matches &#x60;ImageSize&#x60;). | [Defaults to `undefined`] [Enum: 200, 400, original] |
| **userId** | `number` | Owner user ID. | [Defaults to `undefined`] |

### Return type

[**ImageGetUrlsResponse**](ImageGetUrlsResponse.md)

### Authorization

[basicAuth](../README.md#basicAuth), [cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Matching image URLs (may be empty). |  -  |
| **400** | Missing or invalid query parameters, or unknown user. |  -  |
| **403** | Account tier does not allow this image size. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## imagesUpdate

> imagesUpdate(userId, filename, image)

Upload image

Multipart upload that creates three &#x60;Image&#x60; objects (small thumbnail, medium thumbnail, and original)

### Example

```ts
import {
  Configuration,
  ImagesApi,
} from '';
import type { ImagesUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure HTTP basic authorization: basicAuth
    username: "YOUR USERNAME",
    password: "YOUR PASSWORD",
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new ImagesApi(config);

  const body = {
    // number | ID of the user who will own the uploaded image.
    userId: 56,
    // string
    filename: filename_example,
    // Blob | Image file. Only PNG and JPEG are accepted.
    image: BINARY_DATA_HERE,
  } satisfies ImagesUpdateRequest;

  try {
    const data = await api.imagesUpdate(body);
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
| **userId** | `number` | ID of the user who will own the uploaded image. | [Defaults to `undefined`] |
| **filename** | `string` |  | [Defaults to `undefined`] |
| **image** | `Blob` | Image file. Only PNG and JPEG are accepted. | [Defaults to `undefined`] |

### Return type

`void` (Empty response body)

### Authorization

[basicAuth](../README.md#basicAuth), [cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `multipart/form-data`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | Three image variants were stored successfully. |  -  |
| **400** | Input validation failure. Failure reason is under &#x60;detail&#x60;  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

