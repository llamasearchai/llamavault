#!/usr/bin/env python3
"""
LlamaVault Auto Documentation Generator

This module uses an AI-powered approach to generate comprehensive, context-aware
documentation for repository configuration settings.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import argparse
import re
import importlib
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("llamavault.doc_generator")

# Import AI engine if available
try:
    from llama_ai_config_engine import SmartConfigurationManager
    HAS_AI_ENGINE = True
except ImportError:
    HAS_AI_ENGINE = False
    logger.warning("AI engine not available. Some features will be limited.")

class DocGenerator:
    """Generate context-aware documentation for repository configuration."""
    
    def __init__(self, repo_path: Union[str, Path], output_format: str = "markdown"):
        """
        Initialize the documentation generator.
        
        Args:
            repo_path: Path to the repository to analyze
            output_format: Format for generated documentation (markdown, html, rst)
        """
        self.repo_path = Path(repo_path).resolve()
        if not self.repo_path.exists():
            raise FileNotFoundError(f"Repository path does not exist: {self.repo_path}")
            
        self.output_format = output_format
        self.config_files = []
        self.env_vars = []
        self.api_keys = {}
        
        # Initialize AI engine if available
        if HAS_AI_ENGINE:
            self.ai_engine = SmartConfigurationManager(str(self.repo_path))
        else:
            self.ai_engine = None
            
    def analyze_repository(self) -> Dict[str, Any]:
        """
        Analyze repository for configuration patterns.
        
        Returns:
            Dict containing analysis results
        """
        logger.info(f"Analyzing repository: {self.repo_path}")
        
        if self.ai_engine:
            # Use AI engine for analysis
            return self.ai_engine.analyze_repository()
        else:
            # Fall back to basic analysis
            return self._basic_analyze()
            
    def _basic_analyze(self) -> Dict[str, Any]:
        """Basic repository analysis without AI engine."""
        result = {
            "config_files": [],
            "env_vars": [],
            "api_keys": {}
        }
        
        # Find configuration files
        config_patterns = ["*.ini", "*.yaml", "*.yml", "*.json", "*.toml", ".env*"]
        for pattern in config_patterns:
            for file_path in self.repo_path.glob(f"**/{pattern}"):
                if ".git" not in str(file_path):
                    result["config_files"].append(str(file_path.relative_to(self.repo_path)))
        
        # Find environment variables in Python files
        for py_file in self.repo_path.glob("**/*.py"):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                # Simple regex to find environment variables
                env_vars = re.findall(r'os\.environ(?:\.get)?\(["\']([A-Za-z0-9_]+)["\']', content)
                env_vars += re.findall(r'os\.environ\[["\']([A-Za-z0-9_]+)["\']', content)
                
                for var in env_vars:
                    if var not in result["env_vars"]:
                        result["env_vars"].append(var)
            except Exception as e:
                logger.warning(f"Error analyzing {py_file}: {e}")
                
        return result
    
    def generate_documentation(self, output_file: Optional[Union[str, Path]] = None) -> str:
        """
        Generate documentation for repository configuration.
        
        Args:
            output_file: Path to write documentation (if None, returns as string)
            
        Returns:
            Generated documentation content
        """
        logger.info("Generating documentation...")
        
        # Analyze repository
        analysis = self.analyze_repository()
        
        # Generate documentation
        if self.ai_engine:
            # Use AI engine for enhanced documentation
            doc_content = self._generate_ai_documentation(analysis)
        else:
            # Fall back to basic documentation
            doc_content = self._generate_basic_documentation(analysis)
            
        # Write to file if specified
        if output_file:
            output_path = Path(output_file)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(doc_content)
            logger.info(f"Documentation written to {output_path}")
            
        return doc_content
        
    def _generate_ai_documentation(self, analysis: Dict[str, Any]) -> str:
        """Generate enhanced documentation using AI engine."""
        try:
            # Create prompt template for documentation
            doc_template = {
                "markdown": """
                # Configuration Documentation for {repo_name}
                
                This documentation was automatically generated by LlamaVault on {date}.
                
                ## Overview
                
                {overview}
                
                ## Configuration Files
                
                {config_files}
                
                ## Environment Variables
                
                {env_vars}
                
                ## API Keys and Credentials
                
                {api_keys}
                
                ## Best Practices
                
                {best_practices}
                
                ## Security Considerations
                
                {security}
                """,
                "html": """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Configuration Documentation - {repo_name}</title>
                    <style>
                        body { font-family: Arial, sans-serif; line-height: 1.6; }
                        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
                        h1 { color: #333; }
                        h2 { color: #444; margin-top: 30px; }
                        code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
                        pre { background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }
                        .warning { background: #fff8e1; padding: 10px; border-left: 4px solid #ffc107; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Configuration Documentation for {repo_name}</h1>
                        <p><em>This documentation was automatically generated by LlamaVault on {date}.</em></p>
                        
                        <h2>Overview</h2>
                        <p>{overview}</p>
                        
                        <h2>Configuration Files</h2>
                        {config_files}
                        
                        <h2>Environment Variables</h2>
                        {env_vars}
                        
                        <h2>API Keys and Credentials</h2>
                        {api_keys}
                        
                        <h2>Best Practices</h2>
                        {best_practices}
                        
                        <h2>Security Considerations</h2>
                        <div class="warning">
                            {security}
                        </div>
                    </div>
                </body>
                </html>
                """
            }
            
            # Get AI analysis for each section
            repo_name = self.repo_path.name
            date = datetime.now().strftime("%Y-%m-%d")
            
            # Get overview from AI
            overview = self.ai_engine.generate_section("overview", analysis)
            
            # Format config files section
            config_files_content = self.ai_engine.generate_section("config_files", analysis)
            
            # Format environment variables section
            env_vars_content = self.ai_engine.generate_section("env_vars", analysis)
            
            # Format API keys section
            api_keys_content = self.ai_engine.generate_section("api_keys", analysis)
            
            # Get best practices from AI
            best_practices = self.ai_engine.generate_section("best_practices", analysis)
            
            # Get security considerations from AI
            security = self.ai_engine.generate_section("security", analysis)
            
            # Combine into complete documentation
            template = doc_template.get(self.output_format, doc_template["markdown"])
            doc_content = template.format(
                repo_name=repo_name,
                date=date,
                overview=overview,
                config_files=config_files_content,
                env_vars=env_vars_content,
                api_keys=api_keys_content,
                best_practices=best_practices,
                security=security
            )
            
            return doc_content
            
        except Exception as e:
            logger.error(f"Error generating AI documentation: {e}")
            return self._generate_basic_documentation(analysis)
            
    def _generate_basic_documentation(self, analysis: Dict[str, Any]) -> str:
        """Generate basic documentation without AI enhancement."""
        repo_name = self.repo_path.name
        date = datetime.now().strftime("%Y-%m-%d")
        
        if self.output_format == "markdown":
            # Markdown format
            lines = [
                f"# Configuration Documentation for {repo_name}\n",
                f"*Generated on {date}*\n",
                "## Configuration Files\n"
            ]
            
            # Add config files
            for file in analysis.get("config_files", []):
                lines.append(f"- `{file}`\n")
                
            lines.append("\n## Environment Variables\n")
            
            # Add environment variables
            for var in analysis.get("env_vars", []):
                lines.append(f"- `{var}`\n")
                
            lines.append("\n## API Keys and Credentials\n")
            lines.append("The following API keys and credentials were detected:\n")
            
            # Add API keys
            for key, file in analysis.get("api_keys", {}).items():
                lines.append(f"- `{key}` (found in `{file}`)\n")
                
            return "".join(lines)
            
        elif self.output_format == "html":
            # HTML format
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Configuration Documentation - {repo_name}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                    .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                    h1 {{ color: #333; }}
                    h2 {{ color: #444; margin-top: 30px; }}
                    code {{ background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Configuration Documentation for {repo_name}</h1>
                    <p><em>Generated on {date}</em></p>
                    
                    <h2>Configuration Files</h2>
                    <ul>
            """
            
            # Add config files
            for file in analysis.get("config_files", []):
                html += f"        <li><code>{file}</code></li>\n"
                
            html += """
                    </ul>
                    
                    <h2>Environment Variables</h2>
                    <ul>
            """
            
            # Add environment variables
            for var in analysis.get("env_vars", []):
                html += f"        <li><code>{var}</code></li>\n"
                
            html += """
                    </ul>
                    
                    <h2>API Keys and Credentials</h2>
                    <p>The following API keys and credentials were detected:</p>
                    <ul>
            """
            
            # Add API keys
            for key, file in analysis.get("api_keys", {}).items():
                html += f"        <li><code>{key}</code> (found in <code>{file}</code>)</li>\n"
                
            html += """
                    </ul>
                </div>
            </body>
            </html>
            """
            
            return html
            
        else:
            # Default to simple text
            lines = [
                f"Configuration Documentation for {repo_name}",
                f"Generated on {date}\n",
                "Configuration Files:"
            ]
            
            for file in analysis.get("config_files", []):
                lines.append(f"- {file}")
                
            lines.append("\nEnvironment Variables:")
            
            for var in analysis.get("env_vars", []):
                lines.append(f"- {var}")
                
            lines.append("\nAPI Keys and Credentials:")
            
            for key, file in analysis.get("api_keys", {}).items():
                lines.append(f"- {key} (found in {file})")
                
            return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate context-aware documentation for repository configuration"
    )
    
    parser.add_argument(
        "repo_path",
        type=str,
        help="Path to the repository to analyze"
    )
    
    parser.add_argument(
        "--format", "-f",
        type=str,
        choices=["markdown", "html", "rst"],
        default="markdown",
        help="Output format for documentation"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file for documentation"
    )
    
    return parser.parse_args()


def main() -> None:
    """Main function."""
    args = parse_args()
    
    try:
        # Initialize generator
        generator = DocGenerator(
            repo_path=args.repo_path,
            output_format=args.format
        )
        
        # Generate documentation
        doc_content = generator.generate_documentation(
            output_file=args.output
        )
        
        # Print if no output file specified
        if not args.output:
            print(doc_content)
            
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 