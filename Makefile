all: build init-db run 
build:
	@echo "Starting image build..."
	@docker build -t highspot:latest .
init-db:
	@echo "Creating database file..."
	@touch database.db
run: stop
	@echo "Starting Docker container"
	@docker run -d --mount type=bind,source="$$(pwd)"/database.db,target=/app/database.db -p 8080:8080 --name highspot highspot:latest
stop:
	@echo "Stopping container..."
	@docker stop highspot || true 
	@echo "Removing container..."
	@docker rm highspot || true
rm-db: stop
	@echo "Removing database..."
	@rm -f database.db
clean: stop
	@echo "Removing images..."
	@docker rmi highspot
