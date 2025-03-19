FROM ubuntu:latest
LABEL authors="albest"

ENTRYPOINT ["top", "-b"]