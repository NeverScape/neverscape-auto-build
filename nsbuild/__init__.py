#
#  ____   _____ ____   __ __  ____  _      ___   
# |    \ / ___/|    \ |  |  ||    || |    |   \  
# |  _  (   \_ |  o  )|  |  | |  | | |    |    \ 
# |  |  |\__  ||     ||  |  | |  | | |___ |  D  |
# |  |  |/  \ ||  O  ||  :  | |  | |     ||     |
# |  |  |\    ||     ||     | |  | |     ||     |
# |__|__| \___||_____| \__,_||____||_____||_____|
#
# Automated, cross-platform NeverScape client builder
#

import os
import zipfile
import argparse
import paramiko
import configparser

USERNAME = 'user'
PASSWORD = 'nsbuild'
ZIP_PATH = '/tmp/nsbuild.zip'
CLIENT_PATH = os.path.join(os.environ['HOME'], 'code/NeverScape/neverscape-client')
CONFIG_PATH = os.path.join(os.environ['HOME'], '.nsbuild_config')


def get_ssh_client(ip, username, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=22, username=username, password=password)
    return client


def get_sftp_client(ip, username, password):
    transport = paramiko.Transport((ip, 22))
    transport.connect(username=username, password=password)
    return paramiko.SFTPClient.from_transport(transport)


def execute(client, command):
    stdin, stdout, stderr = client.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    if exit_status != 0:
        print('[!] Command Error.')
    return stdout


def get_parser():
    parser = argparse.ArgumentParser(description='nsbuild')
    parser.add_argument(
        '--client', type=str, default=CLIENT_PATH,
        help='path to the client directory'
    )
    parser.add_argument(
        '--config', type=str, default=CONFIG_PATH,
        help='path to the config file'
    )
    return parser


def main():
    # cli
    parser = get_parser()
    args = vars(parser.parse_args())
    client_path = args['client']
    config_file = args['config']

    # read config file
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(config_file)
    mac_ip = config['settings']['mac_ip']
    linux_ip = config['settings']['nix_ip']
    windows_ip = config['settings']['win_ip']

    # zip client
    print('Zipping neverscape-client...')
    z = zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED)
    for root, _, files in os.walk(client_path):
        for f in files:
            z.write(
                os.path.join(root, f),
                os.path.relpath(
                    os.path.join(root, f),
                    os.path.join(client_path, '..')
                )
            )
    z.close()

    print('Creating SSH & SFTP clients...')
    clients = {
        #'mac': {
        #    'bin': 'NeverScape.bin',
        #    'home': '/Users/user',
        #    'ssh': get_ssh_client(mac_ip, USERNAME, PASSWORD),
        #    'sftp': get_sftp_client(mac_ip, USERNAME, PASSWORD),
        #},
        'linux': {
            'bin': 'NeverScape.bin',
            'home': '/home/user',
            'ssh': get_ssh_client(linux_ip, USERNAME, PASSWORD),
            'sftp': get_sftp_client(linux_ip, USERNAME, PASSWORD),
        },
        'windows': {
            'bin': 'NeverScape.exe',
            'home': 'C:\\Users\\user',
            'ssh': get_ssh_client(windows_ip, USERNAME, PASSWORD),
            'sftp': get_sftp_client(windows_ip, USERNAME, PASSWORD),
        },
    }

    for platform, client in clients.items():
        print(f'{platform}: SFTPing the zip')
        remote_zip_path = os.path.join(client['home'], 'nsbuild.zip')
        client['sftp'].put(ZIP_PATH, remote_zip_path)

        print(f'{platform}: Unzipping the client')
        execute(client['ssh'], f'unzip -o {remote_zip_path}')

        print(f'{platform}: Building client!')
        sub_path = f'neverscape-client/build_{platform}.spec'
        spec_path = os.path.join(client['home'], sub_path)
        if platform == 'windows':
            spec_path = spec_path.replace('/', '\\')
        execute(client['ssh'], f'pyinstaller {spec_path}')

        print(f'{platform}: SFTPing the binary')
        bin_path = os.path.join(client['home'], 'dist/main')
        if platform == 'windows':
            bin_path = bin_path.replace('/', '\\') + '.exe'
        client['sftp'].get(bin_path, client['bin'])

    # cleanup & finish
    print('linux: Cleaning up')
    os.system('chmod +x NeverScape.bin')
    execute(clients['linux']['ssh'], 'rm -rf /home/user/*')

    print('windows: Cleaning up')
    execute(
        clients['windows']['ssh'],
        'powershell.exe -Command "Remove-Item \'{0}\*\' -Recurse -Force"'.format(
            'C:\\Users\\user\\neverscape-client')
    )
    execute(
        clients['windows']['ssh'],
        'powershell.exe -Command "Remove-Item \'{0}\*\' -Recurse -Force"'.format(
            'C:\\Users\\user\\dist')
    )
    execute(clients['windows']['ssh'], 'del C:\\Users\\user\\nsbuild.zip')

    os.remove(ZIP_PATH)
