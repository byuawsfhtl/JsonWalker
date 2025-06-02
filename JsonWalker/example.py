from JsonWalker.walk import JsonPath

# Usage examples
if __name__ == "__main__":
    # Example 1: Simple path with context
    # Equivalent to: 'key1[*]^ | key2(-1;int)' in legacy json walker
    data = {
        "key1": [
            {
                "key2": 100
            },
            {}
        ]
    }
    path = JsonPath().key("key1").listAll().addContext().key("key2", default=-1)
    for valOfKey1, key2 in path.walk(data):
        print(f"valOfKey1: {valOfKey1}, key2: {key2}")
    print('--------------------------------------')
    

    # Example 2: Multi-value return
    # Equivalent to: 'key1 | key2 | item1, item2' in legacy json walker
    data2 = {
        "key1": {
            "key2": {
                "item1": "hello",
                "item2": "world"
            }
        }
    }
    path = JsonPath().key("key1").addContext().key("key2").multi(
        JsonPath().key("item1"),
        JsonPath().key("item2")
    )    
    for context, item1, item2 in path.walk(data2):
        print(f"{item1} {item2}")
    print('--------------------------------------')
    
    
    # Example 3: dictionary iteration
    # Equivalent to: 'key1{*}' in legacy json walker
    data3 = {
        "key1": {
            "key2": "value2",
            "key3": "value3",
            "key4": "value4"
        }
    }
    path = JsonPath().key("key1").keyContextAndValue()
    for key, value in path.walk(data3):
        print(f"{key} -- {value}")
    print('--------------------------------------')