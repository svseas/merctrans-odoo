txt
version: "3.1"
services:
  web_prod:
    image: odoo:14.0
    depends_on:
      - db
    ports:
      - "8069:8069"
    volumes:
      - odoo-web-data:/var/lib/odoo
      - ./config:/etc/odoo
      - ./local-addons:/mnt/extra-addons
    environment:
      - USER=odoo
      - PASSWORD=odoo
    secrets:
      - postgresql_password
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_PASSWORD=odoo
      - POSTGRES_USER=odoo
      - PGDATA=/var/lib/postgresql/data/pgdata
    volumes:
      - odoo-db-data:/var/lib/postgresql/data/pgdata
    secrets:
      - postgresql_password
  web_test:
    image: odoo:14.0
    depends_on:
      - db_test
    ports:
      - "8079:8069"
    volumes:
      - odoo-web-data-test:/var/lib/odoo
      - ./config-test:/etc/odoo
      - ./local-addons:/mnt/extra-addons
    environment:
      - USER=odoo
      - PASSWORD=odoo
  db_test:
    image: postgres:13
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_PASSWORD=odoo
      - POSTGRES_USER=odoo
      - PGDATA=/var/lib/postgresql/data/pgdata
    ports:
      - 5435:5432
    volumes:
      - odoo-db-data-test:/var/lib/postgresql/data/pgdata
    secrets:
      - postgresql_password

volumes:
  odoo-web-data:
  odoo-db-data:
  odoo-web-data-test:
  odoo-db-data-test:

secrets:
  postgresql_password:
    file: odoo_pg_pass
