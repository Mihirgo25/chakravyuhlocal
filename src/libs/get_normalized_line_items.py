def get_normalized_line_items(line_items):
    if isinstance(line_items,list):
        for item in line_items:  
            item["market_price"] = item.get('market_price') or item['price']
            item["original_price"] = item.get('original_price') or item['price']
        return line_items
    else:
        return []