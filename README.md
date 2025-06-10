# JsonWalker

_Allows simple, quick, and easy parsing of nasty nested JSON through a fluent object-oriented tool to avoid hours of pain_

JsonWalker's goal is to allow users to specify a path through nested JSON using a chainable, discoverable API, and get the items at each match in the JSON. The library uses generators to efficiently traverse large data structures.

## Installation

JsonWalker is a pip installable package. It is a public package, and will thus not need any special permissions to install.

### Command Line Installation

To install from the command line, simply do `pip install JsonWalker`.

### Use in other pip packages

As this is a public package, it can be added to the required packages of any pip installable packages and will be installed automatically when those are installed in other projects.

## Quick Start

To use this in a project, install using one of the installation methods shown above.

Import the JsonPath class into your file: `from JsonWalker.walk import JsonPath`

As the walk command makes a generator, it can be used in multiple ways.

### Basic Usage Pattern

```python
# Create a path
path = JsonPath().key("users").listAll().key("name")

# Use in a for loop
for name in path.walk(data):
    print(name)

# Or get single values
first_name = next(path.walk(data))
```

## Learning JsonWalker: Step by Step

### 1. Basic Key Access

Start with simple dictionary navigation using `.key()`.

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
    print(name)  # Output: John
```

#### Handling Missing Keys with Defaults

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
path = JsonPath().key("users").listAll().key("name", default="Unknown")
for name in path.walk(data):
    print(name)  # Output: John, Jane, Unknown
```

### 2. Working with Lists

JsonWalker provides several ways to work with arrays.

#### List All Items

```python
from JsonWalker.walk import JsonPath

data = {
    "fruits": ["apple", "banana", "cherry"]
}

path = JsonPath().key("fruits").listAll()
for fruit in path.walk(data):
    print(fruit)  # Output: apple, banana, cherry
```

#### Specific List Index

```python
from JsonWalker.walk import JsonPath

data = {
    "numbers": [0, 1, 2, 3, 4, 5]
}

# Get first item (index 0)
path = JsonPath().key("numbers").listIndex(0)
first_number = next(path.walk(data))
print(first_number)  # Output: 0

# Get last item (negative index)
path = JsonPath().key("numbers").listIndex(-1)
last_number = next(path.walk(data))
print(last_number)  # Output: 5
```

#### List Slicing

```python
from JsonWalker.walk import JsonPath

data = {
    "numbers": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
}

# Get numbers from index 2 to 5 (exclusive)
path = JsonPath().key("numbers").listSlice(2, 6)
for num in path.walk(data):
    print(num)  # Output: 2, 3, 4, 5

# Get the last 3 numbers
path = JsonPath().key("numbers").listSlice(-3, None)
for num in path.walk(data):
    print(num)  # Output: 7, 8, 9
```

### 3. Combining Keys and Lists

Most real-world JSON combines dictionaries and arrays.

```python
from JsonWalker.walk import JsonPath

data = {
    "users": [
        {"name": "John", "age": 30},
        {"name": "Jane", "age": 25}
    ]
}

# Get all user names
path = JsonPath().key("users").listAll().key("name")
for name in path.walk(data):
    print(name)  # Output: John, Jane
```

### 4. Filtering Results

Use `.filter()` to include only items that meet certain conditions.

```python
from JsonWalker.walk import JsonPath

data = {
    "products": [
        {
            "name": "Laptop",
            "category": "electronics",
            "price": 999
        },
        {
            "name": "Book",
            "category": "books", 
            "price": 15
        },
        {
            "name": "Phone",
            "category": "electronics",
            "price": 699
        }
    ]
}

# Get names of only electronic products
path = JsonPath().key('products').listAll().filter(
    conditionPath=JsonPath().key('category'),
    condition=lambda x: x == 'electronics'
).key('name')

for product_name in path.walk(data):
    print(product_name)  # Output: Laptop, Phone
```

#### Complex Filtering Example

```python
from JsonWalker.walk import JsonPath

data = {
    "employees": [
        {
            "name": "Alice",
            "department": {"name": "Engineering", "budget": 50000},
            "salary": 75000
        },
        {
            "name": "Bob", 
            "department": {"name": "Marketing", "budget": 30000},
            "salary": 65000
        },
        {
            "name": "Charlie",
            "department": {"name": "Engineering", "budget": 50000},
            "salary": 80000
        }
    ]
}

# Get names of employees in high-budget departments
path = JsonPath().key('employees').listAll().filter(
    conditionPath=JsonPath().key('department').key('budget'),
    condition=lambda x: x > 40000
).key('name')

for name in path.walk(data):
    print(name)  # Output: Alice, Charlie
```

### 5. Dictionary Iteration with keyContextAndValue

When you need to iterate through all key-value pairs in a dictionary.

```python
from JsonWalker.walk import JsonPath

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

#### More Complex Dictionary Iteration

```python
from JsonWalker.walk import JsonPath

data = {
    "categories": {
        "electronics": {
            "computers": ["laptop", "desktop"],
            "phones": ["smartphone", "tablet"]
        },
        "books": {
            "fiction": ["novel", "short story"],
            "non-fiction": ["biography", "textbook"]
        }
    }
}

# Get all subcategory names and their items
path = JsonPath().key('categories').keyContextAndValue().keyContextAndValue().listAll()
for category, subcategory, item in path.walk(data):
    print(f"{category} > {subcategory} > {item}")
```

Output:
```
electronics > computers > laptop
electronics > computers > desktop
electronics > phones > smartphone
electronics > phones > tablet
books > fiction > novel
books > fiction > short story
books > non-fiction > biography
books > non-fiction > textbook
```

### 6. Multi-Value Returns

Use `.multi()` to get multiple values from the same level in a single traversal.

#### Basic Multi Example

```python
from JsonWalker.walk import JsonPath

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
                "firstName": "Jane",
                "lastName": "Smith"
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

Output:
```
John Doe
Jane Smith
```

#### Multi with Different Data Types

```python
from JsonWalker.walk import JsonPath

data = {
    "products": [
        {
            "info": {
                "name": "Laptop",
                "price": 999,
                "tags": ["electronics", "computer", "portable"]
            }
        },
        {
            "info": {
                "name": "Book",
                "price": 15,
                "tags": ["education", "reading"]
            }
        }
    ]
}

# Get name, price, and all tags for each product
path = JsonPath().key("products").listAll().key("info").multi(
    JsonPath().key("name"),
    JsonPath().key("price"),
    JsonPath().key("tags").listAll()
)

for name, price, tag in path.walk(data):
    print(f"{name} (${price}) - {tag}")
```

Output:
```
Laptop ($999) - electronics
Laptop ($999) - computer
Laptop ($999) - portable
Book ($15) - education
Book ($15) - reading
```

#### Multi with Nested Objects

```python
from JsonWalker.walk import JsonPath

data = {
    "employees": [
        {
            "personal": {
                "name": "Alice",
                "age": 30
            },
            "work": {
                "department": "Engineering",
                "position": "Senior Developer"
            },
            "skills": ["Python", "JavaScript", "SQL"]
        }
    ]
}

# Get personal info, work info, and skills all at once
path = JsonPath().key("employees").listAll().multi(
    JsonPath().key("personal").key("name"),
    JsonPath().key("work").key("department"),
    JsonPath().key("skills").listAll()
)

for name, department, skill in path.walk(data):
    print(f"{name} from {department} knows {skill}")
```

Output:
```
Alice from Engineering knows Python
Alice from Engineering knows JavaScript
Alice from Engineering knows SQL
```

#### Complex Multi Example

```python
from JsonWalker.walk import JsonPath

data = {
    "schools": [
        {
            "name": "Tech University",
            "departments": [
                {
                    "name": "Computer Science",
                    "courses": [
                        {"code": "CS101", "title": "Intro to Programming"},
                        {"code": "CS201", "title": "Data Structures"}
                    ]
                }
            ],
            "location": {"city": "Tech City", "state": "CA"}
        }
    ]
}

# Get school info and all course details
path = JsonPath().key("schools").listAll().multi(
    JsonPath().key("name"),
    JsonPath().key("location").key("city"),
    JsonPath().key("departments").listAll().key("courses").listAll().multi(
        JsonPath().key("code"),
        JsonPath().key("title")
    )
)

for school_name, city, (course_code, course_title) in path.walk(data):
    print(f"{school_name} in {city}: {course_code} - {course_title}")
```

Output:
```
Tech University in Tech City: CS101 - Intro to Programming
Tech University in Tech City: CS201 - Data Structures
```

### 7. Path Joining

Use `PathJoin` to combine multiple reusable path segments.

```python
from JsonWalker.walk import JsonPath, PathJoin

data = {
    "company": {
        "departments": [
            {
                "name": "Engineering",
                "employees": [
                    {"name": "Alice", "role": "Developer"},
                    {"name": "Bob", "role": "Manager"}
                ]
            }
        ]
    }
}

# Define reusable path segments
company_path = JsonPath().key("company")
departments_path = JsonPath().key("departments").listAll()
employee_name_path = JsonPath().key("employees").listAll().key("name")

# Combine paths using PathJoin
full_path = PathJoin(company_path, departments_path, employee_name_path)

for name in full_path.walk(data):
    print(name)  # Output: Alice, Bob
```

#### PathJoin for Complex Reusable Patterns

```python
from JsonWalker.walk import JsonPath, PathJoin

data = {
    "api_response": {
        "data": {
            "users": [
                {
                    "profile": {"name": "John", "email": "john@example.com"},
                    "settings": {"theme": "dark", "notifications": True}
                }
            ]
        }
    }
}

# Define common path segments
api_base = JsonPath().key("api_response").key("data")
user_list = JsonPath().key("users").listAll()
profile_section = JsonPath().key("profile")

# Combine for different use cases
name_path = PathJoin(api_base, user_list, profile_section, JsonPath().key("name"))
email_path = PathJoin(api_base, user_list, profile_section, JsonPath().key("email"))

# Use the combined paths
for name in name_path.walk(data):
    print(f"Name: {name}")
    
for email in email_path.walk(data):
    print(f"Email: {email}")
```

Output:
```
Name: John
Email: john@example.com
```

## API Reference

### Core Methods

| Method | Description |
|--------|-------------|
| `JsonPath()` | Start a new JSON path query chain |
| `.walk(data)` | Execute the path query on JSON data as a Generator |

### Basic Path Building

| Method | Description | Example |
|--------|-------------|---------|
| `.key(name, default=None)` | Access dictionary by key with optional default | `.key("users", default=[])` |
| `.listIndex(idx)` | Access list by specific index (supports negative) | `.listIndex(0)` or `.listIndex(-1)` |
| `.listSlice(start, end)` | Access range of list items | `.listSlice(1, 5)` |
| `.listAll()` | Access all items in a list | `.listAll()` |

### Advanced Methods

| Method | Description | Example |
|--------|-------------|---------|
| `.filter(conditionPath, condition)` | Filter results based on a condition | `.filter(JsonPath().key('status'), lambda x: x == 'active')` |
| `.keyContextAndValue()` | Iterate through key-value pairs of dictionaries | `.keyContextAndValue()` |
| `.multi(*paths)` | Get multiple values from the current context | `.multi(JsonPath().key('name'), JsonPath().key('age'))` |

### Path Utilities

| Class/Method | Description | Example |
|--------------|-------------|---------|
| `PathJoin(*paths)` | Combine multiple path segments into one | `PathJoin(base_path, detail_path)` |

## Real-World Examples

### Processing API Response

```python
from JsonWalker.walk import JsonPath

# Complex API response structure
api_response = {
    "results": [
        {
            "user": {
                "id": "123",
                "profile": {
                    "name": "John Doe",
                    "contacts": [
                        {"type": "email", "value": "john@example.com"},
                        {"type": "phone", "value": "555-1234"}
                    ]
                }
            }
        }
    ]
}

# Extract all contact information
path = JsonPath().key("results").listAll().key("user").key("profile").key("contacts").listAll().multi(
    JsonPath().key("type"),
    JsonPath().key("value")
)

for contact_type, contact_value in path.walk(api_response):
    print(f"{contact_type}: {contact_value}")
```

Output:
```
email: john@example.com
phone: 555-1234
```

### Handling Inconsistent Data Structures

```python
from JsonWalker.walk import JsonPath

# Real-world data often has inconsistent structure
data = {
    "categories": {
        "electronics": {
            "computers": {
                "laptops": ["MacBook", "ThinkPad"],
                "desktops": ["iMac", "HP Pavilion"]
            }
        },
        "books": ["Python Guide", "JavaScript Handbook"]  # Direct array, no subcategories
    }
}

# Handle electronics (nested structure)
electronics_path = JsonPath().key('categories').key('electronics').keyContextAndValue().keyContextAndValue().listAll()
for category, subcategory, item in electronics_path.walk(data):
    print(f"Electronics > {subcategory} > {item}")

# Handle books (direct array)
books_path = JsonPath().key('categories').key('books').listAll()
for book in books_path.walk(data):
    print(f"Books > {book}")
```

Output:
```
Electronics > laptops > MacBook
Electronics > laptops > ThinkPad
Electronics > desktops > iMac
Electronics > desktops > HP Pavilion
Books > Python Guide
Books > JavaScript Handbook
```

## Key Features

1. **Generator-based**: Efficient memory usage for large datasets
2. **Chainable API**: Build complex queries step by step
3. **Type-safe defaults**: Specify fallback values with proper types
4. **Multi-value queries**: Extract multiple values in a single traversal
5. **Flexible indexing**: Support for positive/negative indices and slicing
6. **Dictionary iteration**: Built-in support for key-value pair traversal
7. **Path composition**: Combine and reuse path segments with PathJoin
8. **Filtering**: Include only items that meet specific conditions

## Best Practices

1. **Start simple**: Begin with basic `.key()` and `.listAll()` operations
2. **Use meaningful variable names**: The fluent API makes code self-documenting
3. **Provide defaults**: Use the `default` parameter to handle missing keys gracefully
4. **Break complex queries**: Split very long chains into intermediate variables for readability
5. **Leverage PathJoin**: Create reusable path segments for common patterns
6. **Filter early**: Apply filters as early as possible in your path to improve performance
7. **Use multi strategically**: When you need multiple related values, `.multi()` is more efficient than separate queries