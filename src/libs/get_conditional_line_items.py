def get_filtered_line_items(rate:dict, line_items:list):
    '''
        Line Items are added based on the conditions 
        given by user

        1. Each condition is evaluated based on given operator and few conditions.
        2. After satisfying conditions they are appended to line items
    
    '''
    new_line_items = []
    for item in line_items:
        conditions = item.get('conditions')
        if conditions and validate_conditions(conditions):
            operator = conditions['operator']
            values = conditions['values']
            condition_met = evaluate_conditions(rate, operator, values)
            if condition_met:
                new_line_items.append(item)
        else:
            new_line_items.append(item)
    return new_line_items

def validate_conditions(conditions):
    if 'operator' in conditions and 'values' in conditions:
        return True
    return False

def evaluate_conditions(rate, operator, values):
    if operator == "or":
        return any(check_condition(rate, val) for val in values)
    if operator == "and":
        return all(check_condition(rate, val) for val in values)
    return False

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
