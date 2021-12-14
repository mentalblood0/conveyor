# Conveyor

Library for creating cold-pipeline-oriented systems

Cold pipeline is a pipeline which state stored in external database

## Workers classes

* [Creator](conveyor/workers/Creator.py)
* [Transformer](conveyor/workers/Transformer.py)
* [Mover](conveyor/workers/Mover.py)
* [Destroyer](conveyor/workers/Destroyer.py)

## Item repositories classes

* [DefaultItemRepository](conveyor/item_repositories/DefaultItemRepository.py) -- uses PostgreSQL database for storing metadata and directories tree for storing files

## Example

* [Workers description](tests/example_workers.py)
* [Pipeline description](tests/test_pipeline.py)

