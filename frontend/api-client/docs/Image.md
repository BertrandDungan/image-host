
# Image


## Properties

Name | Type
------------ | -------------
`id` | number
`title` | string
`owner` | number
`image` | string
`size` | [SizeEnum](SizeEnum.md)

## Example

```typescript
import type { Image } from ''

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "title": null,
  "owner": null,
  "image": null,
  "size": null,
} satisfies Image

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as Image
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


