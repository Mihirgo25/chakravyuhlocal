def get_normalized_line_items(line_items):
    if isinstance(line_items,list):
        return [ item | {"market_price": item.get('market_price') or item['price']} for item in line_items]  
    else:
        return []