def adjusted_price_for_flash_booking(line_item, markup):
    if markup > line_item["price"]:
        line_item["original_price"] = line_item["price"] if "original_price" not in line_item else line_item.get("original_price")
        line_item["price"] = markup
        return True

    return False