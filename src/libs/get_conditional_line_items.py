def get_filtered_line_items(rate:dict, line_items:list):
    '''
        Line Items are added based on the conditions 
        given by user

        1. Each condition is evaluated based on given operator and few conditions.
        2. After satisfying conditions they are appended to line items
    
    '''
    item_conditions_mapping = {}
    new_line_items = []
    for item in line_items:
        conditions = item.get('conditions')
        charge_code = item['code']
        if conditions and validate_conditions(conditions):
            operator = conditions['operator']
            values = conditions['values']
            count, condition_met = evaluate_conditions(rate, operator, values)
            if condition_met:
                if charge_code in item_conditions_mapping:
                    item_conditions_mapping[charge_code].append((item, item['price'], count))
                else:
                    item_conditions_mapping[charge_code] = [(item, item['price'], count)]
        else:
            if not charge_code in item_conditions_mapping:
                new_line_items.append(item)
                
    for key,data in item_conditions_mapping.items():
        sorted_data = sorted(data, key=lambda x: (x[2], x[1]), reverse=True)
        best_line_item = sorted_data[0][0]
        index = find_charge_code_index(new_line_items,key)
        if index is not None:
            new_line_items[index]=best_line_item
        else:
            new_line_items.append(best_line_item)

    return new_line_items


def find_charge_code_index(new_line_items,charge_code):
    for index, existing_item in enumerate(new_line_items):
        if existing_item['code'] == charge_code:
           return index
    return None

def validate_conditions(conditions):
    if 'operator' in conditions and 'values' in conditions:
        return True
    return False

def evaluate_conditions(rate, operator, values):
    true_count = 0 
    if operator == "or":
        for val in values:
            if check_condition(rate, val):
                true_count += 1
        return true_count, true_count > 0  
    if operator == "and":
        for val in values:
            if check_condition(rate, val):
                true_count += 1
        return true_count, true_count == len(values) 
    return 0, False  


def check_condition(rate, condition):
    key = condition[0]
    operator = condition[1].lower()
    operand = condition[2]
    if operator == "in":
        if rate.get(key) in operand:
            return True
    if operator == "not_in":
        if rate.get(key) not in operand:
            return True
    if operator == "equal_to" and rate.get(key) == operand:
        return True
    if operator == "not_equal_to" and rate.get(key) != operand:
        return True
    if operator == "greater_than" and rate.get(key) > operand:
        return True
    if operator == "less_than" and rate.get(key) < operand:
        return True
    return False
