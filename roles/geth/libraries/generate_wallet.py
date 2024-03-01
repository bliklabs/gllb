#!/usr/bin/python


from ansible.module_utils.basic import AnsibleModule
import subprocess
import os
import json


def main():
    module = AnsibleModule(
        argument_spec=dict(
            datadir=dict(type='str', required=True),
            json_file=dict(type='str', required=True),
        )
    )

    datadir = module.params['datadir']
    json_file = module.params['json_file']

    try:
        password = subprocess.check_output(['openssl', 'rand', '-hex', '16']).decode().strip()
        temp_file_geth = module.tmpdir + '/geth_output.txt'

        # generate wallet
        with open(temp_file_geth, 'w') as f:
            subprocess.check_call(['geth', '--datadir', datadir, 'account', 'new'], stdin=subprocess.PIPE, stdout=f, text=True, input=password+'\n'+password)

        # parse wallet details
        with open(temp_file_geth, 'r') as f:
            output = f.read()

        public_address = output.split('Public address of the key:  ')[1].split('\n')[0].strip()
        secret_key_path = output.split('Path of the secret key file: ')[1].split('\n')[0].strip()
        secret_key_basename = os.path.basename(secret_key_path)
        json_file = os.path.join('/opt/validator/privs', secret_key_basename, 'meta.json')
        priv_key = subprocess.check_output(['web3', 'account', 'extract', '--keyfile', secret_key_path, '--password', password]).decode().split('Private key:  ')[1].split('\n')[0].strip()

        # Backup the wallet details
        backup_dir = os.path.join('/opt/validator/privs', os.path.basename(secret_key_path))
        os.makedirs(backup_dir, exist_ok=True)
        subprocess.check_call(['cp', secret_key_path, os.path.join(backup_dir, 'encrypted_key')])

        # Jsonify for fetch
        with open(json_file, 'w') as f:
            json.dump([{
                'public_address': public_address,
                'secret_key_path': secret_key_path,
                'password': password,
                'priv_key': priv_key
            }], f, indent=2)

        result = {
            'changed': True,
            'msg': f'Accounts created and details saved in {json_file}'
        }

        module.exit_json(**result)

    except subprocess.CalledProcessError as e:
        module.fail_json(msg=f'Command failed with return code {e.returncode}: {e.cmd}')


if __name__ == '__main__':
    main()
