# Conveyor

Library for creating pipeline-oriented systems



## Why

* Simplicity
* Maintainability
* Scalability



## Key concepts

### [Item](conveyor/core/Item.py)

**Information** unit conveyor operates on

Each item has:

| name               | description                                 |
| ------------------ | ------------------------------------------- |
| data.digest        | constant unique identifier for item         |
| chain              | constant unique identifier for item's chain |
| type               | constant common identifier                  |
| status             | variable common identifier                  |
| data.value         | constant data                               |
| metadata           | variable data                               |
| created            | when was item created                       |
| reserved           | id of worker reserved item if any           |

### [Repository](conveyor/core/Repository.py)

**Storage** interface

### Worker

**Program** unit that operates on items

All workers should be inherited from [abstract workers](#abstract-workers)

### [Effect](conveyor/core/Effect.py)

**Decorator**-like class for adding methods calls logging



## Abstract Workers

|                                                | takes arguments | gets item | creates items | changes item status | changes item metadata | deletes item |
|------------------------------------------------|:---------------:|:---------:|:-------------:|:-------------------:|:---------------------:|:------------:|
| [Creator](conveyor/core/Creator.py)            |        +        |           |       +       |                     |                       |              |
| [Transformer](conveyor/workers/Transformer.py) |                 |     1     |               |          +          |           +           |              |
| [Mover](conveyor/workers/Mover.py)             |                 |     1     |       +       |          +          |                       |              |
| [Destroyer](conveyor/workers/Destroyer.py)     |                 |     1     |               |                     |                       |       +      |
| [Synthesizer](conveyor/workers/Synthesizer.py) |                 |     2     |       +       |          +          |                       |              |



## Repositories

### [Treegres](conveyor/repositories/Treegres)

Stores `Item.data` in files in **directories tree**

Stores the rest of `Item` in **peewee compatible database**



## Effects

### [SimpleLogging](conveyor/repository_effects/SimpleLogging)

Logs repository actions **to stderr**

### [DbLogging](conveyor/repository_effects/DbLogging)

Logs repository actions **to peewee compatible database**

### [ExceptionLogging](conveyor/processor_effects/ExceptionLogging/ExceptionLogging.py)

Logs worker exceptions **to stderr**

### [DbLogging](conveyor/processor_effects/ExceptionDbLogging/ExceptionDbLogging.py)

Logs worker exceptions **to peewee compatible database**