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
    keystore_dir = os.path.join(directory, "keystore")
    priv_dir = os.path.join(directory, "priv")
    genesis_dir = os.path.join(directory, "genesis")
    os.makedirs(directory, exist_ok=True)
    os.makedirs(keystore_dir, exist_ok=True)
    os.makedirs(genesis_dir, exist_ok=True)
    os.makedirs(priv_dir, exist_ok=True)
    return keystore_dir, genesis_dir, priv_dir


def create_accounts(num_accounts, num_signers, data_directory):
    # generate new private and signer accounts
    accounts = []
    for i in range(num_accounts):
        password = generate_random_password()
        account = subprocess.run(['/usr/local/bin/geth', '--datadir', data_directory, 'account', 'new'], input=f'{password}\n{password}\n', capture_output=True, text=True)
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
    if len(sys.argv) != 5:
        print("Usage: python script.py <number_of_accounts> <number_of_signers> <data_directory> <sync_dir>")
        sys.exit(1)
    num_accounts = int(sys.argv[1])
    num_signers = int(sys.argv[2])
    data_directory = os.path.abspath(sys.argv[3])
    sync_directory = os.path.abspath(sys.argv[4])
    if num_signers > num_accounts:
        print("Number of signers cannot exceed number of accounts.")
        sys.exit(1)

    # generate the sync dir used for as a first line for persistance on clean
    data_keystore_dir, data_genesis_dir, data_priv_dir = setup_directories(data_directory)
    sync_keystore_dir, sync_genesis_dir, sync_priv_dir = setup_directories(sync_directory)

    # for scaling wallets as needed
    existing_accounts = []
    accounts_file_path = os.path.join(sync_priv_dir, 'accounts.json')
    if os.path.exists(accounts_file_path):
        with open(accounts_file_path, 'r') as f:
            existing_accounts = json.load(f)

    # generate accounts with geth and clean the 0x wallet prefix
    new_accounts = create_accounts(num_accounts, num_signers, data_directory)
    for account in new_accounts:
        account["address"] = account["address"][2:] if account["address"].startswith("0x") else account["address"]

    # join new and old
    all_accounts = existing_accounts + new_accounts

    # copy all keyfiles to the sync directory
    for account in new_accounts:
        shutil.copy(account["keyfile_path"], sync_keystore_dir)

    # save the combined accounts
    accounts_file_path = os.path.join(data_priv_dir, 'accounts.json')
    with open(accounts_file_path, 'w') as outfile:
        json.dump(all_accounts, outfile, indent=4)
    accounts_file_path = os.path.join(sync_priv_dir, 'accounts.json')
    with open(accounts_file_path, 'w') as outfile:
        json.dump(all_accounts, outfile, indent=4)
    print(json.dumps(all_accounts, indent=4))

    # update perms
    change_permissions(data_directory, "svc_geth", "root", "770")
    change_permissions(data_priv_dir, "root", "root", "0600")
    change_permissions(sync_directory, "svc_geth", "root", "770")
    change_permissions(sync_priv_dir, "root", "root", "0600")


if __name__ == "__main__":
    main()
