# api-gateway Specification

## Purpose
TBD - created by archiving change split-application-to-microservices. Update Purpose after archive.
## Requirements
### Requirement: Gateway preserves the existing REST contract

The system SHALL provide an HTTP API gateway that exposes the same REST routes
the monolith exposed — `/budgets`, `/categories`, `/transactions`, and
`/health` — with the same paths, methods, request bodies, status codes, and
response shapes. The React frontend and its API client SHALL require no
changes.

#### Scenario: An existing REST request still works

- **WHEN** the frontend sends a request to a route that existed in the monolith
- **THEN** the gateway responds with the same status code and response body
  shape the monolith would have returned

#### Scenario: CORS is preserved

- **WHEN** the browser frontend on its configured origin calls the gateway
- **THEN** the gateway returns CORS headers permitting that origin, as the
  monolith did

### Requirement: Gateway translates HTTP to NATS request/reply

For each REST request the gateway SHALL issue a NATS request to the
corresponding domain subject, await the reply, and translate the reply envelope
into an HTTP response. A success envelope SHALL produce the route's normal
success status and body; an error envelope SHALL produce an HTTP response with
the envelope's `status` and `detail`.

#### Scenario: Domain service returns an error envelope

- **WHEN** a domain service replies with an error envelope
- **THEN** the gateway returns an HTTP response carrying that envelope's status
  code and detail

#### Scenario: Domain service is unreachable

- **WHEN** a NATS request times out or no service replies
- **THEN** the gateway returns a `503` (or `504`) response rather than hanging

### Requirement: Gateway health reflects the stack

The gateway's `/health` endpoint SHALL report healthy only when NATS is
reachable and every domain service responds; otherwise it SHALL report
unhealthy.

#### Scenario: All services up

- **WHEN** `/health` is requested and NATS and all three domain services
  respond
- **THEN** the gateway reports a healthy status

#### Scenario: A service down

- **WHEN** `/health` is requested and a domain service does not respond
- **THEN** the gateway reports an unhealthy status
