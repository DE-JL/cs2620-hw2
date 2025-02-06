import sys
import yaml
from nicegui import ui

# Load YAML configuration
def load_config(file_path):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def on_sign_in(username):
    ui.notify(f"Signing in as {username.value}")

def on_sign_up(username):
    ui.notify(f"Signing up as {username.value}")


def main():
    config = load_config("config.yaml")

    with ui.card().tight():
        ui.label("Login").classes("text-h5")

        username = ui.input("Username").classes("w-full")
        password = ui.input("Password").classes("w-full")

        with ui.row():
            ui.button("Sign In").classes("w-1/2")
            ui.button("Sign Up").classes("w-1/2")

if __name__ == '__main__':
    main()


ui.run()
