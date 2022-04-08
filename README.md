# Conveyor

Library for creating cold-pipeline-oriented systems

Cold pipeline is a pipeline which state stored in external database



## Why

* Simplicity
* Maintainability
* Scalability



## Key concepts

### [Item](conveyor/core/Item.py)

**Unit** of information conveyor operates on

Each item has:

| name     | type       | description                                        |
| -------- | ---------- | ---------------------------------------------------|
| chain_id | string     | constant unique identifier for every item in chain |
| id       | string     | constant unique identifier                         |
| type     | string     | constant common identifier                         |
| status   | string     | variable common identifier                         |
| data     | string     | constant storage                                   |
| metadata | dictionary | variable storage                                   |

### [Repository](conveyor/core/Repository.py)

**Interface** to where items are stored

### Worker

**Program** unit that operates on items

All workers classes should be inherited from [abstract workers](#abstract-workers)

### [Effect](conveyor/core/Effect.py)

**Decorator**-like class for adding logging to `Repository`-inherited classes



## Abstract Workers

### [Creator](conveyor/core/Creator.py)

Strictly speaking, `Creator` is not a worker (not inherited from `Worker`)

**Takes** some arguments

**Creates** item with type and status given in self class description

### [Transformer](conveyor/workers/Transformer.py)

Takes **no arguments**

**Gets** item with type and status given in self class description

**Changes** item status and metadata

### [Mover](conveyor/workers/Mover.py)

Takes **no arguments**

**Gets** item with fixed type and status

**Creates** one or more item of type and status given in self class description

**Changes** taken item status

### [Destroyer](conveyor/workers/Destroyer.py)

Takes **no arguments**

**Gets** item with type and status given in self class description

**Deletes** it



## Repositories

### [Treegres](conveyor/repositories/Treegres)

Stores `Item.data` in files in directories tree

Stores the rest of `Item` in peewee compatible database



## Effects

### [SimpleLogging](conveyor/repository_effects/SimpleLogging)

Logs repository actions to stderr

### [DbLogging](conveyor/repository_effects/DbLogging)

Logs repository actions to peewee compatible database



## Example

* [Workers description](tests/example_workers.py)
* [Pipelines description](tests/test_pipeline.py)