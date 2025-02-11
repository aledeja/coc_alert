# Threshold settings
NUPL_THRESHOLDS = {
    'low': (0, 0.25),
    'neutral': (0.25, 0.75),
    'high': (0.75, 1.0)
}

MVRV_LTH_THRESHOLDS = {
    'low': (0, 2),
    'neutral': (2, 7),
    'high': (7, 10)
}

MVRV_STH_THRESHOLDS = {
    'low': (0, 0.8),
    'neutral': (0.8, 1.5),
    'high': (1.5, 3)
}

SOPR_STH_THRESHOLDS = {
    'low': (0, 0.95),
    'neutral': (0.95, 1.1),
    'high': (1.1, 2)
}

# Message templates
NUPL_MESSAGES = {
    'low': "Market is in capitulation, showing significant unrealized losses.",
    'neutral': "Market shows balanced profit/loss ratio.",
    'high': "Market participants sitting on large unrealized profits, potential profit-taking ahead."
}

MVRV_LTH_MESSAGES = {
    'low': "Long-term holders are at a loss, historically a good accumulation zone.",
    'neutral': "Long-term holder positions show healthy valuation.",
    'high': "Long-term holders in significant profit, potential distribution zone."
}

MVRV_STH_MESSAGES = {
    'low': "Short-term holders underwater, suggesting local bottom formation.",
    'neutral': "Short-term holder positions at reasonable valuations.",
    'high': "Short-term holders in heavy profit, increased sell pressure likely."
}

SOPR_STH_MESSAGES = {
    'low': "Short-term holders selling at a loss, potential capitulation.",
    'neutral': "Normal profit-taking behavior from short-term holders.",
    'high': "Short-term holders taking significant profits, potential local top."
}

def get_status(value, thresholds):
    for status, (min_val, max_val) in thresholds.items():
        if min_val <= value < max_val:
            return status
    return 'high' if value >= max_val else 'low'  # Handle values outside ranges 