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

#PATH='/home/b/.local/bin:/usr/bin:/usr/sbin'

eval $(ssh-agent -s)
ssh-add "${ANSIBLE_PRIVATE_KEY_FILE}"
