## ADDED Requirements

### Requirement: NATS request/reply for the gateway edge

The gateway↔service edge SHALL use NATS request/reply: the HTTP-facing create,
read, update, and delete operations of each domain are served on a dedicated
subject namespaced by domain and operation (e.g. `budget.create`,
`category.list`, `transaction.get`). The API gateway SHALL be the caller of
these subjects. Services SHALL NOT call each other over HTTP.

#### Scenario: A service handles a request on its subject

- **WHEN** a request message is published to an operation's subject
- **THEN** the owning service processes it and publishes a reply to the
  request's reply subject

#### Scenario: No reply within the timeout

- **WHEN** a caller issues a request and no reply arrives before the configured
  timeout
- **THEN** the caller treats the operation as failed rather than waiting
  indefinitely

### Requirement: Request/reply message envelope

Every request payload SHALL be JSON containing the operation's input fields,
including identifiers that were previously URL path parameters. Every reply
SHALL be a JSON envelope that is either a success envelope
`{"ok": true, "data": <payload>}` or an error envelope
`{"ok": false, "error": {"status": <http-status-code>, "detail": <string>}}`.

#### Scenario: Successful operation

- **WHEN** a service completes an operation successfully
- **THEN** it replies with `ok` set to true and the result under `data`

#### Scenario: Failed operation

- **WHEN** a service operation fails a domain rule or finds no entity
- **THEN** it replies with `ok` set to false and an `error` object carrying the
  HTTP status code and a human-readable detail

### Requirement: Error mapping preserves REST semantics

The error envelope's `status` and `detail` SHALL carry the same HTTP status
code and message the monolith raised via `HTTPException` for the equivalent
condition, so callers can reproduce the original REST response.

#### Scenario: Missing entity

- **WHEN** an operation references an entity that does not exist
- **THEN** the error envelope carries status `404` and a detail naming the
  missing entity

#### Scenario: Domain rule violation

- **WHEN** an operation violates a domain rule (e.g. an out-of-range date)
- **THEN** the error envelope carries status `422` and a detail describing the
  violation

### Requirement: Domain events for inter-service communication

Inter-service communication SHALL be event-driven. After every successful state
change a domain service SHALL publish a domain event on a subject named
`<domain>.<change>` — `created`, `updated`, or `deleted` (e.g.
`budget.created`, `category.deleted`). The event payload SHALL be a JSON
envelope `{"event": "<domain>.<change>", "data": <entity-state>}`, where `data`
carries the full entity for `created`/`updated` and at least the entity id for
`deleted`. A service SHALL NOT block its request/reply response on the delivery
of an event.

#### Scenario: State change publishes an event

- **WHEN** a domain service successfully creates, updates, or deletes an entity
- **THEN** it publishes the corresponding `<domain>.<change>` event with the
  entity state in the event envelope

#### Scenario: Event delivery is independent of the reply

- **WHEN** an operation's request/reply response has been sent
- **THEN** event publication has occurred or will occur without delaying that
  response

### Requirement: Projection consumers tolerate redelivery

A projection consumer SHALL apply events idempotently, so that an event
delivered more than once (at-least-once delivery) does not corrupt the
local read-model projection it maintains from another domain's events. On
startup a consumer SHALL be able to operate with whatever projection state it
has persisted.

#### Scenario: Duplicate event delivered

- **WHEN** a consumer receives the same domain event twice
- **THEN** the resulting projection state is the same as if it had been
  received once

#### Scenario: Consumer starts with existing projection

- **WHEN** a consuming service restarts
- **THEN** it resumes from its persisted projection rather than requiring a
  full replay before serving requests
