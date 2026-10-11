def format_euro(value):
    text = f"{float(value):,.2f}".replace(",", " ").replace(".", ",")
    return f"{text} €"


def format_percent(value):
    return f"{value:.1f} %".replace(".", ",")
