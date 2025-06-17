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
path = JsonPath().key("users").list_all().key("name").ensure_type(str)

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
4. **Type-safe operations**: Ensure values match expected types with `ensure_type()`
5. **Multi-value queries**: Extract multiple values in a single traversal with proper typing
6. **Flexible indexing**: Support for positive/negative indices and slicing
7. **Dictionary iteration**: Built-in support for key-value pair traversal
8. **Path composition**: Combine and reuse path segments with `.add()`
9. **Filtering**: Include only items that meet specific conditions

## Learning JsonWalker: Step by Step

### 1. Basic Key Access with

Start with simple dictionary navigation using `.key()` and add type safety with `.ensure_type()`.

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
path = JsonPath().key("user").key("name").ensure_type(str)
for name in path.walk(data):  # IDE knows 'name' is str
    print(f"Name: {name}")
    
# Access user's age with type inference
age_path = JsonPath().key("user").key("age").ensure_type(int)
for age in age_path.walk(data):  # IDE knows 'age' is int
    print(f"Age: {age}")
```

```
=== Section 1: Basic Key Access with Type Safety ===
Name: John
Age: 30
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

# Access with defaults and type safety
path = JsonPath().key("users").list_all().key("name", default="Unknown").ensure_type(str)
for name in path.walk(data):  # IDE knows 'name' is str
    print(f"Name: {name}")
```

```
=== Section 1: Handling Missing Keys ===
Name: John
Name: Jane
Name: Unknown
```

### 2. Working with Lists

JsonWalker provides several ways to work with arrays with full type inference.

#### List All Items

```python
from JsonWalker.walk import JsonPath

data = {
    "fruits": ["apple", "banana", "cherry"]
}

path = JsonPath().key("fruits").list_all().ensure_type(str)
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
path = JsonPath().key("numbers").list_index(0).ensure_type(int)
first_number = next(path.walk(data))  # Type: int
print(f"First number: {first_number}")

# Get first score as float
score_path = JsonPath().key("scores").list_index(0).ensure_type(float)
first_score = next(score_path.walk(data))  # Type: float
print(f"First score: {first_score}")
```

```
=== Section 2: Specific List Index ===
First number: 0
First score: 95.5
```

### Working with list_slice

The `list_slice()` method allows you to access specific ranges of elements from lists, following Python's slice notation rules. Understanding the inclusive/exclusive behavior and negative indexing is crucial for effective use.

#### Understanding Slice Behavior with Numbered Data

```python
from JsonWalker.walk import JsonPath

# Sample data with numbered items to demonstrate slice behavior
data = {
    "items": [
        {"id": 0, "name": "item_zero"},
        {"id": 1, "name": "item_one"},
        {"id": 2, "name": "item_two"},
        {"id": 3, "name": "item_three"},
        {"id": 4, "name": "item_four"},
        {"id": 5, "name": "item_five"},
        {"id": 6, "name": "item_six"},
        {"id": 7, "name": "item_seven"},
        {"id": 8, "name": "item_eight"},
        {"id": 9, "name": "item_nine"}
    ]
}

# Basic slice: start=2, end=5 (inclusive start, exclusive end)
# Gets indices 2, 3, 4 (NOT 5)
path = JsonPath().key("items").list_slice(2, 5).key("name").ensure_type(str)
print("Slice [2:5] (items 2, 3, 4):")
for name in path.walk(data):
    print(f"  {name}")
```

```
=== list_slice: Basic Range ===
Slice [2:5] (items 2, 3, 4):
  item_two
  item_three
  item_four
```

#### From Start and To End

```python
from JsonWalker.walk import JsonPath

# Same data as above

# From beginning to index 3 (exclusive)
start_path = JsonPath().key("items").list_slice(None, 3).key("id").ensure_type(int)
print("From start to index 3 [None:3]:")
for item_id in start_path.walk(data):
    print(f"  ID: {item_id}")

print()

# From index 7 to end
end_path = JsonPath().key("items").list_slice(7, None).key("id").ensure_type(int)
print("From index 7 to end [7:None]:")
for item_id in end_path.walk(data):
    print(f"  ID: {item_id}")
```

```
=== list_slice: Start and End Boundaries ===
From start to index 3 [None:3]:
  ID: 0
  ID: 1
  ID: 2

From index 7 to end [7:None]:
  ID: 7
  ID: 8
  ID: 9
```

#### Negative Indexing

```python
from JsonWalker.walk import JsonPath

# Same data as above

# Last 3 items using negative indexing
negative_path = JsonPath().key("items").list_slice(-3, None).multi(
    JsonPath().key("id").ensure_type(int),
    JsonPath().key("name").ensure_type(str)
)
print("Last 3 items [-3:None]:")
for item_id, name in negative_path.walk(data):
    print(f"  ID {item_id}: {name}")

print()

# From index 2 to 3rd from end (exclusive)
mixed_path = JsonPath().key("items").list_slice(2, -2).key("id").ensure_type(int)
print("From index 2 to 3rd from end [2:-2]:")
for item_id in mixed_path.walk(data):
    print(f"  ID: {item_id}")
```

```
=== list_slice: Negative Indexing ===
Last 3 items [-3:None]:
  ID 7: item_seven
  ID 8: item_eight
  ID 9: item_nine

From index 2 to 3rd from end [2:-2]:
  ID: 2
  ID: 3
  ID: 4
  ID: 5
  ID: 6
  ID: 7
```

### Key Points About list_slice

- **Start is inclusive**: `list_slice(2, 5)` includes index 2
- **End is exclusive**: `list_slice(2, 5)` does NOT include index 5
- **None means boundary**: `list_slice(None, 3)` starts from beginning, `list_slice(7, None)` goes to end
- **Negative indices count from end**: `-1` is the last item, `-2` is second to last, etc.
- **Same as Python slicing**: `list_slice(2, 5)` behaves exactly like `my_list[2:5]`
- **Empty results are safe**: Out-of-bounds slices return no results rather than errors

#### Comparison with Other List Methods

```python
from JsonWalker.walk import JsonPath

# Sample data for comparison
small_data = {
    "numbers": [10, 20, 30, 40, 50]
}

# list_all() - gets everything
all_path = JsonPath().key("numbers").list_all().ensure_type(int)
print("list_all():")
for num in all_path.walk(small_data):
    print(f"  {num}")

print()

# list_index() - gets single item
index_path = JsonPath().key("numbers").list_index(2).ensure_type(int)
print("list_index(2):")
for num in index_path.walk(small_data):
    print(f"  {num}")

print()

# list_slice() - gets range
slice_path = JsonPath().key("numbers").list_slice(1, 4).ensure_type(int)
print("list_slice(1, 4):")  # Gets indices 1, 2, 3 (not 4)
for num in slice_path.walk(small_data):
    print(f"  {num}")
```

```
=== list_slice: Method Comparison ===
list_all():
  10
  20
  30
  40
  50

list_index(2):
  30

list_slice(1, 4):
  20
  30
  40
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
path = JsonPath().key("users").list_all().key("profile").multi(
    JsonPath().key("firstName").ensure_type(str),
    JsonPath().key("lastName").ensure_type(str),
    JsonPath().key("age").ensure_type(int)
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
path = JsonPath().key("products").list_all().key("info").multi(
    JsonPath().key("name").ensure_type(str),
    JsonPath().key("price").ensure_type(float),
    JsonPath().key("inStock").ensure_type(bool),
    JsonPath().key("tags").list_all().ensure_type(str)
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
path = JsonPath().key('products').list_all().filter(
    condition_path=JsonPath().key('category').ensure_type(str),
    condition=lambda x: x == 'electronics'
).filter(
    condition_path=JsonPath().key('rating').ensure_type(float),
    condition=lambda x: x > 4.3
).multi(
    JsonPath().key('name').ensure_type(str),
    JsonPath().key('price').ensure_type(float)
)

for product_name, price in path.walk(data):  # Types: str, float
    print(f"{product_name}: ${price}")
```

```
=== Section 4: Filtering ===
Laptop: $999.99
```

### 5. Dictionary Iteration

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
path = JsonPath().key("scores").yield_key(JsonPath().ensure_type(int))
for subject, score in path.walk(data):  # Types: str, int
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
path = JsonPath().key('categories').yield_key(
    JsonPath().yield_key(
        JsonPath().list_all().ensure_type(str)
    )
)

for category, (subcategory, item) in path.walk(data):  # Types: str, tuple[str, str]
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
path = JsonPath().key("results").list_all().key("user").multi(
    JsonPath().key("id").ensure_type(int),
    JsonPath().key("profile").multi(
        JsonPath().key("name").ensure_type(str),
        JsonPath().key("age").ensure_type(int),
        JsonPath().key("active").ensure_type(bool),
        JsonPath().key("contacts").list_all().multi(
            JsonPath().key("type").ensure_type(str),
            JsonPath().key("value").ensure_type(str)
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

### 7. Path Composition with .add()

Use `.add()` to combine path segments for reusability while maintaining type inference.

```python
from JsonWalker.walk import JsonPath

data = {
    "current_projects": [
        {
            "name": "Website Redesign",
            "team": {
                "lead": {"name": "Alice", "email": "alice@company.com"},
                "members": [
                    {"name": "Bob", "email": "bob@company.com"},
                    {"name": "Carol", "email": "carol@company.com"}
                ]
            }
        }
    ],
    "archived_projects": [
        {
            "name": "Mobile App",
            "team": {
                "lead": {"name": "David", "email": "david@company.com"},
                "members": [
                    {"name": "Eve", "email": "eve@company.com"}
                ]
            }
        }
    ]
}

# Define different start paths
current_projects_path = JsonPath().key("current_projects").list_all()
archived_projects_path = JsonPath().key("archived_projects").list_all()

# Define common end path for extracting team member emails
team_emails_path = JsonPath().key("team").key("members").list_all().key("email").ensure_type(str)

# Combine different starts with the same end using .add()
current_team_emails = current_projects_path.add(team_emails_path)
archived_team_emails = archived_projects_path.add(team_emails_path)

# Use with type safety
print("Current project team emails:")
for email in current_team_emails.walk(data):  # Type: str
    print(f"  {email}")

print("Archived project team emails:")
for email in archived_team_emails.walk(data):  # Type: str
    print(f"  {email}")
```

```
=== Section 7: Path Composition ===
Current project team emails:
  bob@company.com
  carol@company.com
Archived project team emails:
  eve@company.com
```

## Advanced Type Safety Features

### Type Narrowing with ensure_type()

The `ensure_type()` method filters out values that don't match the expected type and provides type inference. You don't need to use it at the end of your paths- the only consequence is that your variable will just have return type of `any`. Type hinting is nice though, which is why this demo has it for all the examples.

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
string_path = JsonPath().key("mixed_values").list_all().ensure_type(str)
for value in string_path.walk(data):  # Type: str
    print(f"  String: {value}")

# Extract only numbers (integers)
print("Integers:")
int_path = JsonPath().key("mixed_values").list_all().ensure_type(int)
for value in int_path.walk(data):  # Type: int
    print(f"  Integer: {value}")

# Extract only dictionaries
print("Dictionaries:")
dict_path = JsonPath().key("mixed_values").list_all().ensure_type(dict)
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
path = JsonPath().key("users").list_all().multi(
    JsonPath().key("name").ensure_type(str),
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
path = JsonPath().key("orders").list_all().filter(
    condition_path=JsonPath().key("status").ensure_type(str),
    condition=lambda x: x == "completed"
).multi(
    JsonPath().key("id").ensure_type(str),
    JsonPath().key("customer").multi(
        JsonPath().key("name").ensure_type(str),
        JsonPath().key("vip").ensure_type(bool)
    ),
    JsonPath().key("items").list_all().multi(
        JsonPath().key("name").ensure_type(str),
        JsonPath().key("price").ensure_type(float),
        JsonPath().key("quantity").ensure_type(int)
    ),
    JsonPath().key("total").ensure_type(float)
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
| `.key(name, default=None)` | Access dictionary by key with optional default | `.key("users")` | `_KeyPath[Any]` |
| `.list_index(index)` | Access list by specific index | `.list_index(0)` | `_IndexPath[Any]` |
| `.list_slice(start, end)` | Access range of list items | `.list_slice(1, 5)` | `_SlicePath[Any]` |
| `.list_all()` | Access all items in a list | `.list_all()` | `_SlicePath[Any]` |

### Type Safety Methods

| Method | Description | Example | Type Return |
|--------|-------------|---------|-------------|
| `.ensure_type(type_class)` | Ensure value matches expected type | `.ensure_type(str)` | `_ensure_typePath[T]` |

### Advanced Methods

| Method | Description | Example | Type Return |
|--------|-------------|---------|-------------|
| `.filter(condition_path, condition)` | Filter results based on a condition | `.filter(JsonPath().key('status'), lambda x: x == 'active')` | `_FilteredPath[T]` |
| `.yield_key(valuePath)` | Iterate through key-value pairs | `.yield_key(JsonPath().ensure_type(str))` | `_YieldedKeyPlusValuePath[tuple[str, T]]` |
| `.multi(*paths)` | Get multiple values from current context | `.multi(path1, path2)` | `_MultiValuePath[tuple[...]]` |
| `.add(path)` | Combine current path with another path segment | `.add(JsonPath().key("name"))` | `_Executor[T]` |

## Best Practices

1. **Start simple**: Begin with basic `.key()` and `.list_all()` operations
2. **Use meaningful variable names**: The fluent API makes code self-documenting
3. **Provide defaults**: Use the `default` parameter to handle missing keys gracefully
4. **Break complex queries**: Split very long chains into intermediate variables for readability
5. **Leverage .add()**: Create reusable path segments with path composition
6. **Filter early**: Apply filters as early as possible in your path to improve performance
7. **Use multi strategically**: When you need multiple related values, `.multi()` is more efficient than separate queries
8. **Handle mixed types**: Use `ensure_type()` to filter and work with specific types. This will also give your IDE the ability to infer types when using the `walk` function