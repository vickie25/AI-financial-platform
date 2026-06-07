Dockerfile Instructions for Project Silver
The Golden Rules (Never Break These)
1. Always Pin Your Base Image
dockerfile# ✅ CORRECT
FROM node:20.11.0
FROM python:3.11.4-slim

# ❌ WRONG
FROM node
FROM node:latest

2. Always Pin Package Versions
For Python (pip):
dockerfile# ✅ CORRECT
RUN pip install pytest==8.2.2 requests==2.31.0 flask==3.0.1

# ❌ WRONG
RUN pip install pytest
RUN pip install pytest>=8.0.0
RUN pip install pytest~=8.2
For Node.js (npm):
dockerfile# ✅ CORRECT
RUN npm install jest@29.7.0 express@4.18.2

# ❌ WRONG
RUN npm install jest
RUN npm install jest@latest
Exception — these are fine without versions:
dockerfileRUN pip install -r requirements.txt   # ✅ allowed
RUN npm ci                             # ✅ allowed (uses lockfile)

3. Always Add --no-install-recommends to apt-get
dockerfile# ✅ CORRECT
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential

# ❌ WRONG
RUN apt-get install -y curl
RUN apt-get install -y --no-install-recommends curl  # missing update

4. Always Use COPY . . (not your folder name)
dockerfile# ✅ CORRECT
COPY . .

# ❌ WRONG
COPY my-project/ .
COPY ./my-repo/ /app

5. Only COPY to Allowed Destinations
dockerfile# ✅ CORRECT destinations
COPY . /app
COPY . /workspace
COPY config.json /tmp/config.json
COPY . /opt/myproject
COPY script.sh /usr/local/bin/script.sh
COPY . /home/user

# ❌ WRONG (outside allowed list)
COPY . /myapp
COPY . /data
COPY . /server

6. Combine RUN Commands (max 30 RUN lines allowed)
dockerfile# ✅ CORRECT - combined into one RUN
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git && \
    pip install pytest==8.2.2 && \
    pip install requests==2.31.0

# ❌ WRONG - too many separate RUN lines
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y git
RUN pip install pytest==8.2.2
RUN pip install requests==2.31.0

7. Never Use These (Banned)
dockerfile# ❌ ALL of these will get your Dockerfile REJECTED

RUN --privileged ...          # Never use --privileged
RUN eval "$SOME_COMMAND"      # No eval
RUN sh -c "$MY_VAR"           # No dynamic commands
ADD https://example.com/file  # No ADD with URLs (use curl instead)
For downloading files, do this instead:
dockerfile# ✅ CORRECT way to download a file
RUN curl -fsSL https://example.com/v1.2.3/install.sh | sh

# ❌ WRONG
ADD https://example.com/install.sh /tmp/install.sh

8. Don't Exclude .git/ in .dockerignore
# ❌ NEVER put this in your .dockerignore
.git

# The platform needs .git history to reset commits

Size Limits to Remember
RuleLimitTotal Dockerfile size≤ 20 KBTotal lines≤ 200 linesRUN instructions≤ 30

Full Example Dockerfiles
Python Project
dockerfileFROM python:3.11.4-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    pytest==8.2.2 \
    requests==2.31.0 \
    flask==3.0.1

CMD ["python", "main.py"]
Node.js Project
dockerfileFROM node:20.11.0-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y --no-install-recommends \
    git && \
    rm -rf /var/lib/apt/lists/*

RUN npm ci

CMD ["node", "index.js"]
Java Project
dockerfileFROM maven:3.9.6-eclipse-temurin-17

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y --no-install-recommends \
    git && \
    rm -rf /var/lib/apt/lists/*

RUN mvn install -DskipTests

CMD ["java", "-jar", "target/app.jar"]

Quick Checklist Before Submitting

 Base image has a version tag (not latest)
 All pip packages have ==X.Y.Z
 All npm packages have @X.Y.Z or using npm ci
 Every apt-get install has --no-install-recommends
 Using COPY . . not COPY folder-name/ .
 COPY destinations are /app, /workspace, /tmp, /opt, /usr/local, or /home
 No eval, no --privileged, no ADD https://
 Under 200 lines and 30 RUN commands
 .git/ is NOT in .dockerignore