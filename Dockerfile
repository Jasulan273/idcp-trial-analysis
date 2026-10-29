ARG PYTHON_IMAGE=python:3.12-slim-bookworm@sha256:e697c81897302a4c4333bade000d98038fbb21eb064f8ee1fd42d02ebcd9d337
FROM ${PYTHON_IMAGE} AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /work
RUN groupadd --gid 10001 research && useradd --uid 10001 --gid 10001 --no-log-init research \
    && mkdir /work/results && chown 10001:10001 /work/results
COPY idcp_trial/ ./idcp_trial/
COPY data/example_pairs.csv ./data/example_pairs.csv
USER 10001:10001

FROM base AS test
COPY tests/ ./tests/
ENTRYPOINT ["python", "-m", "unittest"]
CMD ["discover", "-s", "tests", "-v"]

FROM base AS runtime
ENTRYPOINT ["python", "-m", "idcp_trial"]
CMD ["data/example_pairs.csv", "--output", "results"]
