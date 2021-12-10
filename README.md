# Conveyor

Library for creating cold-pipeline-oriented systems

## Workers classes

* `Creator`
* `Transformer`
* `Mover`
* `Destroyer`

## Item repositories classes

* `DefaultItemRepository` -- uses PostgreSQL database for storing metadata and dir tree for storing files

## Example

See `tests/example_workers.py` and `tests/test_pipeline.py`