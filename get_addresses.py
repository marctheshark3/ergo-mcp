import json
import time

def main():
    address_to_height = {}
    offset = 0

    while True:
        data = fetch_boxes(offset, LIMIT)
        items = data.get("items", [])
        if not items:
            break

        for item in items:
            address = item.get("address")
            height = item.get("inclusionHeight")
            if address:
                # Store the latest (highest offset, i.e., most recent) blockheight for each address
                if address not in address_to_height or height > address_to_height[address]:
                    address_to_height[address] = height

        if len(items) < LIMIT:
            break

        offset += LIMIT
        time.sleep(0.1)

    # Output as a mapping of address to blockheight
    with open(OUTPUT_FILE, "w") as f:
        json.dump(address_to_height, f, indent=2)
    print(f"Saved {len(address_to_height)} unique addresses with blockheights to {OUTPUT_FILE}") 