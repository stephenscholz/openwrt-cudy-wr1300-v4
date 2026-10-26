FROM docker.io/library/debian:bookworm@sha256:854dd8ab51d62866dbd8f5431d15ce77b12983a2a4a1e1fe43a2395dc7ef9f61
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    build-essential clang flex bison g++ gawk gcc-multilib g++-multilib \
    gettext git libncurses-dev libssl-dev python3 python3-setuptools \
    rsync swig unzip zlib1g-dev file wget curl ca-certificates patch \
    xz-utils zstd time perl && rm -rf /var/lib/apt/lists/*
ENV FORCE_UNSAFE_CONFIGURE=1
WORKDIR /workspace
