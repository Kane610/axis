Python project to set up a connection towards Axis Communications devices and to subscribe to specific events on the metadatastream.

## Initialization architecture

Vapix initialization is phase-based and driven by handler metadata:

- `API_DISCOVERY`: handlers initialized after API discovery.
- `PARAM_CGI_FALLBACK`: handlers that may initialize from parameter support when not listed in discovery.
- `APPLICATION`: handlers initialized after applications are loaded.

Handlers declare phase membership through `handler_groups` and may customize phase eligibility through `should_initialize_in_group`.

Example fallback policy:

- `LightHandler` participates in both `API_DISCOVERY` and `PARAM_CGI_FALLBACK`.
- In `PARAM_CGI_FALLBACK`, it initializes only when not listed in API discovery and listed in parameters.