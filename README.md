# Conveyor

Library for creating cold-pipeline-oriented systems

Cold pipeline is a pipeline which state stored in external database



## Why

* Simplicity
* Maintainability
* Scalability



## Key concepts

### [Item](conveyor/core/Item.py)

**Information** unit conveyor operates on

Each item has:

| name               | type               | description                                 |
| ------------------ | ------------------ | ------------------------------------------- |
| data.digest.string | string             | constant unique identifier for item         |
| chain.value        | string             | constant unique identifier for item's chain |
| type               | string             | constant common identifier                  |
| status             | string             | variable common identifier                  |
| Data.value         | string             | constant storage                            |
| metadata           | dictionary         | variable storage                            |
| created            | datetime           | datetime when item was created              |
| reserved           | optional string    | id of worker reserved this item if any      |

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