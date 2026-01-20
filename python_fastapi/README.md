### Important notes:
- FastAPI and Gunicorn (multiple Uvicorn workers)
    - Deal with the `BatchSpanProcessor` [not fork-safe issue](https://opentelemetry-python.readthedocs.io/en/stable/examples/fork-process-model/README.html) using the `post_fork` Gunicorn hook. Gunicorn uses `fork()` to create workers, which inherits parent process locks causing deadlocks with background threads.

- FastAPI and Uvicorn (multiple workers without Gunicorn)
    - Uvicorn uses the `spawn` method to create workers, which avoids the fork-safety issue entirely. Each spawned worker starts fresh with its own memory space, so standard OpenTelemetry initialization in the application startup (e.g., FastAPI's `lifespan`) is sufficient.
