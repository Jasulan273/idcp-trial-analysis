# Assignment 5 observed evidence

Captured 29 October 2026 from the real local Jenkins controller at `127.0.0.1:8085`.
Build 2 tested commit `0233e0834e5185e41639027f741727421f92ee3f` and finished SUCCESS.
Its recorded cause is `Started by an SCM change`, rather than a second manual start.

- `jenkins-pipeline.png`: stage view with successful build 2 and the earlier failed build 1.
- `jenkins-console.png`: eight passing tests in the test container.
- `jenkins-success.png`: the final console SUCCESS and artifact collection.
- `console-2.txt`: full build log.
- `verified.json`: selected build metadata and SCM trigger cause.
- `summary.json`, `comparison.svg`, `provenance.txt`: exact archived outputs.

The controller was Jenkins 2.580.2; the container used Python 3.12.16 on ARM64,
with Docker engine 29.5.2. The example input is synthetic. These records verify
software execution, not the scientific benefit of IDCP. Local Jenkins links
require the author's machine; retained screenshots and logs are readable here.
