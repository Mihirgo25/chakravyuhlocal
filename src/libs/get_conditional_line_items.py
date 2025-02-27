def get_filtered_line_items(rate:dict, line_items:list):
    '''
        1. Line items are evaluated based on user-defined conditions.
        2. Each condition is checked using specified operators and criteria.
        3. The best line item is selected based on the highest number of satisfied conditions in case of duplicate line item code.
           If multiple line items have the same number of satisfied conditions, the one with the highest price is chosen.

    '''
    item_conditions_mapping = {}
    new_line_items = []
    for item in line_items:
        conditions = item.get('conditions')
        charge_code = item['code']
        if conditions and validate_conditions(conditions):
            operator = conditions.get('operator')
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
        if sorted_data:
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
    if 'values' in conditions:
        if len(conditions['values']) > 1 and 'operator' not in conditions:
            return False
        return True
    return False


def evaluate_conditions(rate, operator, values):

    true_count = 0 
    if not operator:
        is_condition = check_condition(rate,values[0])
        if is_condition:
            true_count += 1
        return true_count, is_condition
   
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
    key = condition['condition_key']
    operator = condition['operand'].lower()
    condition_value = condition['condition_value']
    if operator == "in":
        if rate.get(key) in condition_value:
            return True
    if operator == "not_in":
        if rate.get(key) not in condition_value:
            return True
    if operator == "equal_to" and rate.get(key) == condition_value:
        return True
    if operator == "not_equal_to" and rate.get(key) != condition_value:
        return True
    if operator == "greater_than" and rate.get(key) > condition_value:
        return True
    if operator == "less_than" and rate.get(key) < condition_value:
        return True
    return False
