


def create_env() -> None:
    with open('.env', 'w') as env_file:
        env_file.write('api_key = ')