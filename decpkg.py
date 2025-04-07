#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
# ▓█████▄ ▓█████  ▄████▄   ██▓███   ██ ▄█▀  ▄████
# ▒██▀ ██▌▓█   ▀ ▒██▀ ▀█  ▓██░  ██▒ ██▄█▒  ██▒ ▀█▒
# ░██   █▌▒███   ▒▓█    ▄ ▓██░ ██▓▒▓███▄░ ▒██░▄▄▄░
# ░▓█▄   ▌▒▓█  ▄ ▒▓▓▄ ▄██▒▒██▄█▓▒ ▒▓██ █▄ ░▓█  ██▓
# ░▒████▓ ░▒████▒▒ ▓███▀ ░▒██▒ ░  ░▒██▒ █▄░▒▓███▀▒
#  ▒▒▓  ▒ ░░ ▒░ ░░ ░▒ ▒  ░▒▓▒░ ░  ░▒ ▒▒ ▓▒ ░▒   ▒
#  ░ ▒  ▒  ░ ░  ░  ░  ▒   ░▒ ░     ░ ░▒ ▒░  ░   ░
#  ░ ░  ░    ░   ░        ░░       ░ ░░ ░ ░ ░   ░
#    ░       ░  ░░ ░               ░  ░         ░
#  ░             ░
#
# (Copyright (c) 2025 maaru.tan \ Marat Arzymatov. All Rights Reserved.)
# https://github.com/maarutan/

# ----------------------------------------------------------------------

# this project was created for declarative interaction with packages
# this project uses
# utelites such as toml yaml
# paru, yay pacman
# popular package managers for archlinux
# this project is strictly for archlinux users.

import os
import subprocess
import argcomplete
import yaml
import toml
import pathlib
import argparse
import shutil
import json
import datetime

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

HOME = pathlib.Path.home()
HERE_YML = pathlib.Path(__file__).parent / "config.yml"
CONFIG_DIR = f"{HOME}/.config/DeclarativePackage"
CONFIG_YML = f"{CONFIG_DIR}/config.yml"
RELATIVE_JSON = f"{CONFIG_DIR}/relative.json"

SETUP_TOML = pathlib.Path(__file__).parent / "pyproject.toml"

RESET = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
REVERSE = "\033[7m"

BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

BACK_BLACK = "\033[40m"
BACK_RED = "\033[41m"
BACK_GREEN = "\033[42m"
BACK_YELLOW = "\033[43m"
BACK_BLUE = "\033[44m"
BACK_MAGENTA = "\033[45m"
BACK_CYAN = "\033[46m"
BACK_WHITE = "\033[47m"


def main():
    if args.aur:
        Aur_helper_soft()
    elif args.version:
        Version()
    elif args.generate:
        GenerateConfigure()
    elif args.sync:
        DecpkgSync()


class DecpkgSync:
    def __init__(self) -> None:
        self.relative = self.check_relative_sync()
        self.absolute = self.check_absolute_sync()
        self.root = self.root_status()
        self.noconfirm = self.set_noconfirm()
        self.aur_helper = self.aur_helper()

        if self.relative and self.absolute:
            print(
                f"\n{YELLOW}WARN: you can't have both 'absolute_sync' and 'relative_sync' set to true"
            )
            self.sync_handler()

        if self.relative:
            self.relative_sync_logic()
            self.relative_sync_install_pkg()

    def relative_sync_install_pkg(self):
        with open(RELATIVE_JSON, "r") as f:
            jsons = json.load(f)

        pacman_list = jsons[0].get("pacman", [])
        aurhelper_list = jsons[1].get("AUR-helper", [])
        aurhelper = self.aur_helper
        haven_list = []
        nohaven_list = []

        aur_haven_list = []
        aur_nohaven_list = []

        for pkg in aurhelper_list:
            command = f"{aurhelper} -Q {pkg}"
            result = subprocess.run(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if result.returncode == 0:
                aur_haven_list.append(
                    f"{CYAN} ~~>   AUR_package {UNDERLINE}{pkg}{RESET}{GREEN} installed"
                )
            else:
                aur_nohaven_list.append(pkg)

        for pkg in pacman_list:
            command = f"{self.root} pacman -Q {pkg}"
            result = subprocess.run(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if result.returncode == 0:
                haven_list.append(
                    f"{CYAN} ~~>   package {UNDERLINE}{pkg}{RESET}{GREEN} installed"
                )
            else:
                nohaven_list.append(pkg)

        for i in haven_list:
            print(i)

        for i in aur_nohaven_list:
            print(i)

        print("▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁")

        for i in nohaven_list:
            print(f" {YELLOW}PACMAN{CYAN} ~~> not found {YELLOW}{UNDERLINE}{i}{RESET}")
        print()

        for i in aur_haven_list:
            print(f" {MAGENTA}AUR {CYAN} ~~> not found {YELLOW}{UNDERLINE}{i}{RESET}")
        print()

        for pkg in nohaven_list:
            command = f"{self.root} pacman -Syu {pkg} {self.noconfirm}"
            os.system(command)

        for pkg in aur_nohaven_list:
            command = f"{self.aur_helper()} -Syu {pkg} {self.noconfirm}"
            os.system(command)

    def aur_helper(self):
        aur = self.read_config().get("aur_helper", [])
        return aur

    def set_noconfirm(self) -> str:
        noconfirm = self.read_config().get("noconfirm", False)
        noconfirm = noconfirm == True
        return "--noconfirm" if noconfirm else ""

    def root_status(self) -> str:
        root = self.read_config().get("use_root", [])
        return f"{root if root else print('you not have root')}"

    def relative_sync_logic(self):
        pathlib.Path(CONFIG_DIR).mkdir(exist_ok=True)
        try:
            pathlib.Path(RELATIVE_JSON).unlink()
        except:
            ""

        if not pathlib.Path(RELATIVE_JSON).exists():
            with open(RELATIVE_JSON, "w") as f:
                default_skilet = {"pacman": [], "aur": []}
                json.dump(default_skilet, f, indent=2)

            with open(CONFIG_YML, "r") as f:
                content = yaml.safe_load(f)

            pacman = content.get("pacman", [])
            aur = content.get("aur", [])

            relative_skilet_aur = {"aur": aur}
            relative_skilet_pacman = {"pacman": pacman}

            with open(RELATIVE_JSON, "w") as f:
                json.dump((relative_skilet_pacman, relative_skilet_aur), f, indent=2)

    def update_configure(self, data: dict):
        yaml = YAML()
        yaml.preserve_quotes = True

        if pathlib.Path(CONFIG_YML).exists():
            with open(CONFIG_YML, "r") as f:
                existing_data = yaml.load(f) or {}
        else:
            existing_data = CommentedMap()

        existing_data.update(data)

        pathlib.Path(CONFIG_DIR).mkdir(exist_ok=True)

        with open(CONFIG_YML, "w") as f:
            yaml.dump(existing_data, f)

    def sync_handler(self):
        ask = input(
            f"{MAGENTA}Choose one to turn false{RESET}\n"
            f"-- [ 1. {YELLOW}absolute_sync{RESET}: {MAGENTA}'true'{RESET}\n"
            f"-- [ 2. {YELLOW}relative_sync{MAGENTA}: 'true'\n"
            f"{CYAN}~~~~> : "
        )
        if ask.lower() in ["1", "absolute"]:
            config_update = {"absolute_sync": "false"}

        elif ask.lower() in ["2", "relative"]:
            config_update = {"relative_sync": "false"}

        else:
            print(f"\n{RED}   ~~~   failed to record     :( ")

        if "config_update" in locals():
            self.update_configure(config_update)  # type: ignore

    def read_config(self):  # type: ignore
        yaml = YAML()
        with open(CONFIG_YML, "r") as f:
            return yaml.load(f)

    def check_relative_sync(self):  # type: ignore
        relative_sync = self.read_config().get("relative_sync", False)
        return relative_sync == True

    def check_absolute_sync(self):  # type: ignore
        absolute_sync = self.read_config().get("absolute_sync", False)
        return absolute_sync == True

    def read_config(self):
        with open(CONFIG_YML, "r") as f:
            return yaml.safe_load(f)

    def check_relative_sync(self):
        relative_sync = self.read_config().get("relative_sync", False)
        return relative_sync == True

    def check_absolute_sync(self):
        absolute_sync = self.read_config().get("absolute_sync", False)
        return absolute_sync == True


class GenerateConfigure:
    def __init__(self) -> None:
        if not pathlib.Path(CONFIG_YML).exists():
            self.write_config()
            print(f"{YELLOW}configure file: {CONFIG_YML} {MAGENTA}created :D")
        else:
            self.handle_existing_config()

    def config_here(self):
        default_config = """ 
# ▓█████▄ ▓█████  ▄████▄   ██▓███   ██ ▄█▀  ▄████
# ▒██▀ ██▌▓█   ▀ ▒██▀ ▀█  ▓██░  ██▒ ██▄█▒  ██▒ ▀█▒
# ░██   █▌▒███   ▒▓█    ▄ ▓██░ ██▓▒▓███▄░ ▒██░▄▄▄░
# ░▓█▄   ▌▒▓█  ▄ ▒▓▓▄ ▄██▒▒██▄█▓▒ ▒▓██ █▄ ░▓█  ██▓
# ░▒████▓ ░▒████▒▒ ▓███▀ ░▒██▒ ░  ░▒██▒ █▄░▒▓███▀▒
#  ▒▒▓  ▒ ░░ ▒░ ░░ ░▒ ▒  ░▒▓▒░ ░  ░▒ ▒▒ ▓▒ ░▒   ▒
#  ░ ▒  ▒  ░ ░  ░  ░  ▒   ░▒ ░     ░ ░▒ ▒░  ░   ░
#  ░ ░  ░    ░   ░        ░░       ░ ░░ ░ ░ ░   ░
#    ░       ░  ░░ ░               ░  ░         ░
#  ░             ░
#
# (Copyright (c) 2025 maaru.tan \\ Marat Arzymatov. All Rights Reserved.)
# https://github.com/maarutan/decpkg 
#
# ------------------------------------------------
#
# Startup
absolute_sync: false # absolute installation where you clearly specify what to remove and what to install if a package is not in the list, then it will be removed. 
relative_sync: true # Relative package installation it you can determine which packages to install but not remove, If you installed through the carrier option you will have to uninstall manually. 
#
# Updates package
update_pkg_with_install: false # You can upgrade your system before you start installing your packages.
update_counter: false # If you choose to update the system before installation you can see the number of updates. 
#
# set root
use_root: "sudo"  # To install packages you need to have super user rights in order to install them. 
#
aur_helper: "paru" # Better aur helper utils.
noconfirm : true # If that's true, then the packets will settle without confirmation.  
#
# Other 
notify: false # If you want to be notified.
#
# install the package using declarative.
pacman:
  # - git         # Popular utelita for version control.
  # - neovim      # Best text editor.
#
# install your package from Arch User Repository.
aur:
  # - peaclock    # Utelita for look clock.
  # - unimatrix   # Huckers background.
        """
        return default_config

    def write_config(self):
        config_path = pathlib.Path(CONFIG_YML)

        if config_path.exists():
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = config_path.with_suffix(f".bak.{timestamp}")
            shutil.copy2(config_path, backup_path)
            print(f"{CYAN}Backup created at: {backup_path}")

        with open(config_path, "w") as f:
            f.write(self.config_here())

    def handle_existing_config(self):
        ask = (
            input(
                f"{YELLOW}configure file: {CONFIG_YML} {MAGENTA}now exists\n"
                f"{CYAN}~~~ Do you want to replace? [ ( y/N ) ]\n ~> : "
            )
            .strip()
            .lower()
        )

        match ask:
            case "y":
                self.write_config()
                print(f"{YELLOW}configure file replaced successfully!")
            case "n" | "":
                print(f"\n {MAGENTA}   ~~ good ")
            case _:
                print(f"\n {RED}~~~~~~   I don't know what the problem is :(")


class Aur_helper_soft:
    def __init__(self) -> None:
        ask = input(
            f"   \n"
            f"   {YELLOW}~~~~> [ 1. | `paru` |{RESET}"
            f"   \n"
            f"   {YELLOW}~~~~> [ 2. | `yay ` |{RESET}"
            f"   \n"
            f"   {MAGENTA}|~~> : "
        )
        if ask.lower() in {"paru", "1"}:
            self.manual_paru()
        elif ask.lower() in ["yay", "2"]:
            self.manual_yay()
        else:
            print("\n        ~~ sory only `paru` and `yay`    :(  ")

    def manual_paru(self):
        if not shutil.which("paru"):
            ask = input(
                f"\n{MAGENTA}|------------------------------------|\n"
                f"{MAGENTA}| manual install {YELLOW}{UNDERLINE}`paru`{RESET}{GREEN} with deckpkg |\n"
                f"{MAGENTA}| ~~~~> {UNDERLINE}( Y/n ){RESET} ]--------------------|\n"
                f"{CYAN}| ~> : "
            )
            if ask.lower() in ["y", ""]:
                if shutil.which("git"):
                    try:
                        print(f"{CYAN}Cloning paru from AUR...{RESET}")
                        subprocess.check_call(
                            [
                                "git",
                                "clone",
                                "https://aur.archlinux.org/paru.git",
                                "/tmp/paru/",
                            ]
                        )
                        print(f"{CYAN}Building package...{RESET}")
                        subprocess.check_call(["makepkg", "-si"], cwd="/tmp/paru/")
                    except:
                        print(f"{RED}Error: Installation failed!{RESET}")
                else:
                    print(
                        f"{RED}Error: git not found, please install git first!{RESET}"
                    )
        else:
            print(f"{GREEN}paru is already installed.{RESET}")

    def manual_yay(self):
        if not shutil.which("yay"):
            ask = input(
                f"\n{MAGENTA}|-----------------------------------|\n"
                f"{MAGENTA}| manual install {YELLOW}{UNDERLINE}`yay`{RESET}{GREEN} with deckpkg |\n"
                f"{MAGENTA}| ~~~~> {UNDERLINE}( Y/n ){RESET} ]-------------------|\n"
                f"{CYAN}| ~> : "
            )
            if ask.lower() in ["y", ""]:
                if shutil.which("git"):
                    try:
                        print(f"{CYAN}Cloning yay from AUR...{RESET}")
                        subprocess.check_call(
                            [
                                "git",
                                "clone",
                                "https://aur.archlinux.org/yay.git",
                                "/tmp/yay/",
                            ]
                        )
                        print(f"{CYAN}Building package...{RESET}")
                        subprocess.check_call(["makepkg", "-si"], cwd="/tmp/yay/")
                    except subprocess.CalledProcessError as e:
                        print(f"{RED}Error: Installation failed!{RESET}")
                else:
                    print(
                        f"{RED}Error: git not found, please install git first!{RESET}"
                    )
        else:
            print(f"{GREEN}yay is already installed.{RESET}")


class Version:
    def __init__(self) -> None:
        ask = input(
            f"   \n"
            + (f"\n   {YELLOW}~~~~> [ 0. | `decpkg` |{RESET} ")
            + (
                f"\n   {YELLOW}~~~~> [ 1. | `pacman` |{RESET} "
                if shutil.which("pacman")
                else ""
            )
            + (
                f"\n   {YELLOW}~~~~> [ 2. |  `paru`  |{RESET} "
                if shutil.which("paru")
                else ""
            )
            + (
                f"\n   {YELLOW}~~~~> [ 3. |  `yay`  |{RESET} "
                if shutil.which("yay")
                else ""
            )
            + f"\n   {MAGENTA}|~~> : "
        )

        if ask.lower() in {"decpkg", "0"}:
            self.decpkg_version()
        elif ask.lower() in {"pacman", "1"} and shutil.which("pacman"):
            self.pacman_version()
        elif ask.lower() in {"paru", "2"} and shutil.which("paru"):
            self.paru_version()
        elif ask.lower() in {"yay", "3"} and shutil.which("yay"):
            self.yay_version()
        else:
            print(
                "\n        ~~ Sorry, only `paru`, `yay`, and `pacman` are available. :( "
            )

    def decpkg_version(self):
        print(
            """
    ┌┬┐┌─┐┌─┐┌─┐┬┌─┌─┐
     ││├┤ │  ├─┘├┴┐│ ┬
    ─┴┘└─┘└─┘┴  ┴ ┴└─┘
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
    """
        )

        with open(SETUP_TOML, "r") as f:
            config = toml.load(f)

        print(f"  ~~~>  Name: {config['project']['name']}")
        print(f"  ~~~>  Version: {config['project']['version']}")
        print(f"  ~~~>  Requires Python: {config['project']['requires-python']}")

    def pacman_version(self, V: bool = True):
        subprocess.check_call(["pacman", "-V"]) if V else subprocess.check_call(
            ["pacman", "-v"]
        )

    def paru_version(self):
        if shutil.which("paru"):
            print("""
    ┌─┐┌─┐┬─┐┬ ┬
    ├─┘├─┤├┬┘│ │
    ┴  ┴ ┴┴└─└─┘
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
            """)
            subprocess.check_call(["paru", "-V"])
        else:
            print(f"\n{RED}Error: {UNDERLINE}`paru`{RESET} not found")

    def yay_version(self):
        if shutil.which("yay"):
            print("""
    ┬ ┬┌─┐┬ ┬
    └┬┘├─┤└┬┘
     ┴ ┴ ┴ ┴
▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
            """)
            subprocess.check_call(["yay", "-V"])
        else:
            print(f"\n{RED}Error: {UNDERLINE}`yay`{RESET} not found")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="declarative package manager")
    parser.add_argument("-s", "--sync", action="store_true", help="Sync `deckpkg`")
    parser.add_argument("-r", "--remove", action="store_true", help="Remove `deckpkg`")
    parser.add_argument(
        "-v", "--version", action="store_true", help="Version `deckpkg`"
    )
    parser.add_argument(
        "-g", "--generate", action="store_true", help="Generate `deckpkg`"
    )
    parser.add_argument("-c", "--config", action="store_true", help="Config `deckpkg`")
    parser.add_argument(
        "-a",
        "--aur",
        action="store_true",
        help="paru or yay for `AUR` in `deckpkg`",
    )

    argcomplete.autocomplete(parser)
    args, unknown = parser.parse_known_args()

    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n {MAGENTA}     ~~ cancel ^^")
