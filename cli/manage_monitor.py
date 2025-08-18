#!/usr/bin/env python3
"""
CraftNudge Continuous Monitor Management CLI.
Provides commands to manage the continuous monitoring system.
"""

import click
import json
import time
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import requests

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.continuous_monitor import ContinuousMonitor
from services.database_service import DatabaseService
from services.github_webhook_handler import GitHubWebhookHandler
from services.agent_orchestrator import AgentOrchestrator
from utils.error_handler import DataStorageError


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """CraftNudge Continuous Monitor Management CLI."""
    pass


@cli.command()
@click.option('--interval', default=30, help='Check interval in seconds (default: 30)')
@click.option('--no-agents', is_flag=True, help='Disable AI agent processing')
@click.option('--no-webhooks', is_flag=True, help='Disable webhook processing')
@click.option('--daemon', is_flag=True, help='Run as daemon process')
def start(interval, no_agents, no_webhooks, daemon):
    """Start the continuous monitoring service."""
    try:
        click.echo("Starting CraftNudge Continuous Monitor...")
        
        if daemon:
            # Run as daemon
            cmd = [
                sys.executable, '-m', 'services.continuous_monitor',
                '--interval', str(interval)
            ]
            if no_agents:
                cmd.append('--no-agents')
            if no_webhooks:
                cmd.append('--no-webhooks')
            
            # Start daemon process
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            click.echo(f"Monitor started as daemon (PID: {process.pid})")
            click.echo(f"Logs: continuous_monitor.log")
        else:
            # Run in foreground
            monitor = ContinuousMonitor(
                check_interval=interval,
                enable_agents=not no_agents,
                enable_webhooks=not no_webhooks
            )
            
            with monitor:
                click.echo(f"Monitor started (check interval: {interval}s)")
                click.echo("Press Ctrl+C to stop...")
                
                try:
                    while monitor.running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    click.echo("\nStopping monitor...")
                    monitor.stop()
        
    except Exception as e:
        click.echo(f"Error starting monitor: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def stop():
    """Stop the continuous monitoring service."""
    try:
        # Try to find and stop the daemon process
        result = subprocess.run(['pgrep', '-f', 'continuous_monitor'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    subprocess.run(['kill', pid])
                    click.echo(f"Stopped monitor process (PID: {pid})")
        else:
            click.echo("No monitor process found")
            
    except Exception as e:
        click.echo(f"Error stopping monitor: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def status():
    """Show the status of the continuous monitoring service."""
    try:
        # Check if monitor is running
        result = subprocess.run(['pgrep', '-f', 'continuous_monitor'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            click.echo(f"✅ Monitor is running (PIDs: {', '.join(pids)})")
        else:
            click.echo("❌ Monitor is not running")
        
        # Check system health
        monitor = ContinuousMonitor()
        health = monitor.check_system_health()
        
        click.echo("\n📊 System Health:")
        click.echo(f"  Database: {health.get('database', 'unknown')}")
        click.echo(f"  Webhook Handler: {health.get('webhook_handler', 'unknown')}")
        click.echo(f"  Agent Orchestrator: {health.get('agent_orchestrator', 'unknown')}")
        click.echo(f"  Ollama Status: {health.get('ollama_status', 'unknown')}")
        
        # Show statistics
        if 'database_stats' in health:
            stats = health['database_stats']
            click.echo(f"\n📈 Statistics:")
            click.echo(f"  Total Commits: {stats.get('total_commits', 0)}")
            click.echo(f"  Unique Authors: {stats.get('unique_authors', 0)}")
            click.echo(f"  Total Interactions: {stats.get('total_interactions', 0)}")
            click.echo(f"  Unprocessed Events: {stats.get('unprocessed_events', 0)}")
        
    except Exception as e:
        click.echo(f"Error getting status: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def health():
    """Check system health and show detailed status."""
    try:
        monitor = ContinuousMonitor()
        health_data = monitor.check_system_health()
        
        click.echo("🏥 System Health Check")
        click.echo("=" * 50)
        
        # Overall status
        overall_status = "✅ Healthy"
        if any('error' in str(v) for v in health_data.values()):
            overall_status = "❌ Unhealthy"
        
        click.echo(f"Overall Status: {overall_status}")
        click.echo(f"Timestamp: {health_data.get('timestamp', 'unknown')}")
        
        # Component status
        click.echo(f"\n📋 Component Status:")
        click.echo(f"  Database: {health_data.get('database', 'unknown')}")
        click.echo(f"  Webhook Handler: {health_data.get('webhook_handler', 'unknown')}")
        click.echo(f"  Agent Orchestrator: {health_data.get('agent_orchestrator', 'unknown')}")
        click.echo(f"  Ollama: {health_data.get('ollama_status', 'unknown')}")
        
        # Detailed statistics
        if 'database_stats' in health_data:
            click.echo(f"\n💾 Database Statistics:")
            stats = health_data['database_stats']
            for key, value in stats.items():
                click.echo(f"  {key.replace('_', ' ').title()}: {value}")
        
        if 'webhook_stats' in health_data:
            click.echo(f"\n🔗 Webhook Statistics:")
            webhook_stats = health_data['webhook_stats']
            for key, value in webhook_stats.items():
                if key not in ['total_commits', 'unique_authors', 'total_interactions', 'unprocessed_events']:
                    click.echo(f"  {key.replace('_', ' ').title()}: {value}")
        
        if 'agent_stats' in health_data:
            click.echo(f"\n🤖 Agent Statistics:")
            agent_stats = health_data['agent_stats']
            for key, value in agent_stats.items():
                click.echo(f"  {key.replace('_', ' ').title()}: {value}")
        
    except Exception as e:
        click.echo(f"Error checking health: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def run_once():
    """Run a single monitoring cycle."""
    try:
        click.echo("Running single monitoring cycle...")
        
        monitor = ContinuousMonitor()
        result = monitor.run_once()
        
        click.echo("✅ Cycle completed")
        click.echo(f"Webhook Processing: {result.get('webhook_processing', {}).get('processed', 0)} events")
        click.echo(f"Agent Processing: {result.get('agent_processing', {}).get('processed', 0)} analyses")
        
        if result.get('health_status'):
            health = result['health_status']
            click.echo(f"System Status: {health.get('database', 'unknown')}")
        
    except Exception as e:
        click.echo(f"Error running cycle: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--host', default='localhost', help='Webhook server host')
@click.option('--port', default=5000, help='Webhook server port')
def webhook_status(host, port):
    """Check webhook server status."""
    try:
        url = f"http://{host}:{port}/health"
        
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                click.echo("✅ Webhook server is running")
                click.echo(f"Status: {data.get('status', 'unknown')}")
                
                if 'statistics' in data:
                    stats = data['statistics']
                    if 'database' in stats:
                        db_stats = stats['database']
                        click.echo(f"Database Commits: {db_stats.get('total_commits', 0)}")
                    if 'webhook' in stats:
                        webhook_stats = stats['webhook']
                        click.echo(f"Webhook Events: {webhook_stats.get('total_webhook_events', 0)}")
            else:
                click.echo(f"❌ Webhook server error: {response.status_code}")
        except requests.exceptions.RequestException:
            click.echo("❌ Webhook server is not accessible")
            
    except Exception as e:
        click.echo(f"Error checking webhook status: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--host', default='localhost', help='Webhook server host')
@click.option('--port', default=5000, help='Webhook server port')
def start_webhook_server(host, port):
    """Start the webhook server."""
    try:
        click.echo(f"Starting webhook server on {host}:{port}...")
        
        cmd = [sys.executable, 'webhook_server.py', '--host', host, '--port', str(port)]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        click.echo(f"✅ Webhook server started (PID: {process.pid})")
        click.echo(f"URL: http://{host}:{port}")
        click.echo(f"Webhook endpoint: http://{host}:{port}/webhook/github")
        
    except Exception as e:
        click.echo(f"Error starting webhook server: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--limit', default=10, help='Number of recent commits to show')
def recent_commits(limit):
    """Show recent commits from the database."""
    try:
        db = DatabaseService()
        commits = db.get_recent_commits(limit)
        
        if not commits:
            click.echo("No commits found in database")
            return
        
        click.echo(f"📝 Recent Commits (showing {len(commits)}):")
        click.echo("=" * 80)
        
        for commit in commits:
            click.echo(f"Hash: {commit['commit_hash'][:8]}...")
            click.echo(f"Author: {commit['author']}")
            click.echo(f"Message: {commit['message'][:60]}{'...' if len(commit['message']) > 60 else ''}")
            click.echo(f"Branch: {commit.get('branch', 'unknown')}")
            click.echo(f"Timestamp: {commit['timestamp_commit']}")
            click.echo("-" * 40)
        
    except Exception as e:
        click.echo(f"Error getting recent commits: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def setup():
    """Setup the continuous monitoring system."""
    try:
        click.echo("🔧 Setting up CraftNudge Continuous Monitor...")
        
        # Initialize database
        click.echo("  Initializing database...")
        db = DatabaseService()
        stats = db.get_statistics()
        click.echo(f"  ✅ Database initialized ({stats.get('total_commits', 0)} commits)")
        
        # Initialize webhook handler
        click.echo("  Initializing webhook handler...")
        webhook_handler = GitHubWebhookHandler(database_service=db)
        click.echo("  ✅ Webhook handler initialized")
        
        # Initialize agent orchestrator
        click.echo("  Initializing agent orchestrator...")
        agent_orchestrator = AgentOrchestrator(database_service=db)
        
        # Check Ollama status
        if agent_orchestrator.check_ollama_status():
            click.echo("  ✅ Ollama is running")
        else:
            click.echo("  ⚠️  Ollama is not running (agent processing will be disabled)")
        
        click.echo("  ✅ Agent orchestrator initialized")
        
        # Show final status
        click.echo("\n🎉 Setup completed successfully!")
        click.echo("\nNext steps:")
        click.echo("  1. Start the monitor: craftnudge monitor start")
        click.echo("  2. Start webhook server: craftnudge monitor start-webhook-server")
        click.echo("  3. Check status: craftnudge monitor status")
        
    except Exception as e:
        click.echo(f"Error during setup: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
