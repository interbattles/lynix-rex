import threading
import sniper
import asset_types
import proxies

NUMBER_OF_THREADS = 10


def main():
    print(len(proxies.proxies))
    print("[+] Welcome to Lynix Snipe Bot, Loading settings..")
    print("[+] Loading " + str(NUMBER_OF_THREADS) + " threads!")
    for x in range(0, NUMBER_OF_THREADS):
        thread = threading.Thread(
            target=sniper.snipe,
            args=(3572679636, 3730614906, 1028606, asset_types.HAT_ASSET_TYPE),
        )
        thread.start()
        print("[+] Sucessfully started thread #" + str(x))


main()
