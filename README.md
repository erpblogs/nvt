# nvt

# quick create a new module 
docker exec -it odoo17-web odoo scaffold custom_menu /mnt/extra-addons

docker restart odoo17-web

sudo docker exec -it odoo17-web /bin/bash -c "odoo -c /etc/odoo/odoo.conf --http-port=9999 -d demo -u custom_users --stop-after-init"

sudo docker exec -it odoo17-web /bin/bash -c "tail -f /var/logs/odoo/odoo-server.log"