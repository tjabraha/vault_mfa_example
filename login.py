import requests  # you will need to install the requests module (command: pip3 install requests)
import json
import getpass

# User provided inputs
user_name = input('Username: ')
password = input('Password: ')

# Uncomment this line to use the password so it won't echo to the screen. Make sure to uncomment the previous line
# password = getpass.getpass(prompt='Password: ')

# Operator provided values.  The only thing you need to change is to add your vault root token
vault_root_token = 's.7osR7zASDqNNfhvFxxZPbSZz'
base_vault_url = 'http://127.0.0.1:8200/'
secret_url_path = '%sv1/kv/data/application_name/users/%s' % (base_vault_url, user_name)
hash_algorithm_url_path = '%sv1/sys/tools/hash/sha2-256' % base_vault_url
totp_endpoint_url = '%sv1/totp/code/%s' % (base_vault_url, user_name)
vault_root_token_headers = {'X-Vault-Token': vault_root_token}
hash_data = {"input": password}

# Http communication with Vault via the requests python module
hash_the_password = requests.post(hash_algorithm_url_path, headers=vault_root_token_headers, data=hash_data)
pass_hash = json.loads(hash_the_password.content)
get_password_data = requests.get(secret_url_path, headers=vault_root_token_headers)
password_value = json.loads(get_password_data.content)

# This section parses the json from the responses
password_from_user = pass_hash['data']['sum']
password_from_vault = password_value['data']['data']['password']

# This is the main logic of the login program.  Will error out if any of the conditions fail
if password_from_user == password_from_vault:
    mfa_token = input('Enter the MFA Token: ')
    mfa_data = {"code": mfa_token}
    check_if_token_is_valid = requests.put(totp_endpoint_url, headers=vault_root_token_headers, data=mfa_data)
    if check_if_token_is_valid.status_code != 200:
        print('Code already used; wait until the next time period')
        print('Login Failed')
        exit(0)
    get_validity = json.loads(check_if_token_is_valid.content)
    get_validity = get_validity['data']['valid']
    if get_validity is True:
        print('Login Succeeded')
    else:
        print('Login Failed')
else:
    print('Login Failed')
