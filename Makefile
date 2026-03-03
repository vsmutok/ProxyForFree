.PHONY: install start stop status stop-all list-countries list-configs lint format clean help api

# Install dependencies using uv
install:
	uv sync

# Start a proxy: make start country=usa config=us-free-44 port=8011
start:
	uv run proxy-start $(country) $(config) $(port)

# Stop a proxy: make stop port=8011
stop:
	uv run proxy-stop $(port)

# Start REST API server
api:
	uv run proxy-api

# Show status of running proxies
status:
	uv run proxy-status

# Stop all proxies and clean up the system
stop-all:
	uv run proxy-stop-all

# View available countries
list-countries:
	uv run proxy-list-countries

# View configs for a country
list-configs:
	uv run proxy-list-configs $(country)

# Lint code using ruff
lint:
	uv run ruff check .

# Format code using ruff
format:
	uv run ruff format .

# Clean temporary files
clean:
	sudo rm -f /tmp/ovpn_*.log /tmp/ovpn_*.pid
	rm -f proxy.conf_*

# Help
help:
	@echo "Available commands:"
	@echo "  make install         - Install dependencies via uv"
	@echo "  make start           - Start a proxy (e.g., make start country=usa config=us-free-44 port=8011)"
	@echo "  make stop            - Stop a proxy (e.g., make stop port=8011)"
	@echo "  make api             - Start the REST API server"
	@echo "  make status          - Show running proxies status"
	@echo "  make stop-all        - Stop all proxies"
	@echo "  make list-countries  - Show available countries"
	@echo "  make list-configs    - Show configs for a country (e.g., make list-configs usa)"
	@echo "  make lint            - Check code with ruff"
	@echo "  make format          - Format code with ruff"
	@echo "  make clean           - Remove temporary files"
