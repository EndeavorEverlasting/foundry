FROM node:20-alpine AS base

ENV PNPM_HOME=/root/.local/share/pnpm \
    PATH=/root/.local/share/pnpm:$PATH \
    CI=1

RUN corepack enable && corepack prepare pnpm@9.12.3 --activate

WORKDIR /app

COPY package.json pnpm-workspace.yaml pnpm-lock.yaml* turbo.json tsconfig.base.json ./
COPY apps/branchfoundry-web/package.json ./apps/branchfoundry-web/
COPY apps/guardfoundry-web/package.json ./apps/guardfoundry-web/
COPY packages/foundry-ui/package.json ./packages/foundry-ui/
COPY packages/foundry-hooks-sdk/ts/package.json ./packages/foundry-hooks-sdk/ts/

RUN pnpm install --frozen-lockfile || pnpm install

COPY apps ./apps
COPY packages ./packages

EXPOSE 5173

CMD ["pnpm", "--filter", "branchfoundry-web", "dev", "--host", "0.0.0.0"]
