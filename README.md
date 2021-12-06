# Conveyor

Library for creating conveyor-oriented systems

## Main classes

### Transformer

Abstract class for describing entities which:

1. Take `something` matching it's status
2. Do some stuff
3. Set new status for `something`

It's constructor takes `InputProvider`. In this case, `InputProvider`'s `get` method should take `status` string and return `ComplexDataProvider`, which should have `status` field of both classes `InputProvider` (to get current status) and `OutputProvider` (to set new status)