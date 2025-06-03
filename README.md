# JsonWalker

_Allows simple, quick, and easy parsing of nasty nested JSON through a fluent object-oriented tool to avoid hours of pain_

JsonWalker's goal is to allow users to specify a path through nested JSON using a chainable, discoverable API, and get the items at each match in the JSON. The library uses generators to efficiently traverse large data structures.

## Installation

JsonWalker is a pip installable package. It is a public package, and will thus not need any special permissions to install.

### Command Line Installation

To install from the command line, simply do `pip install JsonWalker`.

### Use in other pip packages

As this is a public package, it can be added to the required packages of any pip installable packages and will be installed automatically when those are installed in other projects.

## Usage

To use this in a project, install using one of the installation methods shown above.

Import the JsonPath class into your file: `from JsonWalker.walk import JsonPath`

As the walk command makes a generator, it can be used in multiple ways.

```json
{
  'users': [
    {
      'name': 'samantha',
      'points': 2394729
    },
    {
      'name': 'john',
      'points': 2392987
    }
  ]
}
```

### Use in a for loop

```python
path = JsonPath().key("users").listAll().key("name")
for name in path.walk(data):
    ...
```

### Use outside of a for loop

```python
path = JsonPath().key("users").listAll().key("name")
name = next(path.walk(data))
```

The next function is a Python function that gets the "next" value in the generator, and can be called multiple times in a row if desired.

## Quick Start Examples

Here are some practical examples to get you started quickly:

### Example 1: Simple Key Access with Defaults

```python
from JsonWalker.walk import JsonPath

# Sample data with missing keys
data = {
    "key1": [
        {
            "key2": 100
        },
        {}  # key2 is missing here, so contextOfKey1 will be blank, and the default value for key2 will be used
    ]
}

path = JsonPath().key("key1").listAll().addContext().key("key2", default=-1)
for contextOfKey1, key2 in path.walk(data):
    print(f"contextOfKey1: {contextOfKey1}, valueOfKey2: {key2}")
```

Output:
```
contextOfKey1: {'key2': 100}, valueOfKey2: 100
contextOfKey1: {}, valueOfKey2: -1
```

### Example 2: Multi-Value Return

```python
from JsonWalker.walk import JsonPath

# Sample data
data = {
    "key1": {
        "key2": {
            "itemA": "hello",
            "itemB": "world",
            "itemC": "I use Arch, by the way"  # Nobody wants this
        }
    }
}

path = JsonPath().key("key1").addContext().key("key2").multi(
    JsonPath().key("itemA"),
    JsonPath().key("itemB")
)

# If you removed .addContext(), key1Context would not be part of this line
# and everything else would stay the same
for key1Context, itemA, itemB in path.walk(data):
    print(f"{itemA} {itemB}!")
    print(key1Context)
```

Output:
```
hello world!
{'key2': {'itemA': 'hello', 'itemB': 'world', 'itemC': 'I use Arch, by the way'}}
```

### Example 3: Dictionary Iteration

```python
from JsonWalker.walk import JsonPath

# Sample data
data = {
    "key1": {
        "key2": "value2",
        "key3": "value3",
        "key4": "value4"
    }
}

path = JsonPath().key("key1").keyContextAndValue()
for key, value in path.walk(data):
    print(f"{key} -- {value}")
```

Output:
```
key2 -- value2
key3 -- value3
key4 -- value4
```

## Understanding Context

**Context** is one of JsonWalker's most powerful features. It allows you to collect and preserve intermediate values as you traverse through nested JSON structures.

### How Context Works

- Context is a list that accumulates values as you traverse the JSON
- When you reach the end of a path, you get back either:
  - Just the final value (if no context was collected)
  - A list containing `[context_values..., final_value]` (if context was collected)
- Context is particularly useful when you need to know "where you came from" or want to collect multiple related values

### Context Collection Methods

- `.addContext()` - Adds the current value to the context before continuing
- `.keyContextAndValue()` - When iterating through dictionary items, adds just the key's string to the context, rather than the whole dictionary object
- `.multi()` - Collects values from multiple sub-paths and includes them in the result

### Simple Context Example

```python
from JsonWalker.walk import JsonPath

data = {
    "users": [
        {"name": "John", "age": 30},
        {"name": "Jane", "age": 25}
    ]
}

# Without context - just get names
path = JsonPath().key("users").listAll().key("name")
for name in path.walk(data):
    print(name)
print()

# With context - get both user object and name
path = JsonPath().key("users").listAll().addContext().key("name")
for user, name in path.walk(data):
    print(f"{name} has age {user['age']}")
```

Output
```
John
Jane

John has age 30
Jane has age 25
```

## API Reference

JsonWalker uses a fluent, chainable API that makes queries self-documenting and discoverable through IDE autocompletion.

### Core

| Core | Description |
|--------|-------------|
| `JsonPath()` | Start a new JSON path query chain |
| `.walk(data)` | Execute the path query on JSON data as a Generator (gets all the data WHEN you want it, making walk lightning fast)|

### Path Building Methods

| Method | Description | Example |
|--------|-------------|---------|
| `.key(name, default=None)` | Access dictionary by key with optional default if the key is not found | `.key("users")` |
| `.listIndex(idx)` | Access list by specific index (supports negative indices) | `.listIndex(0)` or `.listIndex(-1)` |
| `.listSlice(start, end)` | Access range of list items | `.listSlice(1, 5)` |
| `.listAll()` | Access all items in a list | `.listAll()` |
| `.keyContextAndValue()` | Iterate through key-value pairs of dictionaries, adding keys to context | `.keyContextAndValue()` |
| `.addContext()` | Add the current value to the context before continuing | `.addContext()` |
| `.multi(*paths)` | Create diverging paths from the current context, returning all possible combinations of values | `.multi(path1, path2)` |

## Complete Examples

All examples below include the necessary imports and sample data so you can copy and run them immediately.

### Simple Key Access

```python
from JsonWalker.walk import JsonPath

# Sample data
data = {
    "user": {
        "name": "John",
        "age": 30
    }
}

# Access user's name
path = JsonPath().key("user").key("name")
for name in path.walk(data):
    print(name)
```

Output
```
John
```


### List Iteration with Context

```python
from JsonWalker.walk import JsonPath

# Sample data
data = {
    "users": [
        {"name": "John", "age": 30},
        {"name": "Jane", "age": 25}
    ]
}

# Iterate through all users, keeping user object as context
path = JsonPath().key("users").listAll().addContext().key("name", default="Unknown")
for user, name in path.walk(data):
    print(f"{name} is part of the user dictionary - {user}")
```

Output:
```
John is part of the user dictionary - {'name': 'John', 'age': 30}
Jane is part of the user dictionary - {'name': 'Jane', 'age': 25}
```

### Multi-Value Return

```python
from JsonWalker.walk import JsonPath

# Sample data
data = {
    "users": [
        {
            "profile": {
                "firstName": "John",
                "lastName": "Doe"
            }
        },
        {
            "profile": {
                "firstName": "Kaladin",
                "lastName": "Stormblessed"
            }
        }
    ]
}

# Get both first and last name in one query
path = JsonPath().key("users").listAll().key("profile").multi(
    JsonPath().key("firstName"),
    JsonPath().key("lastName")
)
for firstName, lastName in path.walk(data):
    print(f"{firstName} {lastName}")
```

Output
```
John Doe
Kaladin Stormblessed
```

### Dictionary Iteration with Context

```python
from JsonWalker.walk import JsonPath

# Sample data
data = {
    "scores": {
        "math": 95,
        "science": 87,
        "english": 92
    }
}

# Iterate through all key-value pairs
path = JsonPath().key("scores").keyContextAndValue()
for subject, score in path.walk(data):
    print(f"{subject}: {score}")
```

Output:
```
math: 95
science: 87
english: 92
```

### Range and Slice Operations

```python
from JsonWalker.walk import JsonPath

# Sample data
data = {
    "numbers": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
}

# Get numbers from index 2 to 5 (exclusive)
list1 = []
path = JsonPath().key("numbers").listSlice(2, 6)
for num in path.walk(data):
    list1.append(num)
print(list1)

# Get the last 3 numbers
list2 = []
path = JsonPath().key("numbers").listSlice(-3, None)
for num in path.walk(data):
    list2.append(num)
print(list2)
```

Output
```
[2, 3, 4, 5]
[7, 8, 9]
```

### Complex Nested Data with Added Context

```python
from JsonWalker.walk import JsonPath

# Sample data
data = {
    "departments": [
        {
            "name": "Engineering",
            "employees": [
                {"name": "Alice", "skills": ["Python", "JavaScript"]},
                {"name": "Bob", "skills": ["Java", "C++"]}
            ]
        },
        {
            "name": "Marketing", 
            "employees": [
                {"name": "Charlie", "skills": ["SEO", "Analytics"]}
            ]
        }
    ]
}

# Get all employee names with their department and skills
# This demonstrates nested context collection
path = (JsonPath()
    .key("departments")
    .listAll()
    .addContext()  # Keep department info in context
    .key("employees")
    .listAll()
    .multi(
        JsonPath().key("name"),
        JsonPath().key("skills").listAll()
    )
)

# The whole department dictionary is stored as context, which is why we can access its 'name' key
for dept, name, skill in path.walk(data):
    print(f"{name} from {dept['name']} knows {skill}")
```

Output:
```
Alice from Engineering knows Python
Alice from Engineering knows JavaScript
Bob from Engineering knows Java
Bob from Engineering knows C++
Charlie from Marketing knows SEO
Charlie from Marketing knows Analytics
```

### Real-World Example: Processing Complex API Response

```python
from JsonWalker.walk import JsonPath

# Sample data (complex nested structure like from an API)
apiResponse = {
    "persons": [
        {
            "id": "123",
            "names": [
                {
                    "nameForms": [
                        {
                            "parts": [
                                {
                                    "fields": [
                                        {
                                            "values": [
                                                {"labelId": "PR_GIVEN", "value": "John"}
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ],
            "links": {
                "persona": {
                    "href": "https://example.com/personas/456"
                }
            }
        }
    ]
}

# Extract person info with complex nested structure
person_path = JsonPath().key("persons").listAll().addContext().multi(
    JsonPath().key("id"),
    JsonPath().key("links").key("persona").key("href", default="")
)

for person, person_id, href in person_path.walk(apiResponse):
    print(f"Processing person {person_id} with href: {href}")
    
    # Get label IDs from deeply nested structure
    label_path = (JsonPath()
        .key("names")
        .listAll()
        .key("nameForms")
        .listAll()
        .key("parts")
        .listAll()
        .key("fields")
        .listAll()
        .key("values")
        .listAll()
        .key("labelId", default="")
    )
    
    for labelID in label_path.walk(person):
        if 'PR' in labelID and 'FTHR' not in labelID and 'MTHR' not in labelID:
            print(f"Found person {person_id} with label {labelID}")
```

Output
```
Found person 123 with label PR_GIVEN
```

### Using Single Values with next()

```python
from JsonWalker.walk import JsonPath

# Sample data
data = {
    "users": [
        {"name": "John", "age": 30},
        {"name": "Jane", "age": 25}
    ]
}

# Get just the first user's name
path = JsonPath().key("users").listIndex(0).key("name")
result = next(path.walk(data))
print(f"First user's name: {result}")

# Get the last user's age
path = JsonPath().key("users").listIndex(-1).key("age")
result = next(path.walk(data))
print(f"Last user's age: {result}")
```

Output:
```
First user's name: John
Last user's age: 25
```

### Handling Missing Keys with Defaults

```python
from JsonWalker.walk import JsonPath

# Sample data with missing fields
data = {
    "users": [
        {"name": "John", "age": 30},
        {"name": "Jane"},  # Missing age
        {"age": 40}        # Missing name
    ]
}

# Access with defaults for missing keys
path = JsonPath().key("users").listAll().addContext().multi(
    JsonPath().key("name", default="unknown_name"),
    JsonPath().key("age", default=-1)
)

for user, name, age in path.walk(data):
    print(f"{name} is {age} years old")
```

Output:
```
John is 30 years old
Jane is -1 years old
unknown_name is 40 years old
```

### Real World Example: Two different paths
As you can see in the data below, the subcategory of electronics contains multiple sections, which have the items we are looking for.
On the other hand, the subcategory of books does NOT have any sections, and just contains the books themselves. This is a great example of how real world data can be messy, but consistent. On the bright side, JsonWalker can handle this with two different paths.
```python
# Sample data with nested categories
data = {
    "categories": {
        "electronics": {
            "computers": {
                "laptops": ["MacBook", "ThinkPad", "Dell XPS"],
                "desktops": ["iMac", "HP Pavilion"]
            },
            "phones": {
                "smartphones": ["iPhone", "Samsung Galaxy"]
            }
        },
        "books": ["The Way of Kings", "To Kill a Mockingbird", "Dragonsbane", "Number the Stars"]
    }
}

path = JsonPath().key('categories').key('electronics').keyContextAndValue().keyContextAndValue().listAll()
for subcategory, section, item in path.walk(data):
    print(item)

path = JsonPath().key('categories').key('books').listAll()
for item in path.walk(data):
    print(item)

```

Output:
```
MacBook
ThinkPad
Dell XPS
iMac
HP Pavilion
iPhone
Samsung Galaxy
The Way of Kings
To Kill a Mockingbird
Dragonsbane
Number the Stars
```

## Key Features

1. **Generator-based**: Efficient memory usage for large datasets
2. **Chainable API**: Build complex queries step by step
3. **Context preservation**: Keep intermediate values during traversal with multiple context collection strategies
4. **Type-safe defaults**: Specify fallback values with proper types
5. **Multi-value queries**: Extract multiple values in a single traversal
6. **Flexible indexing**: Support for positive/negative indices and slicing
7. **Dictionary iteration**: Built-in support for key-value pair traversal with context

## Context System Benefits

1. **Relationship Preservation**: Keep track of parent-child relationships in nested data
2. **Multi-level Data Collection**: Gather information from different nesting levels in one pass
3. **Flexible Output**: Choose exactly what information you need from each level
4. **Memory Efficient**: Context is only collected when explicitly requested

## Best Practices

1. **Use meaningful variable names**: The fluent API makes it easy to create readable code
2. **Chain operations logically**: Group related operations together
3. **Leverage context strategically**: Use `.addContext()` when you need parent information, `.keyContextAndValue()` for dictionary keys
4. **Provide defaults**: Use the `default` parameter to handle missing keys gracefully
5. **Break complex queries**: Split very long chains into intermediate variables for readability
6. **Understand context flow**: Remember that context accumulates - each `.addContext()` or `.keyContextAndValue()` adds to your result tuple