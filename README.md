# JsonWalker

_Allows simple, quick, and easy use of nested Json_

JsonWalker's goal is to allow the user to specify a path through nested json, and get the items at each match in the json. Currently, it only outputs generators.

## Installation

JsonWalker is a pip installable package. It is a public package, and will thus not need any special permissions to install.

### Command Line Installation

To install from the command line, `pip install git+https://github.com/byuawsfhtl/JsonWalker.git`.

### Use in other pip packages

As this is a public package, it can be added to the required packages of any pip installable packages and will be installed automatically when those are installed in other projects.

## Usage

To use this in a project, install using one of the installation methods shown above.

Import the walk command into your file: `from JsonWalker.walk import walk`

As the walk command makes a generator, it can be used in multiple ways.

### Use in a for loop

```python
for context1, context2, item1, item2 in walk(json, path):
    ...
```

### Use outside of a for loop

```python
context1, context2, item1, item2 = next(walk(json, path))
```

The next function is a python function that gets the "next" value in the generator, and can be called multiple times in a row if desired.

## Paths

JsonWalker has its own syntax for the path provided for walking through nested json.

Below are the symbols used and some example usages

| Symbol | Meaning                                                                      |
| ------ | ---------------------------------------------------------------------------- |
| \|     | A path divider, used to organize path sections                               |
| \[     | The beginning of an index specification                                      |
| \]     | The end of an index specification                                            |
| \:     | Index range indicator                                                        |
| \(     | The beginning of a default specification                                     |
| \)     | The end of a default specification                                           |
| \;     | Used to separate a default value and its type                                |
| \,     | The delimiter for the multi item return syntax                               |
| \>     | A continuing symbol for the multi item return syntax that works much like \| |
| \^     | Raises the current item as a context of the path                             |
| \*     | The wildcard symbol for the index and dict iteration specifications          |
| \{     | The beginning of a dict iteration specifictation                             |
| \}     | The end of a dict iteration specifictation                                   |

### Examples

#### Simple

```json
{
  "key1": [
    {
      "key2": 100
    },
    {}
  ]
}
```

The following path can be used to iterate through the json, getting the 'key2' value out and raising the current key1 item as a context

`'key1[*]^ | key2(-1;int)'`

It would be called as such

```python
for key1Val, key2 in walk(json, 'key1[*]^ | key2(-1;int)'):
    print(key2)
```

and would output

```cmd
100
-1
```

with key1Val being the current item inside of the key1 list

##### Path Breakdown

First Part
`'key1[*]^'`

The key 'key1' is accessed, returning the inner list.

Then, the index specifier tells JsonWalker to iterate over all values in the list.

Finally, the current value in the iteration of the list is raised as a context.

Second Part
`'key2(-1;int)'`

The key 'key2' is accessed, returning the value at that spot in the current dictionary.

If 'key2' is not a key in the dictionary, then the default specification `'(-1;int)'` is used. In this case, it returns -1 when 'key2' does not exist.

#### Multi Item Return

```json
{
  "key1": {
    "key2": {
      "item1": "hello",
      "item2": "world"
    }
  }
}
```

The following path would iterate through the json, returning item1 and item2 as values, with the outer key1 dictionary as the context

`'key1^ | key2 | item1, item2'`

It would be called as such

```python
for context, item1, item2 in walk(json, 'key1^ | key2 | item1, item2'):
    print(item1 + " " + item2)
```

and would output

```cmd
hello world
```

#### Range specification

```json
{
  "key1": [
    {
      "item": "do not want"
    },
    {
      "item": "hello"
    },
    {
      "item": "world"
    }
  ]
}
```

The following path would iterate through the json, only looking in the given range of the key1 list, outputing the 'item' key values

`'key1[1:*] | item'`

It would be called as such

```python
for item in walk(json, 'key1[1:*] | item'):
    print(item)
```

and would output

```cmd
hello
world
```

#### Multi Value Continue

```json
{
  "key1": {
    "key2": {
      "item1": "hello"
    },
    "key3": {
      "item2": "world"
    },
    "key4": {
      "item4": "not accessing"
    }
  }
}
```

The following path would iterate through the json, returing the three different items that have diverging paths

`'key1 | key2 > item1(''), key3 > item2(''), key4 > item3('')'`

It would be called as such

```python
for item1, item2, item3 in walk(json, 'key1 | key2 > item1(''), key3 > item2(''), key4 > item3('')'):
    print(item1)
    print(item2)
    print(item3)
```

and would output

```cmd
hello
world

```

##### Path Explanation

First Part
`'key1'`

The given json is accessed at the key1 key.

Second Part
`'key2 > item1('';str), key3 > item2('';str), key4 > item3('';str)'`

This part of the path specifies three different return items, as shown by the 2 commas separating the three sections.

Each section does the following:

Accesses the key before the >, accesses the key following the > on the item retrieved before the > and returns the default if the key does not exist on the previous item.

#### Dict Iteration

```json
{
  "key1": {
    "key2": "value2",
    "key3": "value3",
    "key4": "value4"
  }
}
```

The following path would iterate through the json, returning the key as a context and the value as a value

`'key1{*}'`

It would be called as such

```python
for key, value in walk(json, 'key1{*}'):
    print(f"{key} -- {value}")
```

and would output

```cmd
key2 -- value2
key3 -- value3
key4 -- value4
```

##### Path Explanation

First Part:
`'key1'`

The given json is accessed at key1

Second Part:
`'{*}'`

The value at `'key1'` is iterated through, puting the key in the context list and the value as the current value

#### Involved Example and Demonstration of use benefits

Old Python Code

```python
persons = arkInfo.get('persons', [])
familyId = ''
for person in persons:
    for name in person.get('names', []):
        for nameForms in name.get('nameForms', []):
            for parts in nameForms.get('parts', []):
                for fields in parts.get('fields', []):
                    for value in fields.get('values', []):
                        labelID: str = value.get('labelId', '')
                        if 'PR' in labelID and 'FTHR' not in labelID and 'MTHR' not in labelID:
                            arkPerson = person
                            headID = person.get('id', '')
                            personLinks = person.get('links', {})
                            persona = personLinks.get('persona', {})
                            href = persona.get('href', '')
                            if ark not in href:
                                hrefPersonaSplit = href.split('personas/')[1]
                                familyId = hrefPersonaSplit.split('?flag')[0]
                                isHead = False
                            familyId = ark
                            return headTuple(ark=ark, arkPerson=arkPerson, isHead=isHead, headID=headID, familyId=familyId)

    for fields in person.get('fields', {}):
        for values in fields.get('values', {}):
            text = values.get('text', '')
            if 'Head' in text or 'Глава' in text: #'Глава' is head in russian
                personLinks = person.get('links', {})
                persona = personLinks.get('persona', {})
                href = persona.get('href', '')
                if ark not in href:
                    hrefPersonaSplit = href.split('personas/')[1]
                    familyId = hrefPersonaSplit.split('?flag')[0]
                    isHead = False
                arkPerson = person
                familyId = ark
                return headTuple(ark=ark, arkPerson=arkPerson, isHead=isHead, headID=headID, familyId=familyId)

if persons:
    arkPerson = persons[0]
    headID = arkPerson.get('id', '')
    href = arkPerson.get('links', {}).get('persona', {}).get('href', '')
    splitId = href.split('personas/')
    if len(splitId) > 1:
        familyId = splitId[1].split('?flag')[0]
    else:
        familyId = ark
```

With JsonWalker

```python
for person, headID, href in walk(arkInfo, 'persons[*]^ | id, links > persona > href('';str)'):
    for _, labelID in walk(person, 'names[*]^ | nameForms[*] | parts[*] | fields[*] | values[*] | labelId('';str)'):
        if 'PR' not in labelID or 'FTHR' in labelID or 'MTHR' in labelID:
            continue
        arkPerson = person
        if ark not in href:
            hrefPersonaSplit = href.split('personas/')[1]
            familyId = hrefPersonaSplit.split('?flag')[0]
            isHead = False
        familyId = ark
        return headTuple(ark=ark, arkPerson=arkPerson, isHead=isHead, headID=headID, familyId=familyId)

    for _, text in walk(person, "fields[*]^  | values[*] | text('';str)"):
        if 'Head' not in text and 'Глава' not in text: #'Глава' is head in russian
            continue
        if ark not in href:
            hrefPersonaSplit = href.split('personas/')[1]
            familyId = hrefPersonaSplit.split('?flag')[0]
            isHead = False
        arkPerson = person
        familyId = ark
        return headTuple(ark=ark, arkPerson=arkPerson, isHead=isHead, headID=headID, familyId=familyId)

familyId = ''
for person, href in walk(arkInfo, 'persons[0]^|links|persona|href'):
    headID = person.get('id', '')
    splitId = href.split('personas/')
    if len(splitId) > 1:
        familyId = splitId[1].split('?flag')[0]
    else:
        familyId = ark
```

## Some Constraints

1. Indexes must be in the form [n] or [n:m]
2. Defaults must be in the form (value;type)
3. MultiValues must be in the form value1, value2, ...
4. The MultiValue must be the last path in the string
5. The MultiValue must not contain a path divider, it instead uses a comma for separation and a greater than sign for continuation
6. The MultiValue must not contain another MultiValue
7. The Index must have a specific index if it is used in a MultiValue
8. The MultiValue must not contain a DictIter or an Index with a wildcard
9. In order to iterate through a list, a index/range must be specified
10. The Default must contain a type
11. Items leave the generator in this order, where their internal order is specified by order in the path: Contexts, Values
12. DictIters must be {\*}
