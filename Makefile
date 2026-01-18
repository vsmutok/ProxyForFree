.PHONY: install status stop-all list-countries lint format clean help

# Install dependencies using uv
install:
	uv sync

# Show status of running proxies
status:
	sudo uv run proxy-status

# Stop all proxies and clean up the system
stop-all:
	sudo uv run proxy-stop-all

# View available countries
list-countries:
	sudo uv run proxy-list-countries

# View configs for a country
list-configs:
	sudo uv run proxy-list-configs $(country)

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
	@echo "  make status          - Show running proxies status (requires sudo)"
	@echo "  make stop-all        - Stop all proxies (requires sudo)"
	@echo "  make list-countries  - Show available countries (requires sudo)"
	@echo "  make list-configs    - Show configs for a country (e.g., make list-configs country=usa) (requires sudo)"
	@echo "  make lint            - Check code with ruff"
	@echo "  make format          - Format code with ruff"
	@echo "  make clean           - Remove temporary files"
