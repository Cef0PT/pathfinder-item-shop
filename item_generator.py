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

faint_items = []
moderate_items = []
strong_items = []


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


def filter_for_allowed_sources(item_list: list, sources):
    positive_list = []
    for item in item_list:
        if item["Source"] in sources:
            positive_list.append(item)
    print(len(positive_list) + len(item_list))
    return positive_list


def sort_by_aura_strength(item_list: list):
    sort_index = 0
    for item in item_list:
        if item["AuraStrength"] == "faint":
            faint_items.append(item)
        elif item["AuraStrength"] == "moderate":
            moderate_items.append(item)
        elif item["AuraStrength"] == "strong":
            strong_items.append(item)
        else:
            sort_index += 1
    print(f"There were {sort_index} items without feasible aura strength.")


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
        print(f"Rolling {n}d{m}: " + line)
    else:
        print(f"Rolling for {n}d{m} {aura_strength} items: " + line)
    return die_sum


def get_item_by_aura_strength(aura_strength: str):
    if aura_strength == "faint":
        item_list = faint_items
    elif aura_strength == "moderate":
        item_list = moderate_items
    elif aura_strength == "strong":
        item_list = strong_items
    else:
        print("Please provide a valid aura strength.")
        return
    item = item_list[random.randint(1, len(item_list))]
    if item["Price"] == "":
        return get_item_by_aura_strength(aura_strength)
    return item


# main
def run(magic_item_list: list, execute_for_town_size: str, list_of_allowed_sources: list):
    print("Number of all magic items: " + str(len(magic_item_list)))
    cleaned_magic_item_list = filter_for_allowed_sources(magic_item_list, list_of_allowed_sources)
    print("Number of magic items that are allowed: " + str(len(cleaned_magic_item_list)))
    sort_by_aura_strength(cleaned_magic_item_list)
    print()

    item_dic = {'Item': [], 'Slot': [], 'Price': [], 'Source': [], 'Description': []}
    # get faint items
    if execute_for_town_size != "Metropole":
        n, m = obtainable_magic_items_per_town_size[execute_for_town_size]["faint"]
        number_of_faint_items = roll_n_die_m(n, m, "faint")
        for index in range(number_of_faint_items):
            this_item = get_item_by_aura_strength("faint")
            item_dic['Item'].append(this_item['Name'])
            item_dic['Slot'].append(this_item['Slot'])
            item_dic['Price'].append(this_item['Price'])
            item_dic['Source'].append(this_item['Source'])
            item_dic['Description'].append(this_item['Description'])
    else:
        print("All faint magic items are available.")

    # get moderate items
    if execute_for_town_size not in ["Weiler", "Nest"]:
        n, m = obtainable_magic_items_per_town_size[execute_for_town_size]["moderate"]
        number_of_moderate_items = roll_n_die_m(n, m, "moderate")
        for index in range(number_of_moderate_items):
            this_item = get_item_by_aura_strength("moderate")
            item_dic['Item'].append(this_item['Name'])
            item_dic['Slot'].append(this_item['Slot'])
            item_dic['Price'].append(this_item['Price'])
            item_dic['Source'].append(this_item['Source'])
            item_dic['Description'].append(this_item['Description'])
    else:
        print("No moderate magic items are available.")

    # get strong items
    if execute_for_town_size not in ["Weiler", "Nest", "Ansiedlung", "Kleines Dorf"]:
        n, m = obtainable_magic_items_per_town_size[execute_for_town_size]["strong"]
        number_of_strong_items = roll_n_die_m(n, m, "strong")
        for index in range(number_of_strong_items):
            this_item = get_item_by_aura_strength("strong")
            item_dic['Item'].append(this_item['Name'])
            item_dic['Slot'].append(this_item['Slot'])
            item_dic['Price'].append(this_item['Price'])
            item_dic['Source'].append(this_item['Source'])
            item_dic['Description'].append(this_item['Description'])
    else:
        print("No strong magic items are available.")
    # roll_n_die_m(4, 5, "faint")
    obtainable = obtainable_magic_items_per_town_size[execute_for_town_size]["Obtainable"]
    print(f"Any magic items that cost at most {obtainable} are by a 75% chance available.")

    return item_dic
