"""
Continuous Monitoring Service for CraftNudge Git Commit Logger.
Runs in the background to automatically process commits and webhook events.
"""

import time
import threading
import schedule
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import signal
import sys
from pathlib import Path
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.database_service import DatabaseService
from services.github_webhook_handler import GitHubWebhookHandler
from services.agent_orchestrator import AgentOrchestrator
from utils.error_handler import DataStorageError


class ContinuousMonitor:
    """Continuous monitoring service for automatic commit processing."""
    
    def __init__(self, 
                 database_service: DatabaseService = None,
                 webhook_handler: GitHubWebhookHandler = None,
                 agent_orchestrator: AgentOrchestrator = None,
                 check_interval: int = 30,
                 enable_agents: bool = True,
                 enable_webhooks: bool = True):
        """Initialize continuous monitor."""
        self.db = database_service or DatabaseService()
        self.webhook_handler = webhook_handler or GitHubWebhookHandler(database_service=self.db)
        self.agent_orchestrator = agent_orchestrator or AgentOrchestrator(database_service=self.db)
        
        self.check_interval = check_interval
        self.enable_agents = enable_agents
        self.enable_webhooks = enable_webhooks
        
        self.running = False
        self.monitor_thread = None
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('continuous_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('ContinuousMonitor')
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
        sys.exit(0)
    
    def process_webhook_events(self) -> Dict[str, Any]:
        """Process any unprocessed webhook events."""
        try:
            if not self.enable_webhooks:
                return {'status': 'disabled', 'processed': 0}
            
            self.logger.info("Processing unprocessed webhook events...")
            
            # Process unprocessed events
            results = self.webhook_handler.process_unprocessed_events()
            
            if results:
                self.logger.info(f"Processed {len(results)} webhook events")
                
                # Trigger agent processing for new commits
                if self.enable_agents:
                    self._trigger_agent_processing()
            
            return {
                'status': 'success',
                'processed': len(results),
                'results': results
            }
            
        except Exception as e:
            self.logger.error(f"Failed to process webhook events: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'processed': 0
            }
    
    def process_agent_analysis(self) -> Dict[str, Any]:
        """Process commits with AI agents."""
        try:
            if not self.enable_agents:
                return {'status': 'disabled', 'processed': 0}
            
            self.logger.info("Processing commits with AI agents...")
            
            # Process unanalyzed commits
            results = self.agent_orchestrator.process_unanalyzed_commits()
            
            if results:
                self.logger.info(f"Processed {len(results)} commits with agents")
            
            return {
                'status': 'success',
                'processed': len(results),
                'results': results
            }
            
        except Exception as e:
            self.logger.error(f"Failed to process agent analysis: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'processed': 0
            }
    
    def _trigger_agent_processing(self):
        """Trigger agent processing for new commits."""
        try:
            # Get recent commits that haven't been analyzed
            with self.db.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT c.id, c.commit_hash FROM commits c
                    LEFT JOIN agent_interactions ai ON c.id = ai.commit_id
                    WHERE ai.id IS NULL
                    AND c.timestamp_logged > NOW() - INTERVAL '1 hour'
                    ORDER BY c.timestamp_logged DESC
                """)
                
                recent_unanalyzed = cursor.fetchall()
            
            if recent_unanalyzed:
                self.logger.info(f"Found {len(recent_unanalyzed)} recent commits for agent analysis")
                # Process them in a separate thread to avoid blocking
                threading.Thread(target=self.process_agent_analysis, daemon=True).start()
                
        except Exception as e:
            self.logger.error(f"Failed to trigger agent processing: {str(e)}")
    
    def check_system_health(self) -> Dict[str, Any]:
        """Check system health and status."""
        try:
            health_status = {
                'timestamp': datetime.now().isoformat(),
                'database': 'healthy',
                'webhook_handler': 'healthy',
                'agent_orchestrator': 'healthy',
                'ollama_status': 'unknown'
            }
            
            # Check database connection
            try:
                stats = self.db.get_statistics()
                health_status['database_stats'] = stats
            except Exception as e:
                health_status['database'] = f'error: {str(e)}'
            
            # Check webhook handler
            try:
                webhook_stats = self.webhook_handler.get_webhook_statistics()
                health_status['webhook_stats'] = webhook_stats
            except Exception as e:
                health_status['webhook_handler'] = f'error: {str(e)}'
            
            # Check agent orchestrator
            try:
                agent_stats = self.agent_orchestrator.get_agent_statistics()
                health_status['agent_stats'] = agent_stats
                health_status['ollama_status'] = 'running' if agent_stats.get('ollama_status') else 'stopped'
            except Exception as e:
                health_status['agent_orchestrator'] = f'error: {str(e)}'
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Failed to check system health: {str(e)}")
            return {
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error': str(e)
            }
    
    def monitor_cycle(self):
        """Single monitoring cycle."""
        try:
            self.logger.debug("Starting monitoring cycle...")
            
            # Process webhook events
            webhook_result = self.process_webhook_events()
            
            # Process agent analysis
            agent_result = self.process_agent_analysis()
            
            # Log results
            if webhook_result['processed'] > 0 or agent_result['processed'] > 0:
                self.logger.info(f"Cycle completed: {webhook_result['processed']} webhook events, {agent_result['processed']} agent analyses")
            
        except Exception as e:
            self.logger.error(f"Error in monitoring cycle: {str(e)}")
    
    def start(self):
        """Start the continuous monitoring service."""
        if self.running:
            self.logger.warning("Monitor is already running")
            return
        
        self.running = True
        self.logger.info("Starting continuous monitoring service...")
        
        # Schedule monitoring tasks
        schedule.every(self.check_interval).seconds.do(self.monitor_cycle)
        schedule.every().hour.do(self.check_system_health)
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info(f"Continuous monitor started (check interval: {self.check_interval}s)")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Error in monitor loop: {str(e)}")
                time.sleep(5)  # Wait before retrying
    
    def stop(self):
        """Stop the continuous monitoring service."""
        if not self.running:
            return
        
        self.logger.info("Stopping continuous monitoring service...")
        self.running = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        # Close database connections
        try:
            self.db.close()
            self.webhook_handler.close()
            self.agent_orchestrator.close()
        except Exception as e:
            self.logger.error(f"Error closing connections: {str(e)}")
        
        self.logger.info("Continuous monitor stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current monitor status."""
        return {
            'running': self.running,
            'check_interval': self.check_interval,
            'enable_agents': self.enable_agents,
            'enable_webhooks': self.enable_webhooks,
            'health': self.check_system_health()
        }
    
    def run_once(self) -> Dict[str, Any]:
        """Run a single monitoring cycle and return results."""
        try:
            self.logger.info("Running single monitoring cycle...")
            
            webhook_result = self.process_webhook_events()
            agent_result = self.process_agent_analysis()
            health_status = self.check_system_health()
            
            return {
                'webhook_processing': webhook_result,
                'agent_processing': agent_result,
                'health_status': health_status,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in single run: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


def main():
    """Main function to run the continuous monitor."""
    import argparse
    
    parser = argparse.ArgumentParser(description='CraftNudge Continuous Monitor')
    parser.add_argument('--interval', type=int, default=30, 
                       help='Check interval in seconds (default: 30)')
    parser.add_argument('--no-agents', action='store_true',
                       help='Disable AI agent processing')
    parser.add_argument('--no-webhooks', action='store_true',
                       help='Disable webhook processing')
    parser.add_argument('--once', action='store_true',
                       help='Run once and exit')
    parser.add_argument('--health', action='store_true',
                       help='Check system health and exit')
    
    args = parser.parse_args()
    
    # Create monitor
    monitor = ContinuousMonitor(
        check_interval=args.interval,
        enable_agents=not args.no_agents,
        enable_webhooks=not args.no_webhooks
    )
    
    try:
        if args.health:
            # Just check health
            health = monitor.check_system_health()
            print(json.dumps(health, indent=2))
        elif args.once:
            # Run once
            result = monitor.run_once()
            print(json.dumps(result, indent=2))
        else:
            # Run continuously
            monitor.start()
            
            # Keep main thread alive
            try:
                while monitor.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nShutting down...")
                monitor.stop()
                
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
