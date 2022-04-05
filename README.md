# Conveyor

Library for creating cold-pipeline-oriented systems

Cold pipeline is a pipeline which state stored in external database


## Key concepts

### [Item](conveyor/core/Item.py)

Unit of information conveyor operates on

Each item has:

|          | type   | constant | purpose                              |
|----------|--------|----------|--------------------------------------|
| id       | string | constant | unique identifier                    |
| type     | string | constant | grouping                             |
| status   | string | variable | processing progress identifier       |
| data     | string | constant | storing something                    |
| metadata | any    | variable | storing something computed from data |

### [Repository](conveyor/core/Repository.py)

Interface to items storage

### [Worker](conveyor/core/Worker.py)

Program unit that operates on items

### [Effect](conveyor/core/Effect.py)

Decorator-like class for adding logging to `Repository`-inherited classes


## Workers

### [Creator](conveyor/core/Creator.py)

Strictly speaking, `Creator` is not a worker (not inherited from `Worker`)

**Takes** some arguments

**Creates** item with fixed type and status

### [Transformer](conveyor/workers/Transformer.py)

**Gets** item with fixed type and status

**Changes** item status and metadata

### [Mover](conveyor/workers/Mover.py)

**Gets** item with fixed type and status

**Creates** one or more item of fixed type and status

**Changes** taken item status

### [Destroyer](conveyor/workers/Destroyer.py)

**Gets** item with fixed type and status

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