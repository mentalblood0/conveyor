# Conveyor

Library for creating cold-pipeline-oriented systems

Cold pipeline is a pipeline which state stored in external database

## Dependencies

* peewee
* blake3
* logama
* growing-tree-base

## Workers classes

* [Creator](conveyor/workers/Creator.py)
* [Transformer](conveyor/workers/Transformer.py)
* [Mover](conveyor/workers/Mover.py)
* [Destroyer](conveyor/workers/Destroyer.py)

### Factories

* [DestroyerFactory](conveyor/workers/factories/DestroyerFactory.py)

## Repositories classes

* [Treegres](conveyor/repositories/Treegres.py) -- uses peewee compatible (should also support indexes) database for storing metadata, and directories tree for storing files

## RepositoryEffect classes

* [SimpleLogging](conveyor/repository_effects/SimpleLogging.py) -- logs repository actions to stderr
* [DbLogging](conveyor/repository_effects/DbLogging.py) -- logs repository actions to peewee compatible database

## Example

* [Workers description](tests/example_workers.py)
* [Pipeline description](tests/test_pipeline.py)