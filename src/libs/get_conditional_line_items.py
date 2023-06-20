def conditional_line_items(rate, local_rate):
    new_line_items = []
    for item in local_rate['data']['line_items']:
        if item.get('conditions'):
            operator = item['conditions'].get('operator')
            values = item['conditions'].get('values')
            condition_met = evaluate_conditions(rate, operator, values)
            if condition_met:
                new_line_items.append(item)
        else:
            new_line_items.append(item)
    local_rate['data']['line_items'] = new_line_items
    local_rate['line_items'] = new_line_items
    return local_rate

def evaluate_conditions(rate, operator, values):
    if operator == "or":
        return any(check_condition(rate, val) for val in values)
    elif operator == "and":
        return all(check_condition(rate, val) for val in values)
    else:
        return False

def check_condition(rate, condition):
    key = condition[0]
    operator = condition[1].lower()
    operand = condition[2]
    if isinstance(operand, list):
        if operator =="in":
            return rate.get(key) in operand
        elif operator =="not_in":
            return rate.get(key) not in operand
    else:
        if operator == "equal_to" and rate.get(key) == operand:
            return True
        elif operator == "not_equal_to" and rate.get(key) != operand:
            return True
        elif operator == "greater_than" and rate.get(key) > operand:
            return True
        elif operator == "less_than" and rate.get(key) < operand:
            return True
    return False
