"""
SocialAI CLI Commands

All CLI commands and their implementations.
"""

import asyncio
from typing import Optional, List
from datetime import datetime

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax

from socialai.config import Config
from socialai.ai import AIService
from socialai.adapters.registry import AdapterRegistry
from socialai.core.session import SessionManager
from socialai.core.storage import Storage
from socialai.filters import ContentFilter
from socialai.utils.formatters import format_post, format_summary
from socialai.utils.validators import validate_url, validate_platform

app = typer.Typer(
    name="socialai",
    help="Distraction-free AI-powered social media CLI",
    rich_markup_mode="rich"
)
console = Console()

def create_app() -> typer.Typer:
    """Create and configure the CLI application."""
    
    # Feed command group
    @app.command("feed")
    def feed_command(
        platform: str = typer.Argument(..., help="Platform name (twitter, reddit, linkedin)"),
        limit: int = typer.Option(20, "--limit", "-l", help="Number of posts to fetch"),
        filter_type: Optional[str] = typer.Option(None, "--filter", help="Content filter to apply"),
        focus: bool = typer.Option(False, "--focus", help="Enable distraction-free mode"),
        save: bool = typer.Option(False, "--save", help="Save results to history"),
    ) -> None:
        """
        View your feed from a specific platform.
        
        Examples:
        
            socialai feed twitter --limit 10
            socialai feed reddit --filter positive --focus
            socialai feed linkedin --save
        """
        if not validate_platform(platform):
            console.print(f"[red]Error: Unknown platform '{platform}'[/red]")
            console.print("Supported platforms: twitter, reddit, linkedin, hackernews")
            raise typer.Exit(1)
        
        async def _fetch_feed():
            config = Config.load()
            registry = AdapterRegistry(config)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(f"Fetching {platform} feed...", total=None)
                
                try:
                    # Get adapter for platform
                    adapter = registry.get_adapter(platform)
                    
                    # Fetch feed
                    feed = await adapter.fetch_feed(limit=limit)
                    
                    if not feed:
                        console.print("[yellow]No posts found[/yellow]")
                        return
                    
                    # Apply filters if specified
                    if filter_type:
                        content_filter = ContentFilter(config)
                        feed = await content_filter.apply(feed, filter_type)
                    
                    progress.update(task, description="Formatting results...")
                    
                    # Display feed
                    for i, post in enumerate(feed, 1):
                        if focus:
                            # Distraction-free view
                            panel = Panel(
                                format_post(post, minimal=True),
                                title=f"[bold cyan]{post.title or post.content[:50]}...[/bold cyan]",
                                subtitle=f"Platform: {platform.title()} • Score: {post.engagement_score or 0}",
                                border_style="blue"
                            )
                        else:
                            # Standard view
                            panel = Panel(
                                format_post(post),
                                title=f"[bold blue]{post.title or post.content[:50]}...[/bold blue]",
                                subtitle=f"By: {post.author} • Platform: {platform.title()}",
                                border_style="cyan"
                            )
                        
                        console.print(f"[dim]Post {i}/{len(feed)}[/dim]")
                        console.print(panel)
                        console.print()
                    
                    # Save to history if requested
                    if save:
                        storage = Storage(config)
                        await storage.save_feed(platform, feed)
                        console.print(f"[green]✓ Saved {len(feed)} posts to history[/green]")
                        
                except Exception as e:
                    console.print(f"[red]Error fetching feed: {e}[/red]")
                    raise typer.Exit(1)
        
        asyncio.run(_fetch_feed())
    
    # Summarize command
    @app.command("summarize")
    def summarize_command(
        url: str = typer.Argument(..., help="URL to summarize"),
        style: str = typer.Option("brief", "--style", help="Summary style: brief, detailed, bullet"),
        ai_provider: Optional[str] = typer.Option(None, "--ai", help="AI provider to use"),
        output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Save summary to file"),
    ) -> None:
        """
        Summarize content using AI.
        
        Examples:
        
            socialai summarize https://twitter.com/user/status/123456789
            socialai summarize https://reddit.com/r/python/comments/abc123 --style detailed
            socialai summarize https://example.com --output summary.md
        """
        if not validate_url(url):
            console.print("[red]Error: Invalid URL format[/red]")
            raise typer.Exit(1)
        
        async def _summarize():
            config = Config.load()
            ai_service = AIService(config, provider=ai_provider)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Analyzing content...", total=None)
                
                try:
                    # Extract content from URL
                    registry = AdapterRegistry(config)
                    content = await registry.extract_content(url)
                    
                    if not content:
                        console.print("[red]Error: Could not extract content from URL[/red]")
                        raise typer.Exit(1)
                    
                    progress.update(task, description="Generating AI summary...")
                    
                    # Generate summary
                    summary = await ai_service.summarize(content, style=style)
                    
                    # Display summary
                    panel = Panel(
                        format_summary(summary),
                        title="[bold green]AI Summary[/bold green]",
                        subtitle=f"Source: {content['url'][:60]}...",
                        border_style="green"
                    )
                    console.print(panel)
                    
                    # Save to file if requested
                    if output_file:
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(summary)
                        console.print(f"[green]✓ Summary saved to {output_file}[/green]")
                    
                except Exception as e:
                    console.print(f"[red]Error generating summary: {e}[/red]")
                    raise typer.Exit(1)
        
        asyncio.run(_summarize())
    
    # Search command
    @app.command("search")
    def search_command(
        query: str = typer.Argument(..., help="Search query"),
        platforms: List[str] = typer.Option(["twitter"], "--platforms", help="Platforms to search"),
        limit: int = typer.Option(10, "--limit", help="Results per platform"),
        filter_type: Optional[str] = typer.Option(None, "--filter", help="Content filter"),
        save: bool = typer.Option(False, "--save", help="Save results"),
    ) -> None:
        """
        Search content across platforms.
        
        Examples:
        
            socialai search "AI news" --platforms twitter reddit
            socialai search "Python tutorial" --platforms reddit linkedin --filter technical
        """
        async def _search():
            config = Config.load()
            registry = AdapterRegistry(config)
            storage = Storage(config)
            
            all_results = []
            
            for platform in platforms:
                if not validate_platform(platform):
                    console.print(f"[yellow]Skipping unknown platform: {platform}[/yellow]")
                    continue
                
                console.print(f"[cyan]Searching {platform}...[/cyan]")
                
                try:
                    adapter = registry.get_adapter(platform)
                    results = await adapter.search(query, limit=limit)
                    
                    # Apply filter if specified
                    if filter_type:
                        content_filter = ContentFilter(config)
                        results = await content_filter.apply(results, filter_type)
                    
                    all_results.extend(results)
                    
                except Exception as e:
                    console.print(f"[red]Error searching {platform}: {e}[/red]")
                    continue
            
            if not all_results:
                console.print("[yellow]No results found[/yellow]")
                return
            
            # Display results
            table = Table(title="Search Results")
            table.add_column("Platform", style="cyan")
            table.add_column("Title", style="white")
            table.add_column("Author", style="dim")
            table.add_column("Score", style="green")
            
            for result in all_results:
                table.add_row(
                    result.platform,
                    result.title or result.content[:50] + "...",
                    result.author,
                    str(result.engagement_score or 0)
                )
            
            console.print(table)
            
            # Save if requested
            if save:
                await storage.save_search(query, all_results)
                console.print(f"[green]✓ Saved {len(all_results)} results[/green]")
        
        asyncio.run(_search())
    
    # AI command group
    ai_app = typer.Typer(name="ai", help="AI-powered features")
    app.add_typer(ai_app)
    
    @ai_app.command("score")
    def ai_score_command(
        content: str = typer.Argument(..., help="Content to analyze"),
        ai_provider: Optional[str] = typer.Option(None, "--provider", help="AI provider"),
    ) -> None:
        """Score content for engagement potential."""
        async def _score():
            config = Config.load()
            ai_service = AIService(config, provider=ai_provider)
            
            score = await ai_service.score_content(content)
            
            panel = Panel(
                f"Engagement Score: [bold green]{score}/10[/bold green]\n\n"
                f"Analysis: {score.analysis}",
                title="AI Content Analysis",
                border_style="green"
            )
            console.print(panel)
        
        asyncio.run(_score())
    
    @ai_app.command("insights")
    def ai_insights_command(
        query: str = typer.Argument(..., help="Query to analyze"),
        ai_provider: Optional[str] = typer.Option(None, "--provider", help="AI provider"),
    ) -> None:
        """Extract key insights from content."""
        async def _insights():
            config = Config.load()
            ai_service = AIService(config, provider=ai_provider)
            
            insights = await ai_service.extract_insights(query)
            
            panel = Panel(
                format_summary(insights),
                title="Key Insights",
                border_style="blue"
            )
            console.print(panel)
        
        asyncio.run(_insights())
    
    # Focus mode
    @app.command("focus")
    def focus_command(
        enable: bool = typer.Option(True, "--enable/--disable", help="Enable/disable focus mode"),
        duration: int = typer.Option(30, "--duration", help="Session duration in minutes"),
    ) -> None:
        """
        Enable distraction-free focus mode.
        
        Examples:
        
            socialai focus --enable --duration 45
            socialai focus --disable
        """
        async def _focus():
            config = Config.load()
            session_manager = SessionManager(config)
            
            if enable:
                session = await session_manager.start_focus_session(duration)
                console.print(f"[green]✓ Focus mode enabled for {duration} minutes[/green]")
                console.print(f"[dim]Session ID: {session.id}[/dim]")
                
                # Show focus mode tips
                tips = [
                    "Avoid checking notifications",
                    "Focus on content consumption only",
                    "Take breaks every 5-10 minutes",
                    "Use 'q' to quit focus mode early"
                ]
                
                for tip in tips:
                    console.print(f"[dim]• {tip}[/dim]")
            else:
                await session_manager.end_focus_session()
                console.print("[yellow]Focus mode disabled[/yellow]")
        
        asyncio.run(_focus())
    
    # Config command group
    config_app = typer.Typer(name="config", help="Configuration management")
    app.add_typer(config_app)
    
    @config_app.command("show")
    def config_show_command() -> None:
        """Show current configuration."""
        config = Config.load()
        
        # Create config display
        config_text = f"""
AI Configuration:
  Provider: {config.ai.provider}
  Model: {config.ai.model}
  Temperature: {config.ai.temperature}

Platforms:
  Twitter: {'Enabled' if config.platforms.twitter.enabled else 'Disabled'}
  Reddit: {'Enabled' if config.platforms.reddit.enabled else 'Disabled'}
  LinkedIn: {'Enabled' if config.platforms.linkedin.enabled else 'Disabled'}

Focus Mode:
  Enabled: {config.focus.enabled}
  Duration: {config.focus.session_duration} minutes
  
Output:
  Format: {config.output.format}
  Color: {config.output.color}
"""
        
        panel = Panel(
            config_text.strip(),
            title="Current Configuration",
            border_style="cyan"
        )
        console.print(panel)
    
    @config_app.command("set")
    def config_set_command(
        key: str = typer.Argument(..., help="Configuration key (e.g., ai.provider)"),
        value: str = typer.Argument(..., help="Configuration value"),
    ) -> None:
        """Set a configuration value."""
        config = Config.load()
        
        try:
            config.set_value(key, value)
            console.print(f"[green]✓ Set {key} = {value}[/green]")
        except Exception as e:
            console.print(f"[red]Error setting configuration: {e}[/red]")
            raise typer.Exit(1)
    
    # Session management
    @app.command("session")
    def session_command(
        action: str = typer.Argument(..., help="Action: start, end, status"),
        platforms: Optional[List[str]] = typer.Option(None, "--platforms", help="Platforms to include"),
        duration: int = typer.Option(30, "--duration", help="Session duration in minutes"),
    ) -> None:
        """Manage focused reading sessions."""
        async def _session():
            config = Config.load()
            session_manager = SessionManager(config)
            
            if action == "start":
                session = await session_manager.start_session(platforms or [], duration)
                console.print(f"[green]✓ Started session: {session.id}[/green]")
                console.print(f"[dim]Duration: {duration} minutes[/dim]")
                console.print(f"[dim]Platforms: {', '.join(platforms or ['all enabled'])}[/dim]")
                
            elif action == "end":
                session = await session_manager.end_session()
                if session:
                    console.print(f"[yellow]✓ Ended session: {session.id}[/yellow]")
                    console.print(f"[dim]Duration: {session.duration} minutes[/dim]")
                else:
                    console.print("[yellow]No active session[/yellow]")
                    
            elif action == "status":
                session = await session_manager.get_current_session()
                if session:
                    time_left = session.get_time_remaining()
                    console.print(f"[cyan]Active session: {session.id}[/cyan]")
                    console.print(f"[cyan]Time remaining: {time_left} minutes[/cyan]")
                    console.print(f"[cyan]Platforms: {', '.join(session.platforms)}[/cyan]")
                else:
                    console.print("[yellow]No active session[/yellow]")
        
        asyncio.run(_session())
    
    return app
