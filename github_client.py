import time
from pathlib import Path

import jwt
import requests


class GitHubClient:
    BASE_URL = "https://api.github.com"
    API_VERSION = "2022-11-28"

    def __init__(self, config):
        self.config = config
        self.session = requests.Session()

        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": self.API_VERSION,
            }
        )

    def generate_jwt(self):
        key_path = Path(self.config["private_key_path"]).expanduser()

        private_key = key_path.read_text()
        now = int(time.time())

        payload = {"iat": now - 60, "exp": now + 540, "iss": self.config["app_id"]}

        return jwt.encode(payload, private_key, algorithm="RS256")

    def authenticate(self):
        signed_jwt = self.generate_jwt()
        installation_id = self.config["installation_id"]

        url = f"{self.BASE_URL}/app/installations/{installation_id}/access_tokens"

        response = self.session.post(
            url,
            headers={"Authorization": f"Bearer {signed_jwt}"},
            json={"permissions": {"organization_administration": "read"}},
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        self.session.headers.update({"Authorization": f"Bearer {data['token']}"})

        return data["expires_at"]

    def get(self, endpoint):
        response = self.session.get(
            f"{self.BASE_URL}/{endpoint.lstrip('/')}", timeout=30
        )

        response.raise_for_status()

        return response.json()

    def close(self):
        self.session.close()
