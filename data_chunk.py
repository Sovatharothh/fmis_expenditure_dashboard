# =========================
# Data
# =========================
base_class_data = {
    "Class A": {
        "color_class": "class-a",
        "share": "6%",
        "2025": {
            "Financial Law": 3000000,
            "Budget Movement": 450000,
            "Modified Law": 600000,
            "Implementation": 2400000,
            "Available Budget": 750000,
        },
        "2026": {
            "Financial Law": 3300000,
            "Budget Movement": 472500,
            "Modified Law": 648000,
            "Implementation": 2690000,
            "Available Budget": 817500,
        },
    },
    "Class B": {
        "color_class": "class-b",
        "share": "7%",
        "2025": {
            "Financial Law": 3500000,
            "Budget Movement": 625000,
            "Modified Law": 700000,
            "Implementation": 2800000,
            "Available Budget": 875000,
        },
        "2026": {
            "Financial Law": 3850000,
            "Budget Movement": 651250,
            "Modified Law": 756000,
            "Implementation": 3140000,
            "Available Budget": 953750,
        },
    },
    "Class C": {
        "color_class": "class-c",
        "share": "2%",
        "2025": {
            "Financial Law": 1000000,
            "Budget Movement": 150000,
            "Modified Law": 200000,
            "Implementation": 800000,
            "Available Budget": 250000,
        },
        "2026": {
            "Financial Law": 1100000,
            "Budget Movement": 157500,
            "Modified Law": 216000,
            "Implementation": 896000,
            "Available Budget": 272500,
        },
    },
}

levels = ["National Level", "Sub-National Level", "APE Level"]
metrics_order = [
    "Financial Law",
    "Budget Movement",
    "Modified Law",
    "Implementation",
    "Available Budget",
]
metric_colors = {
    "Financial Law": "#22b8ff",
    "Budget Movement": "#24d2ff",
    "Modified Law": "#20d6a2",
    "Implementation": "#ffae14",
    "Available Budget": "#ff5656",
}


def duplicate_across_levels(class_data):
    return {level: deepcopy(class_data) for level in levels}


all_data = {klass: duplicate_across_levels(data) for klass, data in base_class_data.items()}


def build_total_class(all_classes):
    total = {
        "color_class": "class-total",
        "share": "15%",
        "2025": {m: 0 for m in metrics_order},
        "2026": {m: 0 for m in metrics_order},
    }

    for _, level_map in all_classes.items():
        national = level_map["National Level"]
        for year in ["2025", "2026"]:
            for metric in metrics_order:
                total[year][metric] += national[year][metric]

    return duplicate_across_levels(total)


def build_overall_summary(all_classes):
    summary = {m: 0 for m in metrics_order}
    for _, level_map in all_classes.items():
        national = level_map["National Level"]
        for year in ["2025", "2026"]:
            for metric in metrics_order:
                summary[metric] += national[year][metric]
    return summary


