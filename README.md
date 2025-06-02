# JsonWalker

_Allows simple, quick, and easy use of nested JSON with a fluent object-oriented parsing tool to avoid hours of pain_

JsonWalker's goal is to allow users to specify a path through nested JSON using a chainable, discoverable API, and get the items at each match in the JSON. The library uses generators to efficiently traverse large data structures.

## Installation

JsonWalker is a pip installable package. It is a public package, and will thus not need any special permissions to install.

### Command Line Installation

To install from the command line, simply do `pip install JsonWalker`.

### Use in other pip packages

As this is a public package, it can be added to the required packages of any pip installable packages and will be installed automatically when those are installed in other projects.

## Usage

To use this in a project, install using one of the installation methods shown above.

Import the jsonPath function into your file: `from JsonWalker.walk import jsonPath`

As the walk command makes a generator, it can be used in multiple ways.

### Use in a for loop

```python
for context1, context2, item1, item2 in jsonPath().key("users").all().addContext().key("name").walk(data):
    ...
```

### Use outside of a for loop

```python
result = next(jsonPath().key("users").index(0).key("name").walk(data))
```

The next function is a Python function that gets the "next" value in the generator, and can be called multiple times in a row if desired.

## API Reference

JsonWalker uses a fluent, chainable API that makes queries self-documenting and discoverable through IDE autocompletion.

### Core Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `jsonPath()` | Start a new JSON path query chain | `JsonPath` |
| `.walk(data)` | Execute the path query on JSON data | `Generator` |

### Path Building Methods

| Method | Description | Example |
|--------|-------------|---------|
| `.key(name, default=None)` | Access dictionary by key with optional default if the key is not found | `.key("users")` |
| `.index(idx)` | Access list by specific index (supports negative indices) | `.index(0)` or `.index(-1)` |
| `.slice(start, end)` | Access range of list items | `.slice(1, 5)` |
| `.all()` | Access all items in a list | `.all()` |
| `.items()` | Iterate through key-value pairs of dictionaries | `.items()` |
| `.addContext()` | Add additional path context | `.addContext()` |
| `.multi(*paths)` | Create diverging paths from the current context, each returning their own values. (It is generally best practice to avoid multi when paths are very far apart, or share only a small amount of original context) | `.multi(path1, path2)` |

## Complete Examples

All examples below include the necessary imports and sample data so you can copy and run them immediately.

### Simple Key Access

```python
from JsonWalker.walk import jsonPath

# Sample data
data = {
    "user": {
        "name": "John",
        "age": 30
    }
}

# Access user's name
path = jsonPath().key("user").key("name")
for name in path.walk(data):
    print(name)  # Output: John
```

### List Iteration with Context

```python
from JsonWalker.walk import jsonPath

# Sample data
data = {
    "users": [
        {"name": "John", "age": 30},
        {"name": "Jane", "age": 25}
    ]
}

# Iterate through all users, keeping user object as context
path = jsonPath().key("users").all().addContext().key("name", default="Unknown")
for user, name in path.walk(data):
    print(f"{name} is {user.get('age')} years old")
```

Output:
```
John is 30 years old
Jane is 25 years old
```

### Multi-Value Return

```python
from JsonWalker.walk import jsonPath

# Sample data
data = {
    "user": {
        "profile": {
            "firstName": "John",
            "lastName": "Doe"
        }
    }
}

# Get both first and last name in one query
path = jsonPath().key("user").key("profile").multi(
    jsonPath().key("firstName"),
    jsonPath().key("lastName")
)
for firstName, lastName in path.walk(data):
    print(f"{firstName} {lastName}")  # Output: John Doe
```

### Dictionary Iteration

```python
from JsonWalker.walk import jsonPath

# Sample data
data = {
    "scores": {
        "math": 95,
        "science": 87,
        "english": 92
    }
}

# Iterate through all key-value pairs
path = jsonPath().key("scores").items()
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
from JsonWalker.walk import jsonPath

# Sample data
data = {
    "numbers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
}

# Get numbers from index 2 to 5
path = jsonPath().key("numbers").slice(2, 6)
for num in path.walk(data):
    print(num)  # Output: 3, 4, 5, 6

print("---")

# Get the last 3 numbers
path = jsonPath().key("numbers").slice(-3, None)
for num in path.walk(data):
    print(num)  # Output: 8, 9, 10
```

### Complex Nested Data

```python
from JsonWalker.walk import jsonPath

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
path = (jsonPath()
    .key("departments")
    .all()
    .addContext()  # Keep department info
    .key("employees")
    .all()
    .addContext()  # Keep employee info
    .multi(
        jsonPath().key("name"),
        jsonPath().key("skills").all()
    )
)

for dept, employee, name, skill in path.walk(data):
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

### Real-World Example: Processing User Data

```python
from JsonWalker.walk import jsonPath

# Sample data (complex nested structure)
arkInfo = {
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
                                                {"labelId": "PR_GIVEN"}
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
        },
        {
            "id": "789",
            "names": [
                {
                    "nameForms": [
                        {
                            "parts": [
                                {
                                    "fields": [
                                        {
                                            "values": [
                                                {"labelId": "PR_SURNAME"},
                                                {"labelId": "PR_FTHR_GIVEN"}
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
                    "href": "https://example.com/personas/999"
                }
            }
        }
    ]
}

# Extract person info with complex nested structure
person_path = jsonPath().key("persons").all().addContext().multi(
    jsonPath().key("id"),
    jsonPath().key("links").key("persona").key("href", default="")
)

for person, person_id, href in person_path.walk(arkInfo):
    print(f"Processing person {person_id} with href: {href}")
    
    # Get label IDs from deeply nested structure
    label_path = (jsonPath()
        .key("names")
        .all()
        .key("nameForms")
        .all()
        .key("parts")
        .all()
        .key("fields")
        .all()
        .key("values")
        .all()
        .key("labelId", default="")
    )
    
    for labelID in label_path.walk(person):
        if 'PR' in labelID and 'FTHR' not in labelID and 'MTHR' not in labelID:
            print(f"  Found person {person_id} with label {labelID}")
```

Output:
```
Processing person 123 with href: https://example.com/personas/456
  Found person 123 with label PR_GIVEN
Processing person 789 with href: https://example.com/personas/999
  Found person 789 with label PR_SURNAME
```

### Using Single Values with next()

```python
from JsonWalker.walk import jsonPath

# Sample data
data = {
    "users": [
        {"name": "John", "age": 30},
        {"name": "Jane", "age": 25}
    ]
}

# Get just the first user's name
result = next(jsonPath().key("users").index(0).key("name").walk(data))
print(f"First user's name: {result}")  # Output: First user's name: John

# Get the last user's age
result = next(jsonPath().key("users").index(-1).key("age").walk(data))
print(f"Last user's age: {result}")  # Output: Last user's age: 25
```

### Handling Missing Keys with Defaults

```python
from JsonWalker.walk import jsonPath

# Sample data with missing fields
data = {
    "users": [
        {"name": "John", "age": 30},
        {"name": "Jane"},  # Missing age
        {"age": 40}        # Missing name
    ]
}

# Access with defaults for missing keys
path = jsonPath().key("users").all().addContext().multi(
    jsonPath().key("name", default="unknown_name"),
    jsonPath().key("age", default=-1)
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

## Key Features

1. **Generator-based**: Efficient memory usage for large datasets
2. **Chainable API**: Build complex queries step by step
3. **Context preservation**: Keep intermediate values during traversal
4. **Type-safe defaults**: Specify fallback values with proper types
5. **Multi-value queries**: Extract multiple values in a single traversal
6. **Flexible indexing**: Support for positive/negative indices and slicing
7. **Dictionary iteration**: Built-in support for key-value pair traversal

## Benefits

1. **Discoverability**: IDE autocompletion shows available methods as you type
2. **Type Safety**: Proper type hints reduce runtime errors
3. **Readability**: Method names clearly express intent (`.key()`, `.all()`, `.addContext()`)
4. **Extensibility**: Easy to add new functionality through method chaining
5. **Debugging**: Stack traces point to specific methods, not string parsing errors
6. **Documentation**: Each method has clear docstrings explaining its purpose

## Best Practices

1. **Use meaningful variable names**: The fluent API makes it easy to create readable code
2. **Chain operations logically**: Group related operations together
3. **Leverage context**: Use `.addContext()` to preserve intermediate values
4. **Provide defaults**: Use the `default` parameter to handle missing keys gracefully
5. **Break complex queries**: Split very long chains into intermediate variables for readability