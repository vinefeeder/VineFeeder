from rich.console import Console
from rich.panel import Panel
#from devine.core.console import console

def pretty_print():
    console = Console()

    # Combined text block for proper alignment
    text_block = (
        r"[pink1] _   ___          ____           __"       "\n"
        r"| | / (_)__  ___ / __/__ ___ ___/ /__ ____" "\n"
        r"| |/ / / _ \/ -_) _// -_) -_) _  / -_) __/" "\n"
        r"|___/_/_//_/\__/_/  \__/\__/\_,_/\__/_/     " "\n\n\n[/]"

        """
        [bright_green]A front-end for Devine[/]
        Copyright © 2024  A_n_g_e_l_a   
        [blue]https://github.com/vinefeeder[/]"""
    )
    """         
    
        
        [#89B4FA]Search will take keyword(s),
        or a URL for direct download, 
        or leave Search empty and select
        a service to show an action menu.
        In menus with [pink1]🢧[/]: [green]🔺🔻 to scroll[/]
        'a' selects all: space-bar selects one
        In menus with[cyan] >[/] use scroll as above 
        Return to select.[/]
        """

    

    # Create a panel with padding and border
    panel = Panel(
        text_block,
        title="VineFeeder",
        border_style="#89B4FA",
        padding=(1 ,21, 2, 20)  # Adjust padding as needed
    )

    console.print(panel)




