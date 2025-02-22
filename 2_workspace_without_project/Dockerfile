FROM ubuntu:24.04

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /workspace

COPY --from=ghcr.io/astral-sh/uv:0.6.2 /uv /bin/

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-workspace --package=app

COPY . /workspace
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-editable --package=app

CMD ["uv", "run", "fastapi", "dev", "app/main.py"]