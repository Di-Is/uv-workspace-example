
ARG _UV_VERSION=0.6.6

FROM ubuntu:24.04 AS ubuntu_base

# UIDの重複を避けるため、ubuntu:24.04に含まれるubuntuユーザーを削除
RUN userdel -f -r ubuntu

ENV DEBIAN_FRONTEND=noninteractivew

RUN sed -i.bak -r 's@http://(jp\.)?archive\.ubuntu\.com/ubuntu/?@http://ftp.udx.icscoe.jp/Linux/ubuntu/@g' /etc/apt/sources.list.d/ubuntu.sources
RUN --mount=type=cache,target=/var/lib/apt/lists \
    --mount=type=cache,target=/var/cache/apt/archives \
    apt update && \
    apt upgrade -y

RUN --mount=type=cache,target=/var/lib/apt/lists \
    --mount=type=cache,target=/var/cache/apt/archives \
    apt install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        sudo \
        vim

# UID、ユーザー名を ARG で受け取る
ARG DEVEL_USER_ID=1000
ARG _USERNAME=ubuntu
ARG _HOME=/home/${_USERNAME}
ARG _WORKSPACE=${_HOME}/workspace

RUN groupadd -g $DEVEL_USER_ID $_USERNAME && \
    useradd -m -u $DEVEL_USER_ID -g $DEVEL_USER_ID -s /bin/bash $_USERNAME
RUN echo "$_USERNAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER ${_USERNAME}
WORKDIR ${_WORKSPACE}

ENV UV_CACHE_DIR=${_WORKSPACE}/.cache/uv/cache
ENV UV_PYTHON_INSTALL_DIR=${_WORKSPACE}/.cache/uv/python
ENV UV_TOOL_DIR=${_WORKSPACE}/.cache/uv/tool
ENV UV_TOOL_BIN_DIR=${_WORKSPACE}/.cache/uv/tool_bin
ENV PATH=${PATH}:${_HOME}/.local/bin:${_WORKSPACE}/.cache/uv/tool_bin

COPY --from=ghcr.io/astral-sh/uv:0.6.6 /uv /bin/uv
