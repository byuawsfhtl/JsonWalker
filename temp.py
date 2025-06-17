#!/usr/bin/env python3
"""
JsonWalker Code Examples
========================

This file contains all the code examples from the JsonWalker documentation
organized by section for easy testing and experimentation.

To run these examples, make sure you have JsonWalker installed:
pip install JsonWalker
"""

from JsonWalker.walk import JsonPath

def basic_usage_pattern():
    """Basic Usage Pattern from Quick Start"""
    print("\n=== Basic Usage Pattern ===")
    
    data = {
        "users": [
            {"name": "Alice"},
            {"name": "Bob"},
            {"name": "Charlie"}
        ]
    }

    # Create a path with type inference
    path = JsonPath().key("users").list_all().key("name").ensure_type(str)

    # Use in a for loop - IDE knows 'name' is a string
    for name in path.walk(data):
        print(f"User: {name}")

    # Or get single values
    first_name = next(path.walk(data))
    print(f"First user: {first_name}")


def section_1_basic_key_access():
    """1. Basic Key Access with Type Safety"""
    print("=== Section 1: Basic Key Access with Type Safety ===")
    
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
        print(f"Name: {name}")  # Output: John
        
    # Access user's age with type inference
    age_path = JsonPath().key("user").key("age").ensure_type(int)
    for age in age_path.walk(data):  # IDE knows 'age' is int
        print(f"Age: {age}")  # Output: Age: 30


def section_1_handling_missing_keys():
    """1. Handling Missing Keys with Defaults and Type Safety"""
    print("\n=== Section 1: Handling Missing Keys ===")
    
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
        print(f"Name: {name}")  # Output: John, Jane, Unknown


def section_2_working_with_lists():
    """2. Working with Lists and Type Safety"""
    print("\n=== Section 2: Working with Lists and Type Safety ===")
    
    data = {
        "fruits": ["apple", "banana", "cherry"]
    }

    path = JsonPath().key("fruits").list_all().ensure_type(str)
    for fruit in path.walk(data):  # IDE knows 'fruit' is str
        print(f"Fruit: {fruit}")  # Output: apple, banana, cherry


def section_2_specific_list_index():
    """2. Specific List Index with Type Safety"""
    print("\n=== Section 2: Specific List Index ===")
    
    data = {
        "numbers": [0, 1, 2, 3, 4, 5],
        "scores": [95.5, 87.2, 92.8]
    }

    # Get first number as integer
    path = JsonPath().key("numbers").list_index(0).ensure_type(int)
    first_number = next(path.walk(data))  # Type: int
    print(f"First number: {first_number}")  # Output: 0

    # Get first score as float
    score_path = JsonPath().key("scores").list_index(0).ensure_type(float)
    first_score = next(score_path.walk(data))  # Type: float
    print(f"First score: {first_score}")  # Output: 95.5


def section_3_basic_multi():
    """3. Basic Multi Example with Type Inference"""
    print("\n=== Section 3: Basic Multi Example ===")
    
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


def section_3_complex_multi():
    """3. Complex Multi with Nested Types"""
    print("\n=== Section 3: Complex Multi with Nested Types ===")
    
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


def section_4_filtering():
    """4. Filtering with Type Safety"""
    print("\n=== Section 4: Filtering with Type Safety ===")
    
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


def section_5_dictionary_iteration():
    """5. Dictionary Iteration with Type Safety"""
    print("\n=== Section 5: Dictionary Iteration ===")
    
    data = {
        "scores": {
            "math": 95,
            "science": 87,
            "english": 92
        }
    }

    # Iterate through all key-value pairs with type safety
    path = JsonPath().key("scores").multi(
        JsonPath(),
        JsonPath().yield_key(
            JsonPath().ensure_type(int)
        )
    )
    for context, (subject, score) in path.walk(data):
        print(context)
        print(subject, score)

def section_5_complex_dictionary_iteration():
    """5. More Complex Dictionary Iteration with Type Safety"""
    print("\n=== Section 5: Complex Dictionary Iteration ===")
    
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
    
    for category, (subcategory, item) in path.walk(data):
        print(f"{category} > {subcategory} > {item}")


def section_6_real_world_example():
    """6. Real-World Example: Processing API Response with Full Type Safety"""
    print("\n=== Section 6: Real-World API Response Example ===")
    
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


def section_7_path_joining():
    """7. Path Joining with Type Safety"""
    print("\n=== Section 7: Path Joining ===")
    
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
    departments_path = JsonPath().key("departments").list_all()
    employees_path = JsonPath().key("employees").list_all()

    name_path = company_path.add(departments_path).add(employees_path).add(JsonPath().key("name").ensure_type(str))
    salary_path = company_path.add(departments_path).add(employees_path).add(JsonPath().key("salary").ensure_type(int))

    # Use with type safety
    print("Employee names:")
    for name in name_path.walk(data):  # Type str
        print(f"  Employee: {name}")
    
    print("Employee salaries:")
    for salary in salary_path.walk(data):  # Type int
        print(f"  Salary: ${salary:,}")

def advanced_type_narrowing():
    """Advanced Type Safety: Type Narrowing with ensure_type()"""
    print("\n=== Advanced: Type Narrowing ===")
    
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


def advanced_optional_values():
    """Advanced Type Safety: Working with Optional Values"""
    print("\n=== Advanced: Optional Values ===")
    
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


def complete_example():
    """Complete Type-Safe Data Processing Example"""
    print("\n=== Complete Example: E-commerce Data Processing ===")
    
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

def run_all_examples():
    """Run all examples in order"""
    print("JsonWalker Code Examples - Running all examples...\n")
    
    # Basic examples
    basic_usage_pattern()
    section_1_basic_key_access()
    section_1_handling_missing_keys()
    section_2_working_with_lists()
    section_2_specific_list_index()
    
    # Multi-value examples
    section_3_basic_multi()
    section_3_complex_multi()
    
    # Advanced features
    section_4_filtering()
    section_5_dictionary_iteration()
    section_5_complex_dictionary_iteration()
    section_6_real_world_example()
    section_7_path_joining()
    
    # Advanced type safety
    advanced_type_narrowing()
    advanced_optional_values()
    
    # Complete example
    complete_example()
    
    print("\n=== All examples completed! ===")


if __name__ == "__main__":
    try:
        run_all_examples()
    except ImportError as e:
        print(f"Error: {e}")
        print("\nMake sure JsonWalker is installed:")
        print("pip install JsonWalker")
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()