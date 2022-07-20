# Merctrans Project Manager 
- debug docker  odoo
``` bash
docker exec -it 02_merctrans_odoo-web_prod-1 bash -c "odoo shell -d merctrans"
```
- docker exec -it 02_merctrans_odoo-web_prod-1 bash -c "odoo shell -d merctrans"
- Connect Postgres in docker 
``` bash
# name_service_db = 02_merctrans_odoo-db-1
docker exec -it 02_merctrans_odoo-db-1 bash
# Sau khi connect duoc vao bash cua odoo service
psql -U odoo postgres
```
