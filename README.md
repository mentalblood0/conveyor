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

| name     | type       | description                                        |
| -------- | ---------- | ---------------------------------------------------|
| chain_id | string     | constant unique identifier for every item in chain |
| type     | string     | constant common identifier                         |
| id       | string     | constant in-`type`-unique identifier               |
| status   | string     | variable common identifier                         |
| data     | string     | constant storage                                   |
| metadata | dictionary | variable storage                                   |

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



## Example

* [Workers description](tests/example_workers.py)
* [Pipelines description](tests/test_pipeline.py)