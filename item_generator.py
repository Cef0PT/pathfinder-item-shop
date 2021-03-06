# imports
import random

# possible sizes: Weiler, Nest, Ansiedlung, Kleines Dorf, Großes Dorf, Kleinstadt, Großstadt, Metropole
town_sizes = ['Weiler', 'Nest', 'Ansiedlung', 'Kleines Dorf', 'Großes Dorf', 'Kleinstadt', 'Großstadt', 'Metropole']

obtainable_magic_items_per_town_size = {
    "Weiler": {"Obtainable": "50", "faint": [1, 4], "moderate": [0, 0], "strong": [0, 0]},
    "Nest": {"Obtainable": "200", "faint": [1, 6], "moderate": [0, 0], "strong": [0, 0]},
    "Ansiedlung": {"Obtainable": "500", "faint": [2, 4], "moderate": [1, 4], "strong": [0, 0]},
    "Kleines Dorf": {"Obtainable": "1000", "faint": [3, 4], "moderate": [1, 6], "strong": [0, 0]},
    "Großes Dorf": {"Obtainable": "2000", "faint": [3, 4], "moderate": [2, 4], "strong": [1, 4]},
    "Kleinstadt": {"Obtainable": "4000", "faint": [4, 4], "moderate": [3, 4], "strong": [1, 6]},
    "Großstadt": {"Obtainable": "8000", "faint": [4, 4], "moderate": [3, 4], "strong": [2, 6]},
    "Metropole": {"Obtainable": "16000", "faint": [0, 0], "moderate": [4, 4], "strong": [3, 4]}
}

# factor the price of an individual item may be greater than the items that are generically available
price_factor = 100


# functions
def pretty_print(item: dict):
    print(item["Name"])
    print("Slot: " + item["Slot"] + "; Price: " + item["Price"] + "; Source:" + item["Source"])
    print(item["Description"] + "\n")


def get_sources(item_list: list):
    sources_list = []
    for item in item_list:
        if item["Source"] not in sources_list:
            sources_list.append(item["Source"])
    return sources_list


def filter_allowed_items(item_list: list, sources: list, max_price: int):
    positive_list = []
    for item in item_list:
        if item["Source"] in sources and not item['Price'] == '':
            # Fix items with float as price
            if isinstance(item['Price'], float):
                item['Price'] = str(int(item['Price'])) + ' gp'

            # Filter for max price
            numeric_filter = filter(str.isdigit, item['Price'])
            if int(''.join(numeric_filter)) <= max_price:
                positive_list.append(item)
    return positive_list


def sort_by_aura_strength(item_list: list):
    sort_index = 0
    faint, moderate, strong = [], [], []
    for item in item_list:
        if item["AuraStrength"] == "faint":
            faint.append(item)
        elif item["AuraStrength"] == "moderate":
            moderate.append(item)
        elif item["AuraStrength"] == "strong":
            strong.append(item)
        else:
            sort_index += 1
    print_str = f"There were {sort_index} items without feasible aura strength."
    return faint, moderate, strong, print_str


def roll_n_die_m(n: int, m: int, aura_strength=""):
    sides = []
    for die in range(1, n + 1):
        sides.append(random.randint(1, m))
    line = "("
    for side in sides:
        line += str(side) + " + "
    line = line[:len(line) - 3] + ")"
    die_sum = sum(sides)
    line = str(die_sum) + " " + line
    if aura_strength == "":
        print_str = f"Rolling {n}d{m}: " + line
    else:
        print_str = f"Rolling for {n}d{m} {aura_strength} items: " + line
    return die_sum, print_str


def get_item_by_aura_strength(aura_list: list, aura_strength: str):
    if len(aura_list) > 0:
        item = aura_list[random.randint(0, len(aura_list)-1)]
        while item["Price"] == "":
            item = aura_list[random.randint(0, len(aura_list)-1)]
        return item

    else:
        print_str = f"ERROR : No {aura_strength} items available in selected rule sets!"
        return print_str


# main
def run(magic_item_list: list, execute_for_town_size: str, list_of_allowed_sources: list):
    if not list_of_allowed_sources:
        print_strings = ['ERROR: Please select at least one rule set.']
        return None, print_strings

    max_price = int(obtainable_magic_items_per_town_size[execute_for_town_size]["Obtainable"]) * price_factor
    print_strings = ["Number of all magic items: " + str(len(magic_item_list))]
    cleaned_magic_item_list = filter_allowed_items(magic_item_list, list_of_allowed_sources, max_price)
    print_strings.append("Number of magic items that are allowed: " + str(len(cleaned_magic_item_list)))
    faint_items, moderate_items, strong_items, print_str = sort_by_aura_strength(cleaned_magic_item_list)
    print_strings.append(print_str)

    rolled_items = []

    def append_item(it):
        it['Quantity'] = 1  # Init Quantity column
        is_duplicate = False
        for item in rolled_items:
            if item['Name'] == it['Name']:  # Check for duplicates
                item['Quantity'] += 1
                is_duplicate = True
                break

        if not is_duplicate:
            # You cannot pass anything by value in Python, so 'it['Quantity'] = 1' would reset the Quantity in
            # rolled_items to 1. Therefore, we append a copy of it, instead of it itself
            rolled_items.append(dict(it))

    # get faint items
    if execute_for_town_size != "Metropole":
        n, m = obtainable_magic_items_per_town_size[execute_for_town_size]["faint"]
        number_of_faint_items, print_str = roll_n_die_m(n, m, "faint")
        print_strings.append(print_str)
        for index in range(number_of_faint_items):
            current_item = get_item_by_aura_strength(faint_items, "faint")
            if isinstance(current_item, str):
                print_strings.append(current_item)
                break
            else:
                append_item(current_item)
    else:
        print_strings.append("All faint magic items are available.")

    # get moderate items
    if execute_for_town_size not in ["Weiler", "Nest"]:
        n, m = obtainable_magic_items_per_town_size[execute_for_town_size]["moderate"]
        number_of_moderate_items, print_str = roll_n_die_m(n, m, "moderate")
        print_strings.append(print_str)
        for index in range(number_of_moderate_items):
            current_item = get_item_by_aura_strength(moderate_items, "moderate")
            if isinstance(current_item, str):
                print_strings.append(current_item)
                break
            else:
                append_item(current_item)
    else:
        print_strings.append("No moderate magic items are available.")

    # get strong items
    if execute_for_town_size not in ["Weiler", "Nest", "Ansiedlung", "Kleines Dorf"]:
        n, m = obtainable_magic_items_per_town_size[execute_for_town_size]["strong"]
        number_of_strong_items, print_str = roll_n_die_m(n, m, "strong")
        print_strings.append(print_str)
        for index in range(number_of_strong_items):
            current_item = get_item_by_aura_strength(strong_items, "strong")
            if isinstance(current_item, str):
                print_strings.append(current_item)
                break
            else:
                append_item(current_item)
    else:
        print_strings.append("No strong magic items are available.")
    # roll_n_die_m(4, 5, "faint")
    obtainable = obtainable_magic_items_per_town_size[execute_for_town_size]["Obtainable"]
    print_strings.append(f"Any magic items that cost at most {obtainable} are by a 75% chance available.")

    # List of dicts to dict of lists
    if rolled_items:
        rolled_items_dic = {k: [dic[k] for dic in rolled_items] for k in rolled_items[0]}
    else:
        rolled_items_dic = None

    return rolled_items_dic, print_strings
