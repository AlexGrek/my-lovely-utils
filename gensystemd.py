#!/usr/bin/env python3
"""
SystemD Service Generator
Creates, installs, and manages simple systemd services.

Usage:
    python3 gensystemd.py "service-name" "command"
    python3 gensystemd.py "service-name" "command" --install
    python3 gensystemd.py "service-name" "command" --save
"""

import sys
import os
import subprocess
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# SystemD service template
SERVICE_TEMPLATE = """[Unit]
Description={description}
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/bin/bash -c "{command}"
Restart=always
RestartSec=10
User=root

[Install]
WantedBy=multi-user.target
"""

def generate_service_content(service_name, command):
    """Generate systemd service file content."""
    logger.info(f"Generating service content for '{service_name}'")
    
    # Create a description based on the service name
    description = f"Custom service: {service_name}"
    
    # Generate the service content
    content = SERVICE_TEMPLATE.format(
        description=description,
        command=command
    )
    
    logger.info(f"Service content generated successfully")
    return content

def get_service_path(service_name):
    """Get the full path for the systemd service file."""
    if not service_name.endswith('.service'):
        service_name += '.service'
    
    service_path = Path('/etc/systemd/system') / service_name
    logger.info(f"Service path: {service_path}")
    return service_path

def check_root_privileges():
    """Check if the script is running with root privileges."""
    if os.geteuid() != 0:
        logger.error("Root privileges required for installing/saving systemd services")
        logger.error("Please run with sudo: sudo python3 gensystemd.py ...")
        return False
    return True

def save_service_file(service_path, content):
    """Save the service file to the systemd directory."""
    try:
        logger.info(f"Saving service file to {service_path}")
        
        # Create directory if it doesn't exist (shouldn't be needed for /etc/systemd/system)
        service_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the service file
        with open(service_path, 'w') as f:
            f.write(content)
        
        # Set appropriate permissions
        os.chmod(service_path, 0o644)
        
        logger.info(f"Service file saved successfully to {service_path}")
        return True
        
    except PermissionError:
        logger.error(f"Permission denied when writing to {service_path}")
        logger.error("Make sure you're running with sudo privileges")
        return False
    except Exception as e:
        logger.error(f"Error saving service file: {e}")
        return False

def run_systemctl_command(command, service_name=None):
    """Run a systemctl command and log the results."""
    full_command = ['systemctl'] + command
    if service_name:
        full_command.append(service_name)
    
    logger.info(f"Executing: {' '.join(full_command)}")
    
    try:
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stdout.strip():
            logger.info(f"Command output: {result.stdout.strip()}")
        logger.info(f"Command completed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with return code {e.returncode}")
        if e.stdout:
            logger.error(f"stdout: {e.stdout}")
        if e.stderr:
            logger.error(f"stderr: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Error running systemctl command: {e}")
        return False

def install_service(service_name, content):
    """Install the systemd service (save + reload + enable)."""
    logger.info(f"Installing systemd service '{service_name}'")
    
    if not check_root_privileges():
        return False
    
    service_path = get_service_path(service_name)
    
    # Save the service file
    if not save_service_file(service_path, content):
        return False
    
    # Reload systemd daemon
    logger.info("Reloading systemd daemon...")
    if not run_systemctl_command(['daemon-reload']):
        logger.error("Failed to reload systemd daemon")
        return False
    
    # Enable the service
    logger.info(f"Enabling service '{service_name}' to start at boot...")
    if not run_systemctl_command(['enable'], service_name):
        logger.error(f"Failed to enable service '{service_name}'")
        return False
    
    logger.info(f"Service '{service_name}' installed and enabled successfully!")
    logger.info(f"You can now start it with: sudo systemctl start {service_name}")
    logger.info(f"Check status with: sudo systemctl status {service_name}")
    
    return True

def save_only_service(service_name, content):
    """Save the service file without reloading daemon or enabling."""
    logger.info(f"Saving systemd service '{service_name}' (without daemon reload)")
    
    if not check_root_privileges():
        return False
    
    service_path = get_service_path(service_name)
    
    if save_service_file(service_path, content):
        logger.info(f"Service '{service_name}' saved successfully!")
        logger.info("To complete installation, run:")
        logger.info("  sudo systemctl daemon-reload")
        logger.info(f"  sudo systemctl enable {service_name}")
        logger.info(f"  sudo systemctl start {service_name}")
        return True
    
    return False

def main():
    parser = argparse.ArgumentParser(
        description='Generate and install systemd services',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 gensystemd.py "my-app" "python3 /opt/myapp/app.py"
  python3 gensystemd.py "backup-service" "/usr/local/bin/backup.sh" --install
  python3 gensystemd.py "web-server" "cd /var/www && python3 -m http.server 8080" --save
        """
    )
    
    parser.add_argument('name', help='Name of the systemd service')
    parser.add_argument('command', help='Command to run (shell command)')
    parser.add_argument('--install', action='store_true',
                       help='Install the service (save + reload daemon + enable)')
    parser.add_argument('--save', action='store_true',
                       help='Save the service file only (no daemon reload)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Adjust logging level if verbose
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    
    # Validate arguments
    if args.install and args.save:
        logger.error("Cannot use both --install and --save flags together")
        return 1
    
    logger.info(f"Starting systemd service generation for '{args.name}'")
    logger.info(f"Command: {args.command}")
    
    # Generate service content
    try:
        service_content = generate_service_content(args.name, args.command)
    except Exception as e:
        logger.error(f"Error generating service content: {e}")
        return 1
    
    # Handle different modes
    if args.install:
        success = install_service(args.name, service_content)
        return 0 if success else 1
    
    elif args.save:
        success = save_only_service(args.name, service_content)
        return 0 if success else 1
    
    else:
        # Default: output to stdout
        logger.info("Outputting service content to stdout")
        print(service_content)
        logger.info("Service content generated successfully. Use --install or --save to write to system.")
        return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
