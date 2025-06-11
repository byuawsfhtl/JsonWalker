# JsonWalker

_Allows simple, quick, and easy parsing of nasty nested JSON through a fluent object-oriented tool with full type inference to avoid hours of pain_

JsonWalker's goal is to allow users to specify a path through nested JSON-like data using a chainable, discoverable API, and get the items at each match in the JSON. The library uses generators to efficiently traverse large data structures while providing IDE autocompletion and type checking.

## Installation

JsonWalker is a pip installable package. It is a public package hosted on [PyPi](https://pypi.org/project/JsonWalker/).

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
from JsonWalker.walk import JsonPath

# Create a path with type inference
path = JsonPath().key("users").listAll().key("name").ensureType(str)

# Use in a for loop - IDE knows 'name' is a string
for name in path.walk(data):
    print(name)

# Or get single values
first_name = next(path.walk(data))
```

```
=== Basic Usage Pattern ===
User: Alice
User: Bob
User: Charlie
First user: Alice
```

## Key Features

1. **Full Type Inference**: IDE autocompletion and type checking throughout your JSON traversal
2. **Generator-based**: Efficient memory usage for large datasets
3. **Chainable API**: Build complex queries step by step
4. **Type-safe operations**: Ensure values match expected types with `ensureType()`
5. **Multi-value queries**: Extract multiple values in a single traversal with proper typing
6. **Flexible indexing**: Support for positive/negative indices and slicing
7. **Dictionary iteration**: Built-in support for key-value pair traversal
8. **Path composition**: Combine and reuse path segments with PathJoin
9. **Filtering**: Include only items that meet specific conditions

## Learning JsonWalker: Step by Step

### 1. Basic Key Access with Type Safety

Start with simple dictionary navigation using `.key()` and add type safety with `.ensureType()`.

```python
from JsonWalker.walk import JsonPath

# Sample data
data = {
    "user": {
        "name": "John",
        "age": 30
    }
}

# Access user's name with type inference
path = JsonPath().key("user").key("name").ensureType(str)
for name in path.walk(data):  # IDE knows 'name' is str
    print(f"Name: {name}")
    
# Access user's age with type inference
age_path = JsonPath().key("user").key("age").ensureType(int)
for age in age_path.walk(data):  # IDE knows 'age' is int
    print(f"Age: {age}")
```

```
=== Section 1: Basic Key Access with Type Safety ===
Name: John
Age: 30
```

#### Handling Missing Keys with Defaults and Type Safety

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

# Access with defaults and type safety
path = JsonPath().key("users").listAll().key("name", default="Unknown").ensureType(str)
for name in path.walk(data):  # IDE knows 'name' is str
    print(f"Name: {name}")
```

```
=== Section 1: Handling Missing Keys ===
Name: John
Name: Jane
Name: Unknown
```

### 2. Working with Lists and Type Safety

JsonWalker provides several ways to work with arrays with full type inference.

#### List All Items with Type Safety

```python
from JsonWalker.walk import JsonPath

data = {
    "fruits": ["apple", "banana", "cherry"]
}

path = JsonPath().key("fruits").listAll().ensureType(str)
for fruit in path.walk(data):  # IDE knows 'fruit' is str
    print(f"Fruit: {fruit}")
```

```
=== Section 2: Working with Lists and Type Safety ===
Fruit: apple
Fruit: banana
Fruit: cherry
```

#### Specific List Index with Type Safety

```python
from JsonWalker.walk import JsonPath

data = {
    "numbers": [0, 1, 2, 3, 4, 5],
    "scores": [95.5, 87.2, 92.8]
}

# Get first number as integer
path = JsonPath().key("numbers").listIndex(0).ensureType(int)
first_number = next(path.walk(data))  # Type: int
print(f"First number: {first_number}")

# Get first score as float
score_path = JsonPath().key("scores").listIndex(0).ensureType(float)
first_score = next(score_path.walk(data))  # Type: float
print(f"First score: {first_score}")
```

```
=== Section 2: Specific List Index ===
First number: 0
First score: 95.5
```

### 3. Multi-Value Returns

Use `.multi()` to get multiple values from the same level (with complete type safety).

#### Basic Multi Example with Type Inference

```python
from JsonWalker.walk import JsonPath

data = {
    "users": [
        {
            "profile": {
                "firstName": "John",
                "lastName": "Doe",
                "age": 30
            }
        },
        {
            "profile": {
                "firstName": "Jane",
                "lastName": "Smith",
                "age": 25
            }
        }
    ]
}

# Get first name, last name, and age with type inference
path = JsonPath().key("users").listAll().key("profile").multi(
    JsonPath().key("firstName").ensureType(str),
    JsonPath().key("lastName").ensureType(str),
    JsonPath().key("age").ensureType(int)
)

for firstName, lastName, age in path.walk(data):  # IDE knows types: str, str, int
    print(f"{firstName} {lastName} is {age} years old")
```

```
=== Section 3: Basic Multi Example ===
John Doe is 30 years old
Jane Smith is 25 years old
```

#### Complex Multi with Nested Types

```python
from JsonWalker.walk import JsonPath

data = {
    "products": [
        {
            "info": {
                "name": "Laptop",
                "price": 999.99,
                "inStock": True,
                "tags": ["electronics", "computer", "portable"]
            }
        },
        {
            "info": {
                "name": "Book",
                "price": 15.50,
                "inStock": False,
                "tags": ["education", "reading"]
            }
        }
    ]
}

# Get name, price, stock status, and all tags with type safety
path = JsonPath().key("products").listAll().key("info").multi(
    JsonPath().key("name").ensureType(str),
    JsonPath().key("price").ensureType(float),
    JsonPath().key("inStock").ensureType(bool),
    JsonPath().key("tags").listAll().ensureType(str)
)

for name, price, in_stock, tag in path.walk(data):  # Types: str, float, bool, str
    status = "Available" if in_stock else "Out of Stock"
    print(f"{name} (${price}) - {status} - Tag: {tag}")
```

```
=== Section 3: Complex Multi with Nested Types ===
Laptop ($999.99) - Available - Tag: electronics
Laptop ($999.99) - Available - Tag: computer
Laptop ($999.99) - Available - Tag: portable
Book ($15.5) - Out of Stock - Tag: education
Book ($15.5) - Out of Stock - Tag: reading
```

### 4. Filtering

Use `.filter()` to include only items that meet certain conditions

```python
from JsonWalker.walk import JsonPath

data = {
    "products": [
        {
            "name": "Laptop",
            "category": "electronics",
            "price": 999.99,
            "rating": 4.5
        },
        {
            "name": "Book",
            "category": "books", 
            "price": 15.50,
            "rating": 4.8
        },
        {
            "name": "Phone",
            "category": "electronics",
            "price": 699.99,
            "rating": 4.2
        }
    ]
}

# Get names and prices of highly-rated electronic products
path = JsonPath().key('products').listAll().filter(
    conditionPath=JsonPath().key('category').ensureType(str),
    condition=lambda x: x == 'electronics'
).filter(
    conditionPath=JsonPath().key('rating').ensureType(float),
    condition=lambda x: x > 4.3
).multi(
    JsonPath().key('name').ensureType(str),
    JsonPath().key('price').ensureType(float)
)

for product_name, price in path.walk(data):  # Types: str, float
    print(f"{product_name}: ${price}")
```

```
=== Section 4: Filtering with Type Safety ===
Laptop: $999.99
```

### 5. Dictionary Iteration with Type Safety

When you need to iterate through all key-value pairs in a dictionary with type inference.

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
# The keyContextAndValue() method returns tuple[str, Any] by default
for subject, score in path.walk(data):  # Types: str, Any
    print(f"{subject}: {score}")
```

```
=== Section 5: Dictionary Iteration ===
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

# Get all subcategory names and their items with type inference
path = JsonPath().key('categories').keyContextAndValue().keyContextAndValue().listAll().ensureType(str)
for category, subcategory, item in path.walk(data):  # Types: str, str, str
    print(f"{category} > {subcategory} > {item}")
```

```
=== Section 5: Complex Dictionary Iteration ===
electronics > computers > laptop
electronics > computers > desktop
electronics > phones > smartphone
electronics > phones > tablet
books > fiction > novel
books > fiction > short story
books > non-fiction > biography
books > non-fiction > textbook
```

### 6. Real-World Example: Processing API Response

```python
from JsonWalker.walk import JsonPath

# Complex API response structure
api_response = {
    "results": [
        {
            "user": {
                "id": 123,
                "profile": {
                    "name": "John Doe",
                    "age": 30,
                    "active": True,
                    "contacts": [
                        {"type": "email", "value": "john@example.com"},
                        {"type": "phone", "value": "555-1234"}
                    ]
                }
            }
        }
    ]
}

# Extract all user information with complete type safety
path = JsonPath().key("results").listAll().key("user").multi(
    JsonPath().key("id").ensureType(int),
    JsonPath().key("profile").multi(
        JsonPath().key("name").ensureType(str),
        JsonPath().key("age").ensureType(int),
        JsonPath().key("active").ensureType(bool),
        JsonPath().key("contacts").listAll().multi(
            JsonPath().key("type").ensureType(str),
            JsonPath().key("value").ensureType(str)
        )
    )
)

for user_id, (name, age, active, (contact_type, contact_value)) in path.walk(api_response):
    # IDE knows all the types: int, str, int, bool, str, str
    status = "Active" if active else "Inactive"
    print(f"User {user_id}: {name} ({age}) - {status} - {contact_type}: {contact_value}")
```

```
=== Section 6: Real-World API Response Example ===
User 123: John Doe (30) - Active - email: john@example.com
User 123: John Doe (30) - Active - phone: 555-1234
```

### 7. Path Joining

Use `PathJoin` to combine multiple reusable path segments (while maintaining type inference and safety).

```python
from JsonWalker.walk import JsonPath, PathJoin

data = {
    "company": {
        "departments": [
            {
                "name": "Engineering",
                "employees": [
                    {"name": "Alice", "role": "Developer", "salary": 75000},
                    {"name": "Bob", "role": "Manager", "salary": 85000}
                ]
            }
        ]
    }
}

# Define reusable path segments
company_path = JsonPath().key("company")
departments_path = JsonPath().key("departments").listAll()
employees_path = JsonPath().key("employees").listAll()

# Combine paths for different data types
name_path = PathJoin(company_path, departments_path, employees_path, JsonPath().key("name").ensureType(str))
salary_path = PathJoin(company_path, departments_path, employees_path, JsonPath().key("salary").ensureType(int))

# Use with type safety
print("Employee names:")
for name in name_path.walk(data):  # Type: str
    print(f"  Employee: {name}")
    
print("Employee salaries:")
for salary in salary_path.walk(data):  # Type: int
    print(f"  Salary: ${salary:,}")
```

```
=== Section 7: Path Joining ===
Employee names:
  Employee: Alice
  Employee: Bob
Employee salaries:
  Salary: $75,000
  Salary: $85,000
```

## Advanced Type Safety Features

### Type Narrowing with ensureType()

The `ensureType()` method filters out values that don't match the expected type and provides type inference. You don't need to use it at the end of your paths- the only consequence is that your variable will just have return type of `any`. Type hinting is nice though, which is why this demo has it for all the examples.

```python
from JsonWalker.walk import JsonPath

# Mixed data types
data = {
    "mixed_values": [
        "string_value",
        42,
        3.14,
        True,
        {"nested": "object"},
        [1, 2, 3]
    ]
}

# Extract only strings
print("Strings:")
string_path = JsonPath().key("mixed_values").listAll().ensureType(str)
for value in string_path.walk(data):  # Type: str
    print(f"  String: {value}")

# Extract only numbers (integers)
print("Integers:")
int_path = JsonPath().key("mixed_values").listAll().ensureType(int)
for value in int_path.walk(data):  # Type: int
    print(f"  Integer: {value}")

# Extract only dictionaries
print("Dictionaries:")
dict_path = JsonPath().key("mixed_values").listAll().ensureType(dict)
for value in dict_path.walk(data):  # Type: dict
    print(f"  Dictionary: {value}")
```

```
=== Advanced: Type Narrowing ===
Strings:
  String: string_value
Integers:
  Integer: 42
  Integer: True
Dictionaries:
  Dictionary: {'nested': 'object'}
```

The above example is a great way to demo the cursed knowledge that `True` is actually an `int` in Python.

### Working with Optional Values

```python
from JsonWalker.walk import JsonPath
from typing import Optional

data = {
    "users": [
        {"name": "John", "email": "john@example.com"},
        {"name": "Jane"},  # No email
        {"name": "Bob", "email": None}  # Explicit None
    ]
}

# Handle optional emails
path = JsonPath().key("users").listAll().multi(
    JsonPath().key("name").ensureType(str),
    JsonPath().key("email", default=None)  # May be None or string
)

for name, email in path.walk(data):  # Types: str, Any
    if isinstance(email, str):  # Type narrowing
        print(f"{name}: {email}")
    else:
        print(f"{name}: No email")
```

```
=== Advanced: Optional Values ===
John: john@example.com
Jane: No email
Bob: No email
```

### Example: Complete Type-Safe Data Processing

```python
from JsonWalker.walk import JsonPath

# Complex e-commerce data
data = {
    "orders": [
        {
            "id": "ORD-001",
            "customer": {
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "vip": True
            },
            "items": [
                {"name": "Laptop", "price": 999.99, "quantity": 1},
                {"name": "Mouse", "price": 29.99, "quantity": 2}
            ],
            "total": 1059.97,
            "status": "completed"
        }
    ]
}

# Extract complete order information with full type safety
path = JsonPath().key("orders").listAll().filter(
    conditionPath=JsonPath().key("status").ensureType(str),
    condition=lambda x: x == "completed"
).multi(
    JsonPath().key("id").ensureType(str),
    JsonPath().key("customer").multi(
        JsonPath().key("name").ensureType(str),
        JsonPath().key("vip").ensureType(bool)
    ),
    JsonPath().key("items").listAll().multi(
        JsonPath().key("name").ensureType(str),
        JsonPath().key("price").ensureType(float),
        JsonPath().key("quantity").ensureType(int)
    ),
    JsonPath().key("total").ensureType(float)
)

for order_id, (customer_name, is_vip), (item_name, price, qty), total in path.walk(data):
    # All types are properly inferred: str, str, bool, str, float, int, float
    vip_status = " (VIP)" if is_vip else ""
    item_total = price * qty
    print(f"Order {order_id} - {customer_name}{vip_status}")
    print(f"  {item_name}: ${price} x {qty} = ${item_total}")
    print(f"  Order Total: ${total}")
```

```
=== Complete Example: E-commerce Data Processing ===
Order ORD-001 - Alice Johnson (VIP)
  Laptop: $999.99 x 1 = $999.99
  Order Total: $1059.97
Order ORD-001 - Alice Johnson (VIP)
  Mouse: $29.99 x 2 = $59.98
  Order Total: $1059.97
```

This comprehensive type safety makes JsonWalker not just a powerful JSON traversal tool, but also a type-safe one that integrates seamlessly with modern Python development workflows and IDE features.

## API Reference

### Core Methods

| Method | Description | Type Return |
|--------|-------------|-------------|
| `JsonPath()` | Start a new JSON path query chain | `JsonPath[Any]` |
| `.walk(data)` | Execute the path query on JSON data as a Generator | `Generator[T, None, None]` |

### Basic Path Building

| Method | Description | Example | Type Return |
|--------|-------------|---------|-------------|
| `.key(name, default=None)` | Access dictionary by key with optional default | `.key("users")` | `Key[Any]` |
| `.listIndex(idx)` | Access list by specific index | `.listIndex(0)` | `Index[Any]` |
| `.listSlice(start, end)` | Access range of list items | `.listSlice(1, 5)` | `Slice[Any]` |
| `.listAll()` | Access all items in a list | `.listAll()` | `Slice[Any]` |

### Type Safety Methods

| Method | Description | Example | Type Return |
|--------|-------------|---------|-------------|
| `.ensureType(type_class)` | Ensure value matches expected type | `.ensureType(str)` | `EnsureType[T]` |

### Advanced Methods

| Method | Description | Example | Type Return |
|--------|-------------|---------|-------------|
| `.filter(conditionPath, condition)` | Filter results based on a condition | `.filter(JsonPath().key('status'), lambda x: x == 'active')` | `Filter[T]` |
| `.keyContextAndValue()` | Iterate through key-value pairs | `.keyContextAndValue()` | `KeyContextAndValue[tuple[str, Any]]` |
| `.multi(*paths)` | Get multiple values from current context | `.multi(path1, path2)` | `MultiValue[tuple[...]]` |
| `.addContext()` | Add current value to context | `.addContext()` | `AddedContext[T]` |

### Path Utilities

| Class/Method | Description | Example |
|--------------|-------------|---------|
| `PathJoin(*paths)` | Combine multiple path segments | `PathJoin(base_path, detail_path)` |

## Best Practices

1. **Start simple**: Begin with basic `.key()` and `.listAll()` operations
2. **Use meaningful variable names**: The fluent API makes code self-documenting
3. **Provide defaults**: Use the `default` parameter to handle missing keys gracefully
4. **Break complex queries**: Split very long chains into intermediate variables for readability
5. **Leverage PathJoin**: Create reusable path segments for common patterns
6. **Filter early**: Apply filters as early as possible in your path to improve performance
7. **Use multi strategically**: When you need multiple related values, `.multi()` is more efficient than separate queries
8. **Handle mixed types**: Use `ensureType()` to filter and work with specific types. This will also give your IDE the ability to infer types when using the `walk` function