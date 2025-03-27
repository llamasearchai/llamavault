#!/usr/bin/env python3
"""
LlamaVault CLI - Command-line interface for the LlamaVault credential management system
"""

import os
import sys
import argparse
import logging
import getpass
from pathlib import Path
from typing import Dict, List, Optional, Any
import json

from llamavault.core import LlamaVault, CredentialType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("llamavault.cli")

def init_command(args):
    """Initialize a new LlamaVault."""
    vault_path = args.path or os.environ.get("LLAMAVAULT_PATH")
    vault = LlamaVault(vault_path)
    logger.info(f"Initialized LlamaVault at {vault.vault_path}")
    
def add_command(args):
    """Add a credential to the vault."""
    vault_path = args.path or os.environ.get("LLAMAVAULT_PATH")
    vault = LlamaVault(vault_path)
    
    name = args.name
    
    # Get value interactively if not provided
    if args.value:
        value = args.value
    else:
        value = getpass.getpass(f"Enter value for {name}: ")
        confirm = getpass.getpass(f"Confirm value for {name}: ")
        if value != confirm:
            logger.error("Values do not match")
            sys.exit(1)
    
    # Parse credential type
    cred_type = CredentialType.API_KEY
    if args.type:
        try:
            cred_type = CredentialType(args.type)
        except ValueError:
            logger.error(f"Invalid credential type: {args.type}")
            sys.exit(1)
    
    # Parse tags
    tags = args.tags.split(",") if args.tags else None
    
    # Parse metadata
    metadata = {}
    if args.metadata:
        for item in args.metadata:
            key, val = item.split("=", 1)
            metadata[key] = val
    
    # Add credential
    try:
        vault.add_credential(name, value, cred_type, tags, metadata)
        logger.info(f"Added credential: {name}")
    except Exception as e:
        logger.error(f"Error adding credential: {e}")
        sys.exit(1)

def get_command(args):
    """Get a credential from the vault."""
    vault_path = args.path or os.environ.get("LLAMAVAULT_PATH")
    vault = LlamaVault(vault_path)
    
    try:
        credential = vault.get_credential(args.name)
        
        if args.quiet:
            # Print only the value
            print(credential["value"])
        elif args.json:
            # Print full JSON
            print(json.dumps(credential, indent=2))
        else:
            # Print formatted output
            print(f"Name: {credential['name']}")
            print(f"Type: {credential['type']}")
            print(f"Value: {credential['value']}")
            if credential.get("tags"):
                print(f"Tags: {', '.join(credential['tags'])}")
            if credential.get("metadata"):
                print("Metadata:")
                for key, val in credential["metadata"].items():
                    print(f"  {key}: {val}")
                    
    except Exception as e:
        logger.error(f"Error retrieving credential: {e}")
        sys.exit(1)

def list_command(args):
    """List all credentials in the vault."""
    vault_path = args.path or os.environ.get("LLAMAVAULT_PATH")
    vault = LlamaVault(vault_path)
    
    try:
        credentials = vault.list_credentials(tag=args.tag, cred_type=args.type)
        
        if args.json:
            # Print JSON output (without values for security)
            for cred in credentials:
                cred.pop("value", None)
            print(json.dumps(credentials, indent=2))
        else:
            # Print formatted table
            if not credentials:
                print("No credentials found")
                return
                
            # Determine column widths
            name_width = max(4, max(len(c["name"]) for c in credentials))
            type_width = max(4, max(len(c["type"]) for c in credentials))
            
            # Print header
            print(f"{'NAME':<{name_width}} {'TYPE':<{type_width}} {'TAGS'}")
            print(f"{'-'*name_width} {'-'*type_width} {'-'*10}")
            
            # Print credentials
            for cred in credentials:
                tags = ", ".join(cred.get("tags", []))
                print(f"{cred['name']:<{name_width}} {cred['type']:<{type_width}} {tags}")
                
    except Exception as e:
        logger.error(f"Error listing credentials: {e}")
        sys.exit(1)

def remove_command(args):
    """Remove a credential from the vault."""
    vault_path = args.path or os.environ.get("LLAMAVAULT_PATH")
    vault = LlamaVault(vault_path)
    
    try:
        vault.remove_credential(args.name)
        logger.info(f"Removed credential: {args.name}")
    except Exception as e:
        logger.error(f"Error removing credential: {e}")
        sys.exit(1)

def rotate_command(args):
    """Rotate a credential."""
    vault_path = args.path or os.environ.get("LLAMAVAULT_PATH")
    vault = LlamaVault(vault_path)
    
    # Get new value interactively if not provided
    if args.value:
        new_value = args.value
    else:
        new_value = getpass.getpass(f"Enter new value for {args.name}: ")
        confirm = getpass.getpass(f"Confirm new value for {args.name}: ")
        if new_value != confirm:
            logger.error("Values do not match")
            sys.exit(1)
    
    try:
        vault.rotate_credential(args.name, new_value)
        logger.info(f"Rotated credential: {args.name}")
    except Exception as e:
        logger.error(f"Error rotating credential: {e}")
        sys.exit(1)

def import_command(args):
    """Import credentials from a file."""
    vault_path = args.path or os.environ.get("LLAMAVAULT_PATH")
    vault = LlamaVault(vault_path)
    
    try:
        # Read input file
        with open(args.file, "r") as f:
            if args.file.endswith(".json"):
                # JSON format
                credentials = json.load(f)
            elif args.file.endswith((".env", ".txt")):
                # .env format
                credentials = {}
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    key, value = line.split("=", 1)
                    credentials[key.strip()] = {
                        "value": value.strip().strip("\"'"),
                        "type": "api_key"
                    }
            else:
                logger.error(f"Unsupported file format: {args.file}")
                sys.exit(1)
        
        # Import credentials
        count = 0
        for name, data in credentials.items():
            if isinstance(data, str):
                # Simple key-value format
                value = data
                cred_type = CredentialType.API_KEY
                tags = None
                metadata = None
            else:
                # Detailed format
                value = data["value"]
                cred_type = CredentialType(data.get("type", "api_key"))
                tags = data.get("tags")
                metadata = data.get("metadata")
                
            vault.add_credential(name, value, cred_type, tags, metadata)
            count += 1
            
        logger.info(f"Imported {count} credentials")
        
    except Exception as e:
        logger.error(f"Error importing credentials: {e}")
        sys.exit(1)

def export_command(args):
    """Export credentials to a file."""
    vault_path = args.path or os.environ.get("LLAMAVAULT_PATH")
    vault = LlamaVault(vault_path)
    
    try:
        # Get credentials
        credentials = vault.list_credentials(tag=args.tag, cred_type=args.type)
        
        # Format output
        if args.format == "json":
            # Full JSON format
            output = json.dumps({c["name"]: c for c in credentials}, indent=2)
        elif args.format == "env":
            # .env format
            lines = []
            for cred in credentials:
                name = cred["name"]
                value = vault.get_credential(name)["value"]
                lines.append(f"{name}={value}")
            output = "\n".join(lines)
        else:
            logger.error(f"Unsupported export format: {args.format}")
            sys.exit(1)
            
        # Write output
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            logger.info(f"Exported credentials to {args.output}")
        else:
            print(output)
            
    except Exception as e:
        logger.error(f"Error exporting credentials: {e}")
        sys.exit(1)

def analyze_command(args):
    """Analyze a repository for configuration patterns."""
    vault_path = args.path or os.environ.get("LLAMAVAULT_PATH")
    vault = LlamaVault(vault_path)
    
    try:
        analysis = vault.analyze_configuration(args.repo)
        print(json.dumps(analysis, indent=2))
    except Exception as e:
        logger.error(f"Error analyzing repository: {e}")
        sys.exit(1)

def docs_command(args):
    """Generate documentation for a repository."""
    vault_path = args.path or os.environ.get("LLAMAVAULT_PATH")
    vault = LlamaVault(vault_path)
    
    try:
        from llamavault.auto_doc_generator import DocGenerator
        generator = DocGenerator(args.repo, args.format)
        doc_content = generator.generate_documentation(args.output)
        
        if not args.output:
            print(doc_content)
            
    except ImportError:
        logger.error("Documentation generator not available")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error generating documentation: {e}")
        sys.exit(1)

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="LlamaVault - Enterprise-grade credential management"
    )
    
    # Global options
    parser.add_argument(
        "--path", "-p",
        help="Path to the vault directory (default: $LLAMAVAULT_PATH or ~/.llamavault)"
    )
    
    subparsers = parser.add_subparsers(dest="command")
    
    # init command
    init_parser = subparsers.add_parser(
        "init", 
        help="Initialize a new vault"
    )
    
    # add command
    add_parser = subparsers.add_parser(
        "add", 
        help="Add a credential to the vault"
    )
    add_parser.add_argument("name", help="Name of the credential")
    add_parser.add_argument("--value", "-v", help="Value of the credential (if not provided, will prompt)")
    add_parser.add_argument("--type", "-t", choices=[t.value for t in CredentialType], help="Type of credential")
    add_parser.add_argument("--tags", help="Comma-separated list of tags")
    add_parser.add_argument("--metadata", "-m", action="append", help="Metadata in the format key=value")
    
    # get command
    get_parser = subparsers.add_parser(
        "get", 
        help="Get a credential from the vault"
    )
    get_parser.add_argument("name", help="Name of the credential")
    get_parser.add_argument("--quiet", "-q", action="store_true", help="Output only the value")
    get_parser.add_argument("--json", "-j", action="store_true", help="Output in JSON format")
    
    # list command
    list_parser = subparsers.add_parser(
        "list", 
        help="List credentials in the vault"
    )
    list_parser.add_argument("--tag", "-t", help="Filter by tag")
    list_parser.add_argument("--type", choices=[t.value for t in CredentialType], help="Filter by type")
    list_parser.add_argument("--json", "-j", action="store_true", help="Output in JSON format")
    
    # remove command
    remove_parser = subparsers.add_parser(
        "remove", 
        help="Remove a credential from the vault"
    )
    remove_parser.add_argument("name", help="Name of the credential")
    
    # rotate command
    rotate_parser = subparsers.add_parser(
        "rotate", 
        help="Rotate a credential"
    )
    rotate_parser.add_argument("name", help="Name of the credential")
    rotate_parser.add_argument("--value", "-v", help="New value (if not provided, will prompt)")
    
    # import command
    import_parser = subparsers.add_parser(
        "import", 
        help="Import credentials from a file"
    )
    import_parser.add_argument("file", help="File to import (.json, .env)")
    
    # export command
    export_parser = subparsers.add_parser(
        "export", 
        help="Export credentials to a file"
    )
    export_parser.add_argument("--output", "-o", help="Output file (if not provided, prints to stdout)")
    export_parser.add_argument("--format", "-f", choices=["json", "env"], default="env", help="Export format")
    export_parser.add_argument("--tag", "-t", help="Filter by tag")
    export_parser.add_argument("--type", choices=[t.value for t in CredentialType], help="Filter by type")
    
    # analyze command
    analyze_parser = subparsers.add_parser(
        "analyze", 
        help="Analyze a repository for configuration patterns"
    )
    analyze_parser.add_argument("repo", help="Path to the repository")
    
    # docs command
    docs_parser = subparsers.add_parser(
        "docs", 
        help="Generate documentation for a repository"
    )
    docs_parser.add_argument("repo", help="Path to the repository")
    docs_parser.add_argument("--format", "-f", choices=["markdown", "html", "rst"], default="markdown", help="Output format")
    docs_parser.add_argument("--output", "-o", help="Output file (if not provided, prints to stdout)")
    
    return parser.parse_args()

def main():
    """Main function."""
    args = parse_args()
    
    # Execute the requested command
    if args.command == "init":
        init_command(args)
    elif args.command == "add":
        add_command(args)
    elif args.command == "get":
        get_command(args)
    elif args.command == "list":
        list_command(args)
    elif args.command == "remove":
        remove_command(args)
    elif args.command == "rotate":
        rotate_command(args)
    elif args.command == "import":
        import_command(args)
    elif args.command == "export":
        export_command(args)
    elif args.command == "analyze":
        analyze_command(args)
    elif args.command == "docs":
        docs_command(args)
    else:
        # No command specified, show help
        print("LlamaVault - Enterprise-grade credential management\n")
        print("Available commands:")
        print("  init      Initialize a new vault")
        print("  add       Add a credential to the vault")
        print("  get       Get a credential from the vault")
        print("  list      List credentials in the vault")
        print("  remove    Remove a credential from the vault")
        print("  rotate    Rotate a credential")
        print("  import    Import credentials from a file")
        print("  export    Export credentials to a file")
        print("  analyze   Analyze a repository for configuration patterns")
        print("  docs      Generate documentation for a repository")
        print("\nUse llamavault <command> --help for more information about a command.")

if __name__ == "__main__":
    main() 