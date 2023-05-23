"""
Sniping Module - Contains essential functions for price checking
"""
from base64 import decode
import json
import proxies
import requests
import https


ROBLOX_COOKIE = "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_E2D7445306CAB036575D49D2445DA7D86653A6830229E7BE38C97F13FD2B4BA9A92437BD53CF9E7D26F4A02657E8655D5DB6CB91DD8874491B575B43E634C79E98F7ECC9890F33E85FF8850335F25139E87F5C1C1DC0AC297F4D1944DB674BBAC28BB8162BAFE42F2DFA3189F9DA838E8DB1C9340EC225008F9BA0B8EC863A42D2D1891F2FB4861DC6D5749A57BA36E0056B398707EAEC471B3EBC18ADBA5EE63BDBA832E3BF3FF54631819FBADFA6ED0F51B6640387BE877DBE7F2066126140BE2A7095F21B513362BD7B22496344529D4492D7E1FF5D64C7D63E47B77F99CE640AEBC9BC7E324564095151D54DC20494D792D823393EBD7327419C80A83BEFF14EA7C24FAAB9E1655CE04117AA7835A03C1D91595ED7A47FAAB7B1DCAD2AD1B5925AAD7847D5C54791446DA9BE94D2752C0F036ABF7893395218A9A8B328C68E3D6CEA0775CC187501B650B14301B2D10A8AB1A46C770F3DAC23B79BCA5EF7087B4EFAA9847695A430823086C5E2650410C48F"
proxies.parse_proxies()
print(proxies.get_random_proxy())

# 45.140.13.119:9132


def get_csrf_token(cookie: str) -> str:
    """
    Returns CSRF token, usable for making requests
    """

    headers = {
        "User-Agent": https.get_random_agent(),
        "Cookie": ".ROBLOSECURITY=" + cookie,
    }

    token = https.create_request(
        "POST",
        "catalog.roblox.com",
        "/v1/catalog/items/details",
        proxies=None,
        headers=headers,
    )

    if "x-csrf-token" in token.headers:
        return str(token.headers["x-csrf-token"])
    return False


def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""


def get_item_name_by_id(item_id: int) -> str:
    """
    Returns item name from items webpage
    *USES REQUEST MODULE*
    """
    try:
        page = requests.get(
            "https://www.roblox.com/catalog/" + str(item_id),
        )
        return find_between(page.text, "<title>", " - Roblox<").replace(" ", "-")
    except Exception as e:
        print(e)


def https_snipe(item_id: int, item_name: str) -> int:
    """
    Returns items price from https webpage, returns -1 if rate limited
    """

    item_url = "/catalog/" + str(item_id) + "/" + str(item_name)

    conn = https.create_request(
        "GET",
        "www.roblox.com",
        item_url,
        proxies=proxies.get_random_proxy(),  # proxies.get_random_proxy()
    )

    if conn.status != 200:
        return -1

    text = str(conn.read().decode("UTF-8"))

    return int(
        find_between(
            text,
            '<span class="text-robux-lg wait-for-i18n-format-render ">',
            "</span>",
        ).replace(",", "")
    )


def inventory_snipe(inventory_user_id: int, item_id: int, asset_type: int) -> int:
    """
    Returns price based on user who has the item in their inventory
    """
    inventory_url = (
        "/users/inventory/list-json?userId="
        + str(inventory_user_id)
        + "&assetTypeId="
        + str(asset_type)
        + "&itemsPerPage=100",
    )

    conn = https.create_request(
        "GET",
        "www.roblox.com",
        inventory_url[0],
        proxies=proxies.get_random_proxy(),  # proxies.get_random_proxy()
    )

    if conn.status != 200:
        return -1

    for data in json.loads(conn.read().decode("utf-8"))["Data"]["Items"]:
        if int(data["Item"]["AssetId"]) == item_id:
            item_price = data["Product"]["PriceInRobux"]
            if item_price != None:
                return item_price
            return 0
    print("User does not have item in inventory")
    return -1


def catalog_details_snipe(item_id: int) -> int:
    """
    Returns price using catalog details
    """
    data = {"items": [{"itemType": "Asset", "id": int(item_id)}]}
    headers = {
        "X-CSRF-TOKEN": get_csrf_token(ROBLOX_COOKIE),
        "User-Agent": https.get_random_agent(),
        "Referer": "https://www.roblox.com/my/account",
        "Content-Type": "application/json",
        "Origin": "https://www.roblox.com",
        "Cookie": ".ROBLOSECURITY=" + ROBLOX_COOKIE,
    }
    conn = https.create_request(
        "POST",
        "catalog.roblox.com",
        "/v1/catalog/items/details",
        proxies=proxies.get_random_proxy(),
        headers=headers,
        body=json.dumps(data),
    )

    if conn.status != 200:
        return -1

    return int(json.loads(conn.read().decode("UTF-8"))["data"][0]["lowestPrice"])


def resellers_snipe(item_id: int) -> int:
    "Returns item price through resellers API"

    headers = {
        "X-CSRF-TOKEN": get_csrf_token(ROBLOX_COOKIE),
        "User-Agent": https.get_random_agent(),
        "Referer": "https://www.roblox.com/my/account",
        "Origin": "https://www.roblox.com",
        "Cookie": ".ROBLOSECURITY=" + ROBLOX_COOKIE,
    }
    reseller_url = "/v1/assets/" + str(item_id) + "/resellers"

    conn = https.create_request(
        "GET",
        "economy.roblox.com",
        reseller_url,
        proxies=proxies.get_random_proxy(),
        headers=headers,
    )

    if conn.status != 200:
        return -1
    return int(json.loads(str(conn.read().decode("UTF-8")))["data"][0]["price"])


def favorites_snipe(favorited_user_id: int, item_id: int, asset_type: int) -> int:
    """
    Returns item price through favorites api
    PRE-CONDITION: USER MUST HAVE ITEM IN FAVORITES
    """

    favorites_url = (
        "/users/favorites/list-json?assetTypeId="
        + str(asset_type)
        + "&userId="
        + str(favorited_user_id)
    )

    conn = https.create_request(
        "GET", "www.roblox.com", favorites_url, proxies=proxies.get_random_proxy()
    )

    if conn.status != 200:
        return -1

    data = json.loads(conn.read().decode("UTF-8"))["Data"]["Items"]
    for item in data:
        if int(item["Item"]["AssetId"]) == item_id:
            price = item["Product"]["PriceInRobux"]
            if price != None:
                return price
            return 0
    print(
        "User: "
        + str(favorited_user_id)
        + " does not have "
        + str(item_id)
        + "in favorites list"
    )


def catalog_v1_snipe(item_id: int, item_name: str) -> int:
    """
    Returns itemid's price from catalog api v1
    PRE-CONDITION: item_name must be from get_item_name_by_id()
    """

    catalog_url = "/v1/search/items/details?Category=2&Subcategory=2&SortType=1&SortAggregation=4&Limit=30&CreatorName=ROBLOX&Keyword=" + str(
        item_name
    ).replace(
        "-", "%20"
    )

    conn = https.create_request(
        "GET", "catalog.roblox.com", catalog_url, proxies=proxies.get_random_proxy()
    )

    if conn.status != 200:
        return -1

    data = json.loads(conn.read().decode("UTF-8"))

    for item in data["data"]:
        if item["id"] == item_id:
            return int(item["lowestPrice"])

    print("Item was unable to be found using catalog/v1, try different keyword")
    return -1


def catalog_v2_snipe(item_id: int, item_name: str) -> int:
    """
    Returns itemid's price from catalog api v2
    PRE-CONDITION: item_name must be from get_item_name_by_id()
    """

    catalog_url = (
        "/v2/search/items/details?Category=2&Subcategory=2&SortType=1&SortAggregation=4&Limit=30&CreatorName=ROBLOX&Keyword="
        + str(item_name)
    ).replace("-", "%20")

    conn = https.create_request(
        "GET",
        "catalog.roblox.com",
        str(catalog_url),
        proxies=proxies.get_random_proxy(),
    )

    if conn.status != 200:
        return -1

    data = json.loads(conn.read().decode("UTF-8"))

    for item in data["data"]:
        if item["id"] == item_id:
            return int(item["lowestPrice"])

    print("Item was not found with catalog search v2, trying different endpoint ")
    new_url = catalog_url.replace("SortType=1", "SortType=0")

    conn = https.create_request(
        "GET",
        "catalog.roblox.com",
        str(new_url),
        proxies=proxies.get_random_proxy(),
    )

    for item in data["data"]:
        if item["id"] == item_id:
            return int(item["lowestPrice"])

    return -1


def rolimons_snipe(item_id: int) -> int:
    """
    Returns item_id's lowest price through Rolimon's /deals api
    *DOES NOT USE PROXY*
    """

    conn = https.create_request(
        "GET", "www.rolimons.com", "/deals", proxies=proxies.get_random_proxy()
    )

    if conn.status != 200:
        return -1

    return int(
        eval(
            find_between(
                find_between(conn.read().decode("UTF-8"), "var item_activity =", "}"),
                '"' + str(item_id) + '":',
                "]",
            )
            + "]"
        )[2]
    )


import time

RATE_LIMITS = {
    "HTTP_LIMITED": False,
    "INVENTORY_LIMITED": False,
    "CATALOG_DETAILS_LIMITED": False,
    "RESELLERS_LIMITED": False,
    "FAVORITES_LIMITED": False,
    "CATALOG_V1_LIMITED": False,
    "CATALOG_V2_LIMITED": False,
}


def snipe(
    inventory_user_id: int, favorited_user_id: int, item_id: int, asset_type: int
) -> None:
    # Testing not finished obv
    item_name = get_item_name_by_id(item_id)
    while True:
        try:
            if not RATE_LIMITS["HTTP_LIMITED"]:
                if https_snipe(item_id, item_name) != -1:
                    print("HTTP Sniped")
                    continue
                RATE_LIMITS["HTTP_LIMITED"] = True
            if not RATE_LIMITS["INVENTORY_LIMITED"]:
                if inventory_snipe(inventory_user_id, item_id, asset_type) != -1:
                    print("INVENTORY Sniped")
                    continue
                RATE_LIMITS["INVENTORY_LIMITED"] = True
            if not RATE_LIMITS["CATALOG_DETAILS_LIMITED"]:
                if catalog_details_snipe(item_id) != -1:
                    print("CATALOG DETAILS Sniped")
                    continue
                RATE_LIMITS["CATALOG_DETAILS_LIMITED"] = True
            if not RATE_LIMITS["RESELLERS_LIMITED"]:
                if resellers_snipe(item_id) != -1:
                    print("RESELLER Sniped")
                    continue
                RATE_LIMITS["RESELLERS_LIMITED"] = True
            if not RATE_LIMITS["FAVORITES_LIMITED"]:
                if favorites_snipe(favorited_user_id, item_id, asset_type) != -1:
                    print("FAVORITED Sniped")
                    continue
                RATE_LIMITS["FAVORITES_LIMITED"] = True
            if not RATE_LIMITS["CATALOG_V1_LIMITED"]:
                if catalog_v1_snipe(item_id, item_name) != -1:
                    print("CATALOGV1 Sniped")
                    continue
                RATE_LIMITS["CATALOG_V1_LIMITED"] = True
            if not RATE_LIMITS["CATALOG_V2_LIMITED"]:
                if catalog_v2_snipe(item_id, item_name) != -1:
                    print("CATALOGV2 Sniped")
                    continue
                RATE_LIMITS["CATALOG_V2_LIMITED"] = True
            print("Rate Limited")
        except Exception as exc:
            pass
            # print(exc)


# print(get_item_name_by_id(1028606))
# print(https_snipe(1028606, get_item_name_by_id(1028606)))
# snipe(3572679636, 3730614906, 1028606, asset_types.HAT_ASSET_TYPE)
# print(inventory_snipe(3572679636, 1028606, asset_types.HAT_ASSET_TYPE))
