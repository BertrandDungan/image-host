
# ShareLinkCreate

JSON body to create a time-limited share link for an image.

## Properties

Name | Type
------------ | -------------
`image` | number
`expirySeconds` | number

## Example

```typescript
import type { ShareLinkCreate } from ''

// TODO: Update the object below with actual values
const example = {
  "image": null,
  "expirySeconds": null,
} satisfies ShareLinkCreate

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ShareLinkCreate
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


