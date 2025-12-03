from random import choice as random_choice
from string import ascii_letters, digits


def generate_token(lenght=16):
    allowed_chars = ascii_letters + digits
    token = ''.join(random_choice(allowed_chars) for _ in range(lenght))
    return token

def save_env(auth_token: str):
    with open(".env", "w") as f:
        f.write(f"AUTH_TOKEN={auth_token}")

if __name__ == "__main__":
    token = generate_token()
    save_env(token)
