# Conveyor

Library for creating cold-pipeline-oriented systems

Cold pipeline is a pipeline which state stored in external database

## Dependencies

* peewee
* blake3
* logama
* growing-tree-base

## Workers

### [Transformer](conveyor/workers/Transformer.py)

Takes item with fixed type and status

Changes item status and metadata

### [Mover](conveyor/workers/Mover.py)

Takes item with fixed type and status

Creates one or more item of fixed type and status

Changes taken item status

### [Destroyer](conveyor/workers/Destroyer.py)

Deletes item with fixed type and status

## Repositories classes

* [Treegres](conveyor/repositories/Treegres) -- uses peewee compatible (should also support indexes) database for storing metadata, and directories tree for storing files

## RepositoryEffect classes

* [SimpleLogging](conveyor/repository_effects/SimpleLogging) -- logs repository actions to stderr
* [DbLogging](conveyor/repository_effects/DbLogging) -- logs repository actions to peewee compatible database

## Example

* [Workers description](tests/example_workers.py)
* [Pipeline description](tests/test_pipeline.py)