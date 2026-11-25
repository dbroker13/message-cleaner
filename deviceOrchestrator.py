from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import argparse
from hs_apis import HS_API
# from RCSCleaner import clean_device
import RCSCleaner as messenger
import WhatsAppCleaner as whatsapp
import iMessageCleaner as imessage
import os


APITOKEN = os.getenv('Messages_API_Token')
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
APP_MODULES = {
    "messenger": messenger,
    "whatsapp": whatsapp,
    "imessage": imessage
}
def parse_args():
    parser = argparse.ArgumentParser(description="Validate new device setups on the HeadSpin device farm.")
    parser.add_argument(
        "--app",
        required=True,
        choices=sorted(APP_MODULES),
        help="Which check module(s) to run. 'mobile' runs android+ios together into one combined report.",
    )
    target = parser.add_mutually_exclusive_group()
    target.add_argument("--device-id", help="Validate only this device.")
    # target.add_argument("--hostname", help="Validate all eligible devices on this proxy host.")
    parser.add_argument("--max-workers", type=int, default=5, help="Concurrent device validations (default: 5).")
    # parser.add_argument("--output", help="Report output path (default: timestamped file in this folder).")
    return parser.parse_args()

def filter_devices(device_list):
    skipped = []
    holder = device_list.copy()
    for device in holder:
        device_id = device.get("device_id")
        device_address = device.get("device_address")

        def skip(reason):
            device_list.remove(device)
            logging.info(f"Skipping {device_id}: {reason}")
            skipped.append({"device_id": device_id, "device_address": device_address, "reason": reason})

        if device.get("owner_email") is not None:
            skip(f"currently owned/checked out by {device['owner_email']}")
            continue
    return device_list, skipped

def main():
    args = parse_args()
    script = APP_MODULES[args.app]
    hsapi = HS_API(api_token=APITOKEN)
    logging.info(f"User choice {script}")
    if args.device_id:
        #assume user will correctly link app request and device
        device_list = hsapi.fetch_devices(f"device_id:{args.device_id}") 
    else:
        if args.app == 'imessage':
            device_list = hsapi.fetch_devices(f"device_type:ios")
        elif args.app == 'whatsapp':
            #flagging just android RN will need to add iOS later on
            device_list = hsapi.fetch_devices(f"device_type:android+device_note:*Whatsapp*")
            #check for whatsApp note
        else:
            device_list = hsapi.fetch_devices(f"device_type:android")
    if not device_list:
        logging.error("Failed to acquire device list")
        return
    device_list, skipped = filter_devices(device_list)
    logging.info(f"Cleaning {len(device_list)} device(s)")
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_device = {}
        for device in device_list:
            future = executor.submit(script.clean_device, device)
            future_to_device[future] = device
            total = len(future_to_device)
            completed = 0
        for future in as_completed(future_to_device):
            device = future_to_device[future]
                # try:
                #     report["devices"].append(future.result())
                # except Exception as exc:
                #     logging.error(f"{device.get('device_id')}: validation crashed: {exc}")
                #     report["devices"].append({"device_id": device.get("device_id"), "error": str(exc)})
            completed += 1
            logging.info(f"Progress: {completed}/{total} devices complete ({device.get('device_id')})")
        


if __name__ == "__main__":
    main()