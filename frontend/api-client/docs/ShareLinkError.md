
# ShareLinkError

Error body when share link creation validation fails.

## Properties

Name | Type
------------ | -------------
`detail` | string

## Example

```typescript
import type { ShareLinkError } from ''

// TODO: Update the object below with actual values
const example = {
  "detail": null,
} satisfies ShareLinkError

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ShareLinkError
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


