all: build init-db run 
build: 
	docker build -t highspot:latest .
init-db:
	touch database.db
run:
	docker run -d --mount type=bind,source="$$(pwd)"/database.db,target=/app/database.db -p 8080:8080 highspot:latest
clean:
	@echo "Removing database..."
	rm database.db
