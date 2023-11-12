def flatten(arr):
   if isinstance(arr, list):
       return sum(map(flatten, arr), [])
   else:
       return [arr]
   
def flatten_unique_list(array):
    flattened_array = flatten(array)
    filtered_array = list(filter(lambda x: x is not None, flattened_array))
    unique_array = list(set(filtered_array))
    return unique_array