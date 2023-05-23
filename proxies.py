"""

Lynix's functionality includes 2 different types of proxy parsing
1. dkmwdckk:zdo37eu16s06@45.142.28.83:8094 (semi-converted proxy format)
2. 138.128.97.239:7829:dohtvdoc:5ma6i9k8m8la (webshare.io format)

"""

from random import random, shuffle
import random
import os
import traceback

user_proxies = ["45.140.13.119:9132", ""]
proxy_index = 0
current_proxy = user_proxies[proxy_index]


def parse_proxies() -> None:
    """
    Parses user proxies from proxies.txt and appends them into user_proxies
    """
    try:
        with open("proxies.txt") as proxy_file:
            for line in proxy_file:
                line = line.replace("\n", "")
                if (
                    line.find("@") != -1
                ):  # If the line is in semi-converted proxy format
                    # dkmwdckk:zdo37eu16s06@45.142.28.83:8094
                    user_proxies.append(str(line))
                else:  # Webshare.io format
                    # 138.128.97.239:7829:dohtvdoc:5ma6i9k8m8la
                    proxy = line.split(":")
                    if len(proxy) < 3:
                        proxy_ip = str(proxy[0])
                        proxy_port = str(proxy[1])
                        user_proxies.append(proxy_ip + ":" + proxy_port)
                        continue
                    proxy_ip = str(proxy[0])
                    proxy_port = str(proxy[1])
                    proxy_user = str(proxy[2])
                    proxy_pass = str(proxy[3])
                    user_proxies.append(
                        proxy_user
                        + ":"
                        + proxy_pass
                        + "@"
                        + proxy_ip
                        + ":"
                        + proxy_port
                    )
        shuffle(user_proxies)
    except:
        print("Unable to parse proxies. Please try again!")
        traceback.print_exc()
        os._exit(-1)


proxies = [
    "45.142.28.83:8094",
    "45.137.60.112:6640",
    "45.140.13.124:9137",
    "45.140.13.112:9125",
    "45.142.28.20:8031",
    "45.140.13.119:9132",
    "45.142.28.145:8156",
    "45.142.28.187:8198",
    "176.116.230.128:7214",
    "176.116.230.151:7237",
]


def get_random_proxy() -> str:
    """
    Returns random proxy from saved user_proxies list
    """
    return random.choice(proxies)  # "45.140.13.119:9132"
