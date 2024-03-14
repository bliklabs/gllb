# validator_testnet -- gllb

geth:boot|client + lighthouse:boot|bn|vc + lb:nginx

Generates a proof of stake ethereum network.
Includes an execution API for transactions and validations.
Roles for geth and lighthouse use local cache to dynamically generate:
  - wallets
  - bootnodes
  - enr
  - validators
  - local testnet
  - cluster runtime configurations. 

Playbooks support: 
  ```
  - bootstrap_and_deploy_testnet.yml
    - AIO buildout
    - Chooses the first node in < groupname > as bootnode
  - bootstrap.yml
    - Configures N>=1 dynamically generated bootnode
  - sync_config.yml
    - Synchronizes cluster facts and statefully configures specified peer(S)
  - clean(_geth|_lighthouse).yml
    - removes service, packaging, and configuration residue
  ```

Each node runs the following systemd services:
  ```
  geth-boot
  geth
  lighthouse-boot
  lighthouse ( i.e., beacon )
  lighthouse-vc
  nginx
  ```

Each host offers api services on the default route service | nginx forwarding port:
  ```
  geth-authrpc                  = 8551 | 65001
  geth-http                     = 8552 | 65002
  lighthouse_beacon_http        = 15000 | 65003
  lighthouse_vc_http            = 16000 | 65004
  ```


## Installation

To install this project, follow these steps:

1. Clone the repository:
    ```
    git clone https://github.com/bliklabs/validator_testnet
    ```

2. Navigate to the project directory:
    ```
    cd validator_testnet
    ```
3. Sync with main (required if you have the v1.0.0-beta release)
    ```
    git remote add origin https://github.com/bliklabs/validator_testnet
    git fetch origin main
    git pull origin main
    ```


## Usage

To provision a VM cluster:

1. Copy your ciuser: "ansible" ssh private key:
   ```   
   cp /foo/bar/privkey < PROJECT_DIRECTORY >/.secret
   ```

2. Load the configuration environment:
   ```
   source load_environment.sh
   ```

3. Define the hosts you would like to bootstrap and cluster by group:
   ```
   > $ cat hosts/hosts.ini
   # testnet vm nodes
   [testnet]
   vm01
   vm02

   # dockers
   [multi_node_validator]
   ubuntu01
   ubuntu02

   # Multicluster
   [bootnodes]
   vm100
   vm200

   [cluster1]
   vm100
   vm101
   vm102

   [cluster1:vars]
   bootstrap=vm100
   
   [cluster2]
   vm200 bootstrap=vm200
   vm201 bootstrap=vm200
   vm202 bootstrap=vm200
   ```

4. Define < hostvars[nginx_vhosts | nginx_proxy_template="vhosts.j2"] > for your node:
   ```
   > $ cat vm02.yml 
   nginx_proxy_template: "vhost.j2"
   nginx_vhosts:
     - address: "{{ ansible_default_ipv4.address }}"
       listen: "65501"
       server_name: "geth_authrpc"
       forward_port: "8551"
       template: "{{ playbook_dir }}/templates/vhost.j2"
     - address: "{{ ansible_default_ipv4.address }}"
       listen: "65502"
       server_name: "geth_http"
       forward_port: "8552"
       template: "{{ playbook_dir }}/templates/vhost.j2"
     - address: "{{ ansible_default_ipv4.address }}"
       listen: "65503"
       server_name: "lighthouse_beacon_http"
       forward_port: "15000"
       template: "{{ playbook_dir }}/templates/vhost.j2"
     - address: "{{ ansible_default_ipv4.address }}"
       listen: "65504"
       server_name: "lighthouse_vc_http"
       forward_port: "16000"
       template: "{{ playbook_dir }}/templates/vhost.j2"
    ```

5. Run playbook:
   - Full deployment - TEST:PASS
     ```
     ansible-playbook -i hosts/hosts.ini playbooks/bootstrap_and_deploy_testnet.yml -l < groupname > --flush-cache
     ```
   - Stateful rebuilds: -- TEST:PASS
     ```
     # Clean
     ansible-playbook -i hosts/hosts.ini -l < hostname > playbooks/clean.yml --flush-cache
     ansible-playbook -i hosts/hosts.ini -l < hostname > playbooks/clean_geth.yml --flush-cache          # optional
     ansible-playbook -i hosts/hosts.ini -l < hostname > playbooks/clean_lighthouse.yml --flush-cache    # optional

     # Sync_and_config
     ansible-playbook -i hosts/hosts.ini -l < hostname > playbooks/sync_and_config.yml -e "bootstrap=< node_to_sync_with >"
     ```
   - Bootstrap, then sync_config: -- TEST:PASS
     ```
     # Generate bootstrap nodes defined in groupname, where len(groupname) == 2
     ansible-playbook -i hosts/hosts.ini playbooks/bootstrap.yml -l < boot_nodes_groupname > --flush-cache

     # Sync and config each respective cluster group
     ansible-playbook -i hosts/hosts.ini playbooks/sync_and_config.yml -l < cluster_nodes_groupname_1 >  -e "bootstrap=< boot_nodes_groupname[0] >"
     ansible-playbook -i hosts/hosts.ini playbooks/sync_and_config.yml -l < cluster_nodes_groupname_2 >  -e "bootstrap=< boot_nodes_groupname[1] >"
     ```


## Configuration

1. Required - 
   ```
   sudo apt install ansible docker.io python3-pip -y
   sudo pip3 install molecule molecule-docker jmespath
   sudo ansible-galaxy collection install community.general
   sudo ansible-galaxy collection install community.docker
   sudo ansible-galaxy collection install ansible.posix
   ```

2. Files:
   ```
   > $ cat ansible.cfg
   [defaults]
   fact_caching = jsonfile
   fact_caching_connection = cache/
                                                                                          
   > $ cat load_environment.sh
   #!/bin/bash

   PROJECT_OWNER="$(whoami)"
   PROJECT_PATH="${PWD}"
   PROJECT_END_STATE="${PROJECT_PATH}/hosts"
   ANSIBLE_INVENTORY="${PROJECT_END_STATE}/hosts.ini"
   ANSIBLE_PRIVATE_KEY_FILE="${PROJECT_PATH}/.secret"
   ANSIBLE_SSH_ARGS="-o StrictHostKeyChecking=no -o ForwardAgent=yes"
   ANSIBLE_ROLES_PATH="${PROJECT_PATH}/roles"
   ANSIBLE_GALAXY_CACHE_DIR="${PROJECT_PATH}/var"
   ANSIBLE_LOG_PATH="${PROJECT_PATH}/var/ansible.log"
   ANSIBLE_PYTHON_INTERPRETER='/usr/bin/python3'
   ANSIBLE_PLAYBOOK_DIR="${PROJECT_PATH}/playbooks"
   ANSIBLE_CACHE_PLUGIN="jsonfile"

   eval $(ssh-agent -s)
   ssh-add "${ANSIBLE_PRIVATE_KEY_FILE}"
   ```


## Tests

Molecule tests are provided for all roles.

1. geth
2. lighthouse
3. multi_node_validator 

To provision a cluster via molecule and docker:

1. Navigate to role:
   ```
   cd playbooks/roles/multi_node_validator/
   ```

2. Run molecule test:
   ```
   molecule test
   ```


## Contributing

blik@mail.bliklabs.com
