# ---------- Stage 1: Builder ----------
FROM python:3.10-slim AS builder

WORKDIR /myapp

COPY requirements/base.txt .

RUN pip3 install --no-cache-dir --prefix=/install -r base.txt



# ---------- Stage 2: Runtime ----------
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /myapp

# Copy only installed dependencies from builder
COPY --from=builder /install /usr/local


COPY . .

EXPOSE 8001
# EXPOSE: Is used for documentation purpose, so the develoepr may know which port will be used by the APP itself.

# CMD ["python3", "manage.py", "makemigrations"]

# CMD ["python3", "manage.py", "runserver", "0.0.0.0:8001"]

COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]


# loopback address: It will only accept connections that come from this same machine.
# A loopback address is a special, reserved IP address (like 127.0.0.1 for IPv4 or ::1 for IPv6)
# that allows a network device to send data packets to itself, never leaving the machine, for testing, development, and internal communication

# Why this does NOT work in Docker:
# CMD ["python3", "manage.py", "runserver", "127.0.0.1:8000"]

# What Django is saying:
# “I will accept requests only from inside the container.”


# Why this WORKS
# CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]

# What it means:

# “Listen on all network interfaces.”

# That includes:

# Loopback (127.x.x.x)

# Network interface (eth0)

# So Docker can successfully forward traffic.


# 8000:8000  --> host:container



# Multi-stage builds allow us to separate build-time and runtime dependencies. We build artifacts in one stage
#  and copy only the required output into a smaller final image, reducing size and improving security.”
