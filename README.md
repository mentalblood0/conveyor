<h1 align="center">🧮 conveyor</h1>

<h3 align="center">library for creating pipeline-oriented systems</h3>

<p align="center">
<a href="https://github.com/MentalBlood/conveyor/actions/workflows/lint.yml"><img alt="Lint Status" src="https://github.com/MentalBlood/conveyor/actions/workflows/lint.yml/badge.svg"></a>
<a href="https://github.com/MentalBlood/conveyor/actions/workflows/typing.yml"><img alt="Typing Status" src="https://github.com/MentalBlood/conveyor/actions/workflows/typing.yml/badge.svg"></a>
<a href="https://github.com/MentalBlood/conveyor/actions/workflows/complexity.yml"><img alt="Complexity Status" src="https://github.com/MentalBlood/conveyor/actions/workflows/complexity.yml/badge.svg"></a>
<a href="https://github.com/MentalBlood/conveyor/actions/workflows/tests.yml"><img alt="Tests Status" src="https://github.com/MentalBlood/conveyor/actions/workflows/tests.yml/badge.svg"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

## Why

* Simplicity
* Maintainability
* Scalability

## Key concepts

### [Item](conveyor/core/Item/Item.py)

**Information** unit conveyor operates on

Each item has:

| name               | description                                 |
| ------------------ | ------------------------------------------- |
| chain              | constant unique identifier for item's chain |
| type               | constant common identifier                  |
| status             | variable common identifier                  |
| data               | constant data                               |
| metadata           | variable data                               |
| created            | when was item created                       |
| reserved           | id of worker reserved item if any           |

### [Repository](conveyor/core/Repository/Repository.py)

**Storage** interface

Each repository consists of some [part repositories](conveyor/core/Repository/PartRepository.py)

### [Worker](conveyor/core/Worker/Worker.py)

**Program** unit that operates on items

Each worker consists of given

0. [Repository](conveyor/core/Repository/Repository.py)
1. [Receiver](conveyor/core/Worker/Receiver.py)
2. [Processor](conveyor/core/Worker/Processor.py)
3. [Actor](conveyor/core/Worker/Action.py)