
ARG _UV_VERSION=0.6.2

FROM ghcr.io/astral-sh/uv:${_UV_VERSION} AS uv

FROM ubuntu:24.04 AS base

ENV DEBIAN_FRONTEND=noninteractive
ENV UV_CACHE_DIR=/workspace/.uv_cache/cache
ENV UV_PYTHON_INSTALL_DIR=/workspace/.uv_cache/python
ENV UV_TOOL_DIR=/root/.local/bin

WORKDIR /workspace

RUN sed -i.bak -r 's@http://(jp\.)?archive\.ubuntu\.com/ubuntu/?@http://ftp.udx.icscoe.jp/Linux/ubuntu/@g' /etc/apt/sources.list.d/ubuntu.sources
RUN apt update && \
    apt upgrade -y && \
    apt install -y --no-install-recommends \
        zsh \
        curl \
        git \
        vim \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

ENV SHELL=/bin/zsh
RUN chsh -s $(which zsh)

COPY --from=uv /uv /bin/
