# validator_testnet -- gllb

Converged geth + lighthouse | nginx deployed via ansible

Roles for geth and lighthouse use local cache to dynamically generate wallets, bootnodes,
enr, validators, testnet, and a slew of runtime configuration. Playbook support includes an 
AIO bootstrap_and_deploy_testnet, bootstrap, sync_config, and clean modes. The only needed hostvars
definitions are nginx_vhosts options. All other configurations are pulled from vars, generated, or synced at runtime.

Each node runs the following systemd services:
  ```
  geth-boot
  geth
  lighthouse-boot
  lighthouse (i.e., beacon)
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

## Usage

To provision a VM cluster:

1. Copy your ciuser: "ansible" ssh private key:
   ```   
   {$PROJECT_DIRECTORY}/.secret
   ```

2. Load the configuration environment:
   ```
   source load_environment.sh
   ```

3. Define the hosts you would like to bootstrap and cluster by group:
   ```
   > $ cat hosts/hosts.ini
   # vms
   [testnet]
   vm01
   vm02

   # dockers
   [multi_node_validator]
   ubuntu01
   ubuntu02

   # untested multi cluster builds
   [bootnodes]
   vm100
   vm200

   [cluster1] # bootstrap_node == vm100
   vm100
   vm101
   vm102

   [cluster2] # bootstrap_node == vm200
   vm200
   vm201
   vm202
   ```

4. Define the hostvars for your nginx server in testnet:
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
   ```
   # Full deployment
   ansible-playbook -i hosts/hosts.ini playbooks/bootstrap_and_deploy_testnet.yml -l testnet --flush-cache

   # Rebuilds:
   ## clean 
   ansible-playbook -i hosts/hosts.ini playbooks/clean.yml -l testnet --flush-cache


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
   ANSIBLE_CACHE_PLUGIN_CONNECTION="${PROJECT_PATH}/cache/"

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
