# Conveyor

Library for creating pipeline-oriented systems



## Why

* Simplicity
* Maintainability
* Scalability



## Key concepts

### [Item](conveyor/core/Item/Item.py)

**Information** unit conveyor operates on

Each item has:

| name               | description                                 |
| ------------------ | ------------------------------------------- |
| chain              | constant unique identifier for item's chain |
| type               | constant common identifier                  |
| status             | variable common identifier                  |
| data               | constant data                               |
| metadata           | variable data                               |
| created            | when was item created                       |
| reserved           | id of worker reserved item if any           |

### [Repository](conveyor/core/Repository/Repository.py)

**Storage** interface

Each repository consists of some [part repositories](conveyor/core/Repository/PartRepository.py)

### [Worker](conveyor/core/Worker/Worker.py)

**Program** unit that operates on items

Each worker consists of given

0. [Repository](conveyor/core/Repository/Repository.py)
1. [Receiver](conveyor/core/Worker/Receiver.py)
2. [Processor](conveyor/core/Worker/Processor.py)
3. [Actor](conveyor/core/Worker/Processor.py)