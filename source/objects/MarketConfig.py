from .ExtractionConfig import EXTRACTABLE_RESOURCE_DEFS


# Core economy commodity tuning.
BASE_MARKET_COMMODITY_DEFS = (
    {"id": "food", "name": "Food Rations", "base_price": 45, "stock_min": 16, "stock_max": 80, "volatility_min": -22, "volatility_max": 28},
    {"id": "ore", "name": "Raw Ore", "base_price": 75, "stock_min": 14, "stock_max": 70, "volatility_min": -26, "volatility_max": 34},
    {"id": "fuel", "name": "Refined Fuel", "base_price": 120, "stock_min": 10, "stock_max": 56, "volatility_min": -30, "volatility_max": 38},
    {"id": "parts", "name": "Ship Parts", "base_price": 190, "stock_min": 8, "stock_max": 42, "volatility_min": -35, "volatility_max": 45},
    {"id": "med", "name": "Medical Supplies", "base_price": 260, "stock_min": 7, "stock_max": 34, "volatility_min": -42, "volatility_max": 56},
)

# Mining commodity tuning by resource id.
# Edit these values to rebalance the mineral economy.
MINED_RESOURCE_MARKET_PROFILES = {
    "iron": {"base_price": 90, "stock_min": 9, "stock_max": 50, "volatility_min": -24, "volatility_max": 30},
    "nickel": {"base_price": 105, "stock_min": 7, "stock_max": 40, "volatility_min": -28, "volatility_max": 36},
    "silver": {"base_price": 130, "stock_min": 5, "stock_max": 30, "volatility_min": -36, "volatility_max": 48},
    "gold": {"base_price": 240, "stock_min": 3, "stock_max": 18, "volatility_min": -50, "volatility_max": 75},
    "diamond": {"base_price": 420, "stock_min": 1, "stock_max": 10, "volatility_min": -95, "volatility_max": 135},
}

MINED_RESOURCE_MARKET_DEFAULTS = {
    "base_price": 100,
    "stock_min": 3,
    "stock_max": 24,
    "volatility_min": -40,
    "volatility_max": 55,
}


def _build_mined_resource_commodity_defs() -> tuple:
    market_defs = []
    for resource in EXTRACTABLE_RESOURCE_DEFS:
        resource_id = resource["id"]
        profile = MINED_RESOURCE_MARKET_PROFILES.get(resource_id, {})
        market_defs.append(
            {
                "id": resource_id,
                "name": resource["name"],
                "base_price": int(profile.get("base_price", MINED_RESOURCE_MARKET_DEFAULTS["base_price"])),
                "stock_min": int(profile.get("stock_min", MINED_RESOURCE_MARKET_DEFAULTS["stock_min"])),
                "stock_max": int(profile.get("stock_max", MINED_RESOURCE_MARKET_DEFAULTS["stock_max"])),
                "volatility_min": int(profile.get("volatility_min", MINED_RESOURCE_MARKET_DEFAULTS["volatility_min"])),
                "volatility_max": int(profile.get("volatility_max", MINED_RESOURCE_MARKET_DEFAULTS["volatility_max"])),
            }
        )
    return tuple(market_defs)


MARKET_COMMODITY_DEFS = BASE_MARKET_COMMODITY_DEFS + _build_mined_resource_commodity_defs()

MARKET_COMMODITY_NAME_BY_ID = {
    commodity["id"]: commodity["name"]
    for commodity in MARKET_COMMODITY_DEFS
}
