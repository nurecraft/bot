# nurecraft_bot

This bot based on example bot of [aiogram](https://github.com/aiogram/aiogram) framework team.

## What this bot can do?

- May exist
- Watch new chat members and filter users (ask question and restrict user)
- Has simple admin commands for making restrictions
- Collect linked Minecraft accounts
- Register user on Minecraft server
- Check online count, list of player and TPS.
- Prepare server commands
- Send message to Telegram chat
- Find Telegram user by Minecraft username

## Development

### System dependencies

- Python 3.8
- pipenv
- Docker
- docker-compose
- make

### Setup environment

- Install dependencies in venv: `pipenv install --dev`
- Copy `.env.dist` to `.env` file and change values in this file
- Run databases in docker: `make docker-up-db`
- Apply migrations: `make migrate`

### Project structure

- Application package is in `app`
- All text translations is placed in `locales`
- Migrations is placed in `migrations`
- Entry-point is `app/__main__.py` (Can be executed as `python -m app`)
...

### Contributing

Before you will make commit need to run `black`, `isort` and `Flake8` via command `make lint`
If you change Database models you will need to generate migrations: `make migration message="do something"`

## Deployment

Here listed only Docker deployment methods.
That's mean you can't read here how to deploy the bot with other methods instead of Docker
but you can do that manually.

Also this bot can't be normally started in Docker with polling mode
because in this mode aiohttp server will be not started and healthcheck can not be started.

### docker-compose

Pre-requirements:
- Docker
- docker-compose

Steps:
- Prepare `.env` file
- ... (TODO)
- `make app-create` - for first deploy, for updating or restarting

Stopping:
- `make docker-stop`

Destroying (with volumes):
- `make docker-destroy`

### Docker Swarm

Pre-requirements:
- Docker (with activated swarm mode)
- traefik 2.0 in Docker (with overlay network named `web`)
