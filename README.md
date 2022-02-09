# Conveyor

Library for creating cold-pipeline-oriented systems

Cold pipeline is a pipeline which state stored in external database

## Workers classes

* [Creator](conveyor/workers/Creator.py)
* [Transformer](conveyor/workers/Transformer.py)
* [Mover](conveyor/workers/Mover.py)
* [Destroyer](conveyor/workers/Destroyer.py)

## Repositories classes

* [Treegres](conveyor/repositories/Treegres.py) -- uses Peewee compatible (should also support indexes) database for storing metadata, and directories tree for storing files

## RepositoryEffect classes

* [SimpleLogging](conveyor/repository_effects/SimpleLogging.py) -- logs repository actions to stderr
* [DbLogging](conveyor/repository_effects/DbLogging.py) -- logs repository actions to Peewee compatible database

## Example

* [Workers description](tests/example_workers.py)
* [Pipeline description](tests/test_pipeline.py)