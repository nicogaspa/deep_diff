from copy import deepcopy
from datetime import date, datetime
from typing import List, Callable, Optional

validKinds = ['N', 'E', 'A', 'D']


class Diff:
    def __init__(self, kind, path):
        self.kind = kind
        self.path = path

    def __str__(self):
        return f"{self.kind} - {self.path}"

    def __repr__(self):
        return f"{self.kind} - {self.path}"


class DiffEdit(Diff):
    """ Edited value """

    def __init__(self, path, origin, value):
        super().__init__("E", path)
        self.lhs = origin
        self.rhs = value


class DiffNew(Diff):
    """ New value """

    def __init__(self, path, value):
        super().__init__("N", path)
        self.rhs = value


class DiffDeleted(Diff):
    """ Deleted value """

    def __init__(self, path, value):
        super().__init__("D", path)
        self.lhs = value


class DiffArray(Diff):
    """ Array differences """

    def __init__(self, path, index, item):
        super().__init__("A", path)
        self.index = index
        self.item = item


def hash_this_string(string):
    hashed = 0
    if len(string) == 0:
        return hashed
    for char in string:
        hashed = ((hashed << 5) - hashed) + ord(char)
        hashed = hashed & hashed  # Convert to 32bit integer
    return hashed


def get_order_independent_hash(obj):
    """
    Gets a hash of the given object in an array order-independent fashion
    also object key order independent (easier since they can be alphabetized)
    """
    accum = 0
    if isinstance(obj, list):
        for item in obj:  # Addition is commutative
            accum += get_order_independent_hash(item)
        array_string = f'[type: array, hash: {accum}]'
        return accum + hash_this_string(array_string)
    if isinstance(obj, dict):
        for key in obj:
            key_value_string = f'[ type: object, key: {key}, value hash: {get_order_independent_hash(obj[key])} ]'
            accum += hash_this_string(key_value_string)
        return accum
    string_to_hash = f'[ type: {type(obj)}  value: {obj} ]'
    return accum + hash_this_string(string_to_hash)


def deep_diff(lhs, rhs, changes: Optional[List[Diff]] = None, prefilter: Callable = None,
              path: List[str] = None, key: str = None, stack: List[dict] = None,
              order_independent: bool = False) -> List[Diff]:
    """

    :param lhs: Left value
    :param rhs: Right value
    :param changes: changes array to be passed in recursive way
    :param prefilter: function to filter, or ignore, some keys
    :param path: current path of recursion
    :param key:
    :param stack:
    :param order_independent: if True, lists will be sorted by type and value,
                              thus not considering differences for elements in the wrong place
    :return: array of differences found
    """
    changes = changes if changes is not None else []
    path = path if path is not None else []
    stack = stack if stack is not None else []
    current_path = deepcopy(path)
    if key is not None:
        if prefilter is not None:
            if isinstance(prefilter, Callable) and prefilter(current_path, key):
                # ignoring
                return
        current_path.append(key)
    ltype = type(lhs)
    rtype = type(rhs)
    ldefined = lhs is not None or (len(stack) > 0 and stack[len(stack) - 1]["lhs"] is not None and key in stack[len(stack) - 1]["lhs"])
    rdefined = rhs is not None or (len(stack) > 0 and stack[len(stack) - 1]["rhs"] is not None and key in stack[len(stack) - 1]["rhs"])

    if not ldefined and rdefined:
        changes.append(DiffNew(current_path, rhs))
    elif not rdefined and ldefined:
        changes.append(DiffDeleted(current_path, lhs))
    elif ltype != rtype:
        changes.append(DiffEdit(current_path, lhs, rhs))
    elif (ltype == date or ltype == datetime) and (lhs - rhs).microseconds != 0:
        changes.append(DiffEdit(current_path, lhs, rhs))
    elif (isinstance(lhs, dict) or isinstance(lhs, list)) and lhs is not None and rhs is not None:
        other = False
        for i in reversed(range(len(stack) - 1, -1)):  # ??
            if stack[i]["lhs"] == lhs:
                other = True
                break
        if other:
            # lhs is contains a cycle at this element and it differs from rhs
            changes.append(DiffEdit(current_path, lhs, rhs))
        else:
            stack.append({"lhs": lhs, "rhs": rhs})
            if isinstance(lhs, list):
                # If order doesn't matter, we need to sort our arrays
                if order_independent:
                    lhs.sort(key=lambda x: get_order_independent_hash(x))
                    rhs.sort(key=lambda x: get_order_independent_hash(x))
                i = len(rhs) - 1
                j = len(lhs) - 1
                while i > j:
                    changes.append(DiffArray(current_path, i, DiffNew(None, rhs[i])))
                    i -= 1
                while j > i:
                    changes.append(DiffArray(current_path, j, DiffDeleted(None, lhs[j])))
                    j -= 1
                while i >= 0:
                    deep_diff(lhs[i], rhs[i], changes, prefilter, current_path, i, stack, order_independent)
                    i -= 1
            else:  # dict
                lkeys = list(lhs.keys())
                rkeys = list(rhs.keys())
                for k in lkeys:  # Finding index of key in rhs
                    try:
                        r_index = rkeys.index(k)
                    except ValueError:
                        r_index = -1
                    if r_index >= 0:
                        deep_diff(lhs[k], rhs[k], changes, prefilter, current_path, k, stack, order_independent)
                        rkeys[r_index] = None  # Setting None to ignore in next iteration
                    else:
                        deep_diff(lhs[k], None, changes, prefilter, current_path, k, stack, order_independent)
                for k in rkeys:
                    if k is not None:
                        deep_diff(None, rhs[k], changes, prefilter, current_path, k, stack, order_independent)
            stack.pop()  # stack.length = stack.length - 1
    elif lhs != rhs:
        changes.append(DiffEdit(current_path, lhs, rhs))

    return changes
