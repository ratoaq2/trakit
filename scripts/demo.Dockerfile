# trakit from this repository with VHS, to record docs/images/demo.gif. See scripts/demo.sh.
# The image installs the code of the branch, so the GIF shows the output of the branch.
FROM docker.io/library/python:3.15-slim

ARG VHS_VERSION=0.12.1
ARG TTYD_VERSION=1.7.7

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl chromium \
    && curl -sSL -o /usr/local/bin/ttyd https://github.com/tsl0922/ttyd/releases/download/${TTYD_VERSION}/ttyd.x86_64 \
    && chmod +x /usr/local/bin/ttyd \
    && curl -sSL -o /tmp/vhs.deb https://github.com/charmbracelet/vhs/releases/download/v${VHS_VERSION}/vhs_${VHS_VERSION}_amd64.deb \
    && apt-get install -y /tmp/vhs.deb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/vhs.deb

COPY pyproject.toml README.md LICENSE /src/
COPY trakit /src/trakit
RUN pip install --no-cache-dir "/src[yaml]" && rm -rf /src

ENV VHS_NO_SANDBOX=true

ENTRYPOINT ["vhs"]
