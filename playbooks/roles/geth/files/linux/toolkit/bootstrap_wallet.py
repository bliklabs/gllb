#!/usr/bin/env python3


import subprocess
import json
import random
import sys
import os
import shutil


def generate_random_password(length=12):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(random.choice(chars) for _ in range(length))


def setup_directories(directory):
    directory = os.path.abspath(directory)
    data_dir = os.path.join(directory, "data")
    keystore_dir = os.path.join(data_dir, "keystore")
    priv_dir = os.path.join(directory, "privs")
    genesis_dir = os.path.join(directory, "genesis")
    os.makedirs(directory, exist_ok=True)
    shutil.rmtree(data_dir)
    os.makedirs(keystore_dir, exist_ok=True)
    os.makedirs(genesis_dir, exist_ok=True)
    os.makedirs(priv_dir, exist_ok=True)
    return data_dir, keystore_dir, genesis_dir, priv_dir


def create_accounts(num_accounts, num_signers, data_dir):
    # generate new private and signer accounts
    accounts = []
    for i in range(num_accounts):
        password = generate_random_password()
        account = subprocess.run(['/usr/local/bin/geth', '--datadir', data_dir, 'account', 'new'], input=f'{password}\n{password}\n', capture_output=True, text=True)
        # parse the output from geth account creation
        if account.returncode == 0:
            output = account.stdout.splitlines()
            address_line = [line for line in output if line.startswith("Public address of the key:")][0]
            address = address_line.split(':')[-1].strip()
            secret_key_line = [line for line in output if line.startswith("Path of the secret key file:")][0]
            secret_key_path = secret_key_line.split(':')[-1].strip()
            secret_key_path = secret_key_path.strip()
            # divy up the signers and private account
            if i < num_signers:
                account_type = "signer"
            else:
                account_type = "private"
            # add account to data structure
            accounts.append({
                "address": address,
                "password": password,
                "type": account_type,
                "keyfile_path": os.path.abspath(secret_key_path)
            })
    return accounts


def change_permissions(directory, owner, group, octal):
    subprocess.run(["chown", "-R", f"{owner}:{group}", directory])
    subprocess.run(["chmod", "-R", octal, directory])


def main():
    if len(sys.argv) != 4:
        print("Usage: python script.py <number_of_accounts> <number_of_signers> <root_directory> --danger")
        sys.exit(1)
    num_accounts = int(sys.argv[1])
    num_signers = int(sys.argv[2])
    root_directory = os.path.abspath(sys.argv[3])
    if num_signers > num_accounts:
        print("Number of signers cannot exceed number of accounts.")
        sys.exit(1)

    # generate dirs
    data_dir, keystore_dir, genesis_dir, priv_dir = setup_directories(root_directory)

    # generate accounts with geth and clean the 0x wallet prefix
    new_accounts = create_accounts(num_accounts, num_signers, data_dir)
    for account in new_accounts:
        account["address"] = account["address"][2:] if account["address"].startswith("0x") else account["address"]

    # save accounts
    accounts_file_path = os.path.join(priv_dir, 'accounts.json')
    with open(accounts_file_path, 'w') as outfile:
        json.dump(new_accounts, outfile, indent=4)
    print(json.dumps(new_accounts, indent=4))

    # update perms
    change_permissions(root_directory, "svc_geth", "root", "770")
    change_permissions(priv_dir, "root", "root", "0600")


if __name__ == "__main__":
    main()
