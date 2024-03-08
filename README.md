# Ansible driven ethereum local testnet


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

1. Copy your CIUSER ssh private key:
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
   ```

4. Run playbook:
   ```
   ansible-playbook -i hosts/hosts.ini playbooks/deploy_testnet.yml -l testnet --flush-cache
   ```


## Configuration

1. Required - ansible-galaxy collection install community.general

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
