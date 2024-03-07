FROM ubuntu:22.04

# Install systemd and other necessary packages
RUN apt-get update \
    && apt-get install -y systemd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Enable systemd
RUN systemctl mask \
    dev-hugepages.mount \
    sys-fs-fuse-connections.mount \
    sys-kernel-config.mount \
    display-manager.service \
    systemd-logind.service \
    getty@.service \
    console-getty.service

# Ensure systemd starts
CMD ["/lib/systemd/systemd"]
