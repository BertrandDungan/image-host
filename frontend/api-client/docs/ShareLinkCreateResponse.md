
# ShareLinkCreateResponse

Share link row as returned after create, including the GET URL for this link.

## Properties

Name | Type
------------ | -------------
`id` | number
`image` | number
`expiry` | Date
`url` | string

## Example

```typescript
import type { ShareLinkCreateResponse } from ''

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "image": null,
  "expiry": null,
  "url": null,
} satisfies ShareLinkCreateResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ShareLinkCreateResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


