from random import randint, sample


EXTRACTABLE_BODY_TYPES = {"Asteroid", "Comet"}

EXTRACTABLE_RESOURCE_DEFS = (
    {"id": "iron", "name": "Iron", "style": "bold white"},
    {"id": "gold", "name": "Gold", "style": "bold yellow"},
    {"id": "silver", "name": "Silver", "style": "bright_white"},
    {"id": "diamond", "name": "Diamond", "style": "bold cyan"},
    {"id": "nickel", "name": "Nickel", "style": "grey70"},
)

RESOURCE_TOTAL_MIN_UNITS = 10
RESOURCE_TOTAL_MAX_UNITS = 200
RESOURCE_TYPE_COUNT_MIN = 1
RESOURCE_TYPE_COUNT_MAX = 4

EXTRACTION_BATCH_MIN_UNITS = 4
EXTRACTION_BATCH_MAX_UNITS = 16

# Descriptor thresholds are based on each resource's share of the total detected pool.
RESOURCE_SCAN_DESCRIPTORS = (
    {"id": "rich", "label": "Rich", "min_share": 0.45, "style": "bold green"},
    {"id": "medium", "label": "Medium", "min_share": 0.18, "style": "bold yellow"},
    {"id": "low", "label": "Low", "min_share": 0.08, "style": "bright_white"},
    {"id": "traces", "label": "Traces", "min_share": 0.0, "style": "grey70"},
)


RESOURCE_DEF_BY_ID = {entry["id"]: entry for entry in EXTRACTABLE_RESOURCE_DEFS}


def generate_resource_pool() -> dict[str, int]:
    total_units = randint(RESOURCE_TOTAL_MIN_UNITS, RESOURCE_TOTAL_MAX_UNITS)
    max_type_count = min(RESOURCE_TYPE_COUNT_MAX, len(EXTRACTABLE_RESOURCE_DEFS), total_units)
    min_type_count = min(RESOURCE_TYPE_COUNT_MIN, max_type_count)
    if max_type_count <= 0:
        return {}
    resource_type_count = randint(min_type_count, max_type_count)
    selected = sample(EXTRACTABLE_RESOURCE_DEFS, resource_type_count)

    pool = {}
    remaining = total_units
    for index, resource in enumerate(selected):
        resource_id = resource["id"]
        types_left_after_this = resource_type_count - index - 1
        min_reserve = types_left_after_this
        if index == resource_type_count - 1:
            allocation = remaining
        else:
            max_for_this = remaining - min_reserve
            allocation = randint(1, max_for_this)
        pool[resource_id] = allocation
        remaining -= allocation
    return pool


def classify_resource_descriptor(quantity: int, total_units: int) -> dict:
    if total_units <= 0 or quantity <= 0:
        return RESOURCE_SCAN_DESCRIPTORS[-1]
    share = quantity / total_units
    for descriptor in RESOURCE_SCAN_DESCRIPTORS:
        if share >= descriptor["min_share"]:
            return descriptor
    return RESOURCE_SCAN_DESCRIPTORS[-1]
