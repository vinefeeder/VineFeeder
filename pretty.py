from rich.console import Console
from rich.panel import Panel





# Define the Catppuccin Mocha color scheme
catppuccin_mocha = {
    "bg": "rgb(30,30,46)",
    "text": "rgb(205,214,244)",
    "text2": "rgb(162,169,193)",
    "black": "rgb(69,71,90)",
    "bright_black": "rgb(88,91,112)",
    "red": "rgb(243,139,168)",
    "green": "rgb(166,227,161)",
    "yellow": "rgb(249,226,175)",
    "blue": "rgb(137,180,250)",
    "pink": "rgb(245,194,231)",
    "cyan": "rgb(148,226,213)",
    "gray": "rgb(166,173,200)",
    "bright_gray": "rgb(186,194,222)",
    "dark_gray": "rgb(54,54,84)"
}

def pretty_print():
    console = Console()

    # Combined text block with the color scheme
    text_block = (
        f"[{catppuccin_mocha['pink']}] _   ___          ____           __" "\n"
        f"| | / (_)__  ___ / __/__ ___ ___/ /__ ____" "\n"
        f"| |/ / / _ \\/ -_) _// -_) -_) _  / -_) __/" "\n"
        f"|___/_/_//_/\\__/__/  \\__/\\__/\\_,_/\\__/_/     [/]" "\n\n\n"
        f"[{catppuccin_mocha['green']}]A front-end for Devine[/]\n"
        f"[{catppuccin_mocha['text2']}]Copyright © 2024  A_n_g_e_l_a[/]\n"
        f"[{catppuccin_mocha['blue']}]https://github.com/vinefeeder[/]"
    )

    # 
    instructions = (
        f"[{catppuccin_mocha['gray']}]Search will take keyword(s), " "\n"
        "or a URL for direct download, " "\n"
        "or leave Search empty and select \na service to show an action menu." "\n"
        
    )

    # Display the panel
    panel = Panel(
        text_block + "\n\n" + instructions,
        title="VineFeeder",
        border_style=catppuccin_mocha["blue"],
        padding=(1, 17, 2, 16),
        style=f"on {catppuccin_mocha['bg']}",
        expand=False
    )

    console.print(panel)


