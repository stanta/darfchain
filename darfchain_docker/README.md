Installation development environment with Dokers
#####################################################################################
1. Install docker
   https://docs.docker.com/engine/installation/  
2. Install docker-compose

   pip install docker-compose

3. Inside directory from github

   docker-compose up -d

drink coffee or do something else  depends on your internet connection.

As result: localhost:8077 - odoo
           localhost:8076 - odoo
           localhost:58080 - rethinkdb
           localhost:32782 - bigchaindb API
Default docker bridge ip: 172.17.0.1
Setting test node for ethereum: http://172.17.0.1:8545
Connect with http://remix.ethereum.org (not https): 
               Menu Environment select web3 provider
               Provider for this development env: localhost:8545
               
               
darfchain module - ./addons/darfchain
odoo_main - odoo system Dockerfile with libraries
bigchaindb - bigchaindb sours
docs -bigchaindb documentation 