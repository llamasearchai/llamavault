#!/usr/bin/env python3
"""
Command-line interface for LlamaVault credential management
"""

import os
import sys
import logging
import getpass
from pathlib import Path
from typing import Optional, List, Dict, Any
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich import box
import json

from . import __version__
from .vault import Vault
from .exceptions import VaultError, CredentialNotFoundError, AuthenticationError, EncryptionError

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("llamavault.cli")

# Create rich console
console = Console()

# Create click context settings
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

def print_version(ctx, param, value):
    """Print the version and exit"""
    if not value or ctx.resilient_parsing:
        return
    console.print(f"[bold green]LlamaVault[/bold green] version: [bold]{__version__}[/bold]")
    ctx.exit()

def get_vault_password() -> str:
    """Get vault password from environment or prompt"""
    password = os.environ.get("LLAMAVAULT_PASSWORD")
    if not password:
        password = getpass.getpass("Vault password: ")
    return password

@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.option('--vault-dir', type=click.Path(), help='Custom vault directory')
@click.option('--version', is_flag=True, callback=print_version, 
             expose_value=False, is_eager=True, help='Show version and exit')
@click.pass_context
def cli(ctx: click.Context, debug: bool, vault_dir: Optional[str]) -> None:
    """
    LlamaVault - Secure credential management for LLM apps
    
    Store and manage API keys and other credentials securely.
    """
    # Setup logging level
    if debug:
        logging.getLogger("llamavault").setLevel(logging.DEBUG)
        
    # Store common options in context
    ctx.ensure_object(dict)
    ctx.obj['debug'] = debug
    ctx.obj['vault_dir'] = vault_dir

@cli.command()
@click.option('--force', is_flag=True, help='Overwrite existing vault')
@click.pass_context
def init(ctx: click.Context, force: bool) -> None:
    """Initialize a new vault"""
    vault_dir = ctx.obj.get('vault_dir')
    
    with console.status("[bold green]Initializing vault...[/bold green]"):
        try:
            # Get password for the new vault
            password = getpass.getpass("New vault password: ")
            password_confirm = getpass.getpass("Confirm password: ")
            
            if password != password_confirm:
                console.print("[bold red]Passwords don't match![/bold red]")
                sys.exit(1)
            
            # Create vault
            vault = Vault(vault_dir=vault_dir, password=password)
            vault.init(force=force)
            
            console.print("[bold green]✓[/bold green] Vault initialized successfully!")
        except VaultError as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            sys.exit(1)

@cli.command()
@click.argument('name')
@click.pass_context
def add(ctx: click.Context, name: str) -> None:
    """Add a credential to the vault"""
    vault_dir = ctx.obj.get('vault_dir')
    
    try:
        # Get password for the vault
        password = get_vault_password()
        
        # Get credential value
        value = getpass.getpass(f"Enter value for '{name}': ")
        
        # Get optional metadata
        add_metadata = Confirm.ask("Add metadata?", default=False)
        metadata = {}
        
        if add_metadata:
            console.print("Enter metadata (empty key to finish):")
            while True:
                key = Prompt.ask("  Key")
                if not key:
                    break
                value_meta = Prompt.ask("  Value")
                metadata[key] = value_meta
        
        # Open vault and add credential
        with console.status(f"[bold green]Adding credential '{name}'...[/bold green]"):
            vault = Vault(vault_dir=vault_dir, password=password)
            vault.add_credential(name, value, metadata=metadata)
        
        console.print(f"[bold green]✓[/bold green] Added credential: [bold]{name}[/bold]")
        
    except VaultError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)

@cli.command()
@click.argument('name')
@click.pass_context
def get(ctx: click.Context, name: str) -> None:
    """Retrieve a credential from the vault"""
    vault_dir = ctx.obj.get('vault_dir')
    
    try:
        # Get password for the vault
        password = get_vault_password()
        
        # Open vault and get credential
        with console.status(f"[bold green]Retrieving credential '{name}'...[/bold green]"):
            vault = Vault(vault_dir=vault_dir, password=password)
            value = vault.get_credential(name)
        
        console.print(f"[bold]{name}[/bold]: {value}")
        
    except CredentialNotFoundError:
        console.print(f"[bold red]Error:[/bold red] Credential '{name}' not found")
        sys.exit(1)
    except VaultError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)

@cli.command()
@click.pass_context
def list(ctx: click.Context) -> None:
    """List all credentials in the vault"""
    vault_dir = ctx.obj.get('vault_dir')
    
    try:
        # Get password for the vault
        password = get_vault_password()
        
        # Open vault and list credentials
        with console.status("[bold green]Listing credentials...[/bold green]"):
            vault = Vault(vault_dir=vault_dir, password=password)
            credentials = vault.get_all_credentials()
        
        if not credentials:
            console.print("[yellow]No credentials found in vault[/yellow]")
            return
            
        # Display credentials in a table
        table = Table(title="Credentials", box=box.ROUNDED)
        table.add_column("Name", style="cyan")
        table.add_column("Created", style="green")
        table.add_column("Updated", style="yellow")
        table.add_column("Last Accessed", style="blue")
        table.add_column("Metadata", style="magenta")
        
        for name, cred in credentials.items():
            created = cred.created_at.strftime("%Y-%m-%d %H:%M") if cred.created_at else "N/A"
            updated = cred.updated_at.strftime("%Y-%m-%d %H:%M") if cred.updated_at else "N/A"
            accessed = cred.last_accessed.strftime("%Y-%m-%d %H:%M") if cred.last_accessed else "Never"
            metadata = json.dumps(cred.metadata) if cred.metadata else ""
            
            table.add_row(name, created, updated, accessed, metadata)
        
        console.print(table)
        
    except VaultError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)

@cli.command()
@click.argument('name')
@click.pass_context
def remove(ctx: click.Context, name: str) -> None:
    """Remove a credential from the vault"""
    vault_dir = ctx.obj.get('vault_dir')
    
    try:
        # Get password for the vault
        password = get_vault_password()
        
        # Confirm deletion
        if not Confirm.ask(f"Are you sure you want to remove '{name}'?", default=False):
            console.print("Operation cancelled.")
            return
        
        # Open vault and remove credential
        with console.status(f"[bold green]Removing credential '{name}'...[/bold green]"):
            vault = Vault(vault_dir=vault_dir, password=password)
            vault.remove_credential(name)
        
        console.print(f"[bold green]✓[/bold green] Removed credential: [bold]{name}[/bold]")
        
    except CredentialNotFoundError:
        console.print(f"[bold red]Error:[/bold red] Credential '{name}' not found")
        sys.exit(1)
    except VaultError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)

@cli.command()
@click.argument('output_file', type=click.Path())
@click.option('--uppercase/--no-uppercase', default=True, 
             help='Convert environment variable names to uppercase')
@click.pass_context
def export(ctx: click.Context, output_file: str, uppercase: bool) -> None:
    """Export credentials to a .env file"""
    vault_dir = ctx.obj.get('vault_dir')
    
    try:
        # Get password for the vault
        password = get_vault_password()
        
        # Open vault and export credentials
        with console.status(f"[bold green]Exporting credentials to {output_file}...[/bold green]"):
            vault = Vault(vault_dir=vault_dir, password=password)
            vault.export_env_file(output_file, uppercase=uppercase)
        
        console.print(f"[bold green]✓[/bold green] Credentials exported to: [bold]{output_file}[/bold]")
        
    except VaultError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)

@cli.command()
@click.option('--backup-dir', type=click.Path(), help='Directory to store backup')
@click.pass_context
def backup(ctx: click.Context, backup_dir: Optional[str]) -> None:
    """Create a backup of the vault"""
    vault_dir = ctx.obj.get('vault_dir')
    
    try:
        # Get password for the vault
        password = get_vault_password()
        
        # Open vault and create backup
        with console.status("[bold green]Creating backup...[/bold green]"):
            vault = Vault(vault_dir=vault_dir, password=password)
            backup_path = vault.backup(backup_dir=backup_dir)
        
        console.print(f"[bold green]✓[/bold green] Backup created at: [bold]{backup_path}[/bold]")
        
    except VaultError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)

@cli.command()
@click.pass_context
def change_password(ctx: click.Context) -> None:
    """Change the vault password"""
    vault_dir = ctx.obj.get('vault_dir')
    
    try:
        # Get current password
        current_password = get_vault_password()
        
        # Get new password
        new_password = getpass.getpass("New password: ")
        confirm_password = getpass.getpass("Confirm new password: ")
        
        if new_password != confirm_password:
            console.print("[bold red]Passwords don't match![/bold red]")
            sys.exit(1)
        
        # Open vault and change password
        with console.status("[bold green]Changing password...[/bold green]"):
            vault = Vault(vault_dir=vault_dir, password=current_password)
            vault.change_password(new_password)
        
        console.print("[bold green]✓[/bold green] Password changed successfully!")
        
    except VaultError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)

@cli.command()
@click.option('--host', default='127.0.0.1', help='Host to listen on')
@click.option('--port', default=5000, help='Port to listen on')
@click.pass_context
def web(ctx: click.Context, host: str, port: int) -> None:
    """Start the web interface"""
    # This will be imported here to avoid dependencies when not needed
    try:
        from .web import app
    except ImportError:
        console.print("[bold red]Error:[/bold red] Web interface dependencies not installed.")
        console.print("Install them with: [bold]pip install llamavault[web][/bold]")
        sys.exit(1)
    
    vault_dir = ctx.obj.get('vault_dir')
    
    console.print(Panel(
        "[bold green]LlamaVault Web Interface[/bold green]\n\n"
        f"Starting server on [bold]http://{host}:{port}[/bold]\n"
        "Press CTRL+C to stop",
        title="Web Server",
        border_style="green"
    ))
    
    # Set environment variable for vault directory
    if vault_dir:
        os.environ['LLAMAVAULT_DIR'] = str(vault_dir)
    
    # Start web server
    app.run(host=host, port=port, debug=ctx.obj.get('debug', False))

def main() -> None:
    """Main entry point for CLI"""
    try:
        cli(obj={})
    except Exception as e:
        console.print(f"[bold red]Unhandled error:[/bold red] {e}")
        if os.environ.get("LLAMAVAULT_DEBUG"):
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)

if __name__ == '__main__':
    main() 