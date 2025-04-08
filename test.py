from decpkg import *


def read_json_without_comments():
    with open(CONFIG_JSON, "r") as f:
        jsonc_content = f.read()
        jsonc_content = re.sub(r"//.*", "", jsonc_content)
        jsonc_content = re.sub(r",\s*(]|})", r"\1", jsonc_content)
        data = json.loads(jsonc_content)
        return data[0]


def check_relative_sync():
    json = read_json_without_comments()
    return json["relative_sync"]


def get_aur_helper() -> str:
    try:
        aur = read_json_without_comments()
        aur = aur.get("aur_helper", "")
        return aur
    except KeyError:
        print("\n{YELLOW} ~~~>  'aur_helper' not found in config.")
        return ""


def root_status() -> str:
    json = read_json_without_comments()
    json = json["use_root"]
    return f"{json if json else print('you not have root')}"


def set_noconfirm() -> str:
    data = read_json_without_comments()
    value = data.get("noconfirm", False)

    if not isinstance(value, bool):
        value = False
    return "--noconfirm" if value else ""


def relative_sync_install_pkg():
    jsons = read_json_without_comments()

    # pacman_list = jsons["packages"][0]["pacman"]
    aurhelper_list = jsons.get("AUR-helper", [])
    aurhelper = get_aur_helper()
    root = root_status()
    haven_list = []
    noconfirm = set_noconfirm()
    nohaven_list = []

    aur_haven_list = []
    aur_nohaven_list = []

    print(json.dumps(jsons, indent=2))
    print(aurhelper)
    # print(pacman_list)
    # for pkg in aurhelper_list:
    #     command = f"{aurhelper} -Q {pkg}"
    #     result = subprocess.run(
    #         command,
    #         shell=True,
    #         stdout=subprocess.PIPE,
    #         stderr=subprocess.PIPE,
    #         text=True,
    #     )
    #     if result.returncode == 0:
    #         aur_haven_list.append(
    #             f"{CYAN} ~~>   AUR_package {UNDERLINE}{pkg}{RESET}{GREEN} installed"
    #         )
    #     else:
    #         aur_nohaven_list.append(pkg)
    #
    # for pkg in pacman_list:
    #     command = f"{root} pacman -Q {pkg}"
    #     result = subprocess.run(
    #         command,
    #         shell=True,
    #         stdout=subprocess.PIPE,
    #         stderr=subprocess.PIPE,
    #         text=True,
    #     )
    #     if result.returncode == 0:
    #         haven_list.append(
    #             f"{CYAN} ~~>   package {UNDERLINE}{pkg}{RESET}{GREEN} installed"
    #         )
    #     else:
    #         nohaven_list.append(pkg)
    #
    # for i in haven_list:
    #     print(i)
    #
    # for i in aur_nohaven_list:
    #     print(i)
    #
    # print("▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁")
    #
    # for i in nohaven_list:
    #     print(f" {YELLOW}PACMAN{CYAN} ~~> not found {YELLOW}{UNDERLINE}{i}{RESET}")
    # print()
    #
    # for i in aur_haven_list:
    #     print(f" {MAGENTA}AUR {CYAN} ~~> not found {YELLOW}{UNDERLINE}{i}{RESET}")
    # print()
    #
    # for pkg in nohaven_list:
    #     command = f"{root} pacman -Syu {pkg} {noconfirm}"
    #     os.system(command)
    #
    # for pkg in aur_nohaven_list:
    #     command = f"{aurhelper} -Syu {pkg} {noconfirm}"
    #     os.system(command)


relative_sync_install_pkg()
