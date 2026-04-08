# Test sample: Node.js app Dockerfile with intentional security and hygiene issues.
# This file contains ~10 deliberate problems for the code review skill to catch.

# [ISSUE: FROM latest — unpinned, non-reproducible]
FROM node:latest

# [ISSUE: WORKDIR not set — implicit / as working directory]

# [ISSUE: Secret baked into image via ENV]
ENV DB_PASSWORD=supersecret123
ENV NODE_ENV=production

# [ISSUE: apt cleanup in a separate RUN layer — layer bloat]
RUN apt-get update && apt-get install -y curl python3 build-essential
RUN rm -rf /var/lib/apt/lists/*

# [ISSUE: COPY . . before npm install — busts dependency cache on every source change]
COPY . .
RUN npm install --production

# [ISSUE: ADD instead of COPY for a local config file]
ADD config/app.json /app/config.json

# [ISSUE: curl with TLS verification disabled — supply chain risk]
RUN curl -k https://internal-registry.example.com/setup.sh | bash

# [ISSUE: No USER instruction — container runs as root]

EXPOSE 3000

CMD ["node", "src/index.js"]
