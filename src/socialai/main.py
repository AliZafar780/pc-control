"""
SocialAI CLI Entry Point

The main entry point for the SocialAI command-line interface.
"""

import sys
import asyncio
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from socialai.cli import create_app
from socialai.config import Config
from socialai.version import __version__

# Create Typer app
app = create_app()
console = Console()

# Global configuration
config: Optional[Config] = None

def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"SocialAI version: {__version__}")
        raise typer.Exit()

@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config file"),
    version: Optional[bool] = typer.Option(None, "--version", callback=version_callback, help="Show version"),
) -> None:
    """
    SocialAI - Distraction-free AI-powered social media CLI.
    
    A modern CLI tool for consuming social media content with AI-powered
    summarization, content filtering, and focus modes.
    
    Examples:
    
        # View your feed from Twitter
        socialai feed twitter --limit 20
        
        # Summarize a thread
        socialai summarize https://twitter.com/user/status/123456789
        
        # Search across platforms
        socialai search "AI news" --platforms twitter reddit
        
        # Start a focused session
        socialai session start --platforms twitter reddit --duration 30
    """
    global config
    
    # Initialize configuration
    if verbose:
        console.print("[cyan]SocialAI[/cyan] - Initializing with verbose mode")
    
    try:
        config = Config.load(config_path)
        if verbose:
            console.print(f"[green]Configuration loaded from: {config.config_path}[/green]")
    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)

def cli() -> int:
    """Main CLI entry point."""
    try:
        # Show welcome message on first run
        if not sys.argv[1:]:  # No arguments provided
            welcome_text = Text()
            welcome_text.append("Welcome to ", style="cyan")
            welcome_text.append("SocialAI", style="bold cyan")
            welcome_text.append(" - Distraction-free social media CLI\n\n", style="cyan")
            welcome_text.append("Get started with:\n", style="yellow")
            welcome_text.append("  socialai --help           ", style="white")
            welcome_text.append("# Show all commands\n", style="dim")
            welcome_text.append("  socialai config --help    ", style="white")
            welcome_text.append("# Configure the application\n", style="dim")
            welcome_text.append("  socialai feed --help      ", style="white")
            welcome_text.append("# View your feeds\n", style="dim")
            
            panel = Panel(
                welcome_text,
                title="🚀 SocialAI",
                subtitle="Built for focused productivity",
                border_style="cyan"
            )
            console.print(panel)
            console.print("\n[dim]Run [cyan]socialai --help[/cyan] for complete command reference.[/dim]")
            return 0
        
        # Run the application
        app()
        return 0
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        return 1
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if "--verbose" in sys.argv or "-v" in sys.argv:
            console.print_exception()
        return 1

if __name__ == "__main__":
    sys.exit(cli())
