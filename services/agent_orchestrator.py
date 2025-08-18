"""
Agent Orchestrator for CraftNudge Git Commit Logger.
Manages Code Llama and Ollama agents for processing commits and code analysis.
"""

import requests
import json
import subprocess
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import os
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.database_service import DatabaseService
from utils.error_handler import DataStorageError


class AgentOrchestrator:
    """Orchestrates Code Llama and Ollama agents for commit processing."""
    
    def __init__(self, database_service: DatabaseService = None, 
                 ollama_base_url: str = "http://localhost:11434",
                 code_llama_model: str = "codellama:7b",
                 ollama_model: str = "llama2:7b"):
        """Initialize agent orchestrator."""
        self.db = database_service or DatabaseService()
        self.ollama_base_url = ollama_base_url
        self.code_llama_model = code_llama_model
        self.ollama_model = ollama_model
        
        # Initialize agent configurations
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize agent configurations in database."""
        try:
            # Code Llama configuration
            code_llama_config = {
                'base_url': self.ollama_base_url,
                'model': self.code_llama_model,
                'temperature': 0.1,
                'max_tokens': 2048,
                'system_prompt': """You are a code analysis agent. Analyze the provided code changes and provide insights about:
1. Code quality and best practices
2. Potential bugs or issues
3. Security concerns
4. Performance implications
5. Suggestions for improvement

Provide clear, actionable feedback."""
            }
            
            self.db.save_agent_config(
                agent_name='code_llama_analyzer',
                agent_type='code_analysis',
                model_name=self.code_llama_model,
                configuration=code_llama_config
            )
            
            # Ollama configuration
            ollama_config = {
                'base_url': self.ollama_base_url,
                'model': self.ollama_model,
                'temperature': 0.2,
                'max_tokens': 1024,
                'system_prompt': """You are a commit analysis agent. Analyze commit messages and changes to provide insights about:
1. Commit message quality
2. Change impact assessment
3. Development patterns
4. Team collaboration insights
5. Project health indicators

Provide concise, valuable feedback."""
            }
            
            self.db.save_agent_config(
                agent_name='ollama_commit_analyzer',
                agent_type='commit_analysis',
                model_name=self.ollama_model,
                configuration=ollama_config
            )
            
        except Exception as e:
            print(f"Warning: Failed to initialize agent configurations: {str(e)}")
    
    def check_ollama_status(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def ensure_model_available(self, model_name: str) -> bool:
        """Ensure the specified model is available in Ollama."""
        try:
            # Check if model exists
            response = requests.get(f"{self.ollama_base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_exists = any(model['name'] == model_name for model in models)
                
                if not model_exists:
                    print(f"Model {model_name} not found, pulling...")
                    # Pull the model
                    pull_response = requests.post(f"{self.ollama_base_url}/api/pull", 
                                                json={'name': model_name})
                    if pull_response.status_code != 200:
                        print(f"Failed to pull model {model_name}")
                        return False
                
                return True
            return False
        except Exception as e:
            print(f"Error ensuring model availability: {str(e)}")
            return False
    
    def query_ollama(self, model: str, prompt: str, system_prompt: str = None) -> str:
        """Query Ollama with a prompt."""
        try:
            payload = {
                'model': model,
                'prompt': prompt,
                'stream': False
            }
            
            if system_prompt:
                payload['system'] = system_prompt
            
            response = requests.post(f"{self.ollama_base_url}/api/generate", 
                                   json=payload, timeout=60)
            
            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                raise Exception(f"Ollama API error: {response.status_code}")
                
        except Exception as e:
            raise DataStorageError(f"Failed to query Ollama: {str(e)}")
    
    def analyze_commit_with_code_llama(self, commit_data: Dict[str, Any], 
                                     changed_files: List[str]) -> Dict[str, Any]:
        """Analyze commit using Code Llama for code quality insights."""
        try:
            if not self.check_ollama_status():
                raise DataStorageError("Ollama is not running")
            
            if not self.ensure_model_available(self.code_llama_model):
                raise DataStorageError(f"Code Llama model {self.code_llama_model} not available")
            
            # Get agent configuration
            config = self.db.get_agent_config('code_llama_analyzer')
            if not config:
                raise DataStorageError("Code Llama configuration not found")
            
            # Prepare analysis prompt
            prompt = f"""
Analyze the following commit and code changes:

Commit: {commit_data['commit_hash']}
Author: {commit_data['author']}
Message: {commit_data['message']}
Changed Files: {', '.join(changed_files)}

Please provide a comprehensive code analysis including:
1. Code quality assessment
2. Potential issues or bugs
3. Security considerations
4. Performance implications
5. Suggestions for improvement

Focus on the technical aspects and provide actionable feedback.
"""
            
            # Query Code Llama
            analysis = self.query_ollama(
                model=self.code_llama_model,
                prompt=prompt,
                system_prompt=config['configuration']['system_prompt']
            )
            
            return {
                'agent_type': 'code_llama',
                'analysis_type': 'code_quality',
                'analysis': analysis,
                'timestamp': datetime.now().isoformat(),
                'model_used': self.code_llama_model
            }
            
        except Exception as e:
            raise DataStorageError(f"Failed to analyze commit with Code Llama: {str(e)}")
    
    def analyze_commit_with_ollama(self, commit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze commit using Ollama for commit message and pattern insights."""
        try:
            if not self.check_ollama_status():
                raise DataStorageError("Ollama is not running")
            
            if not self.ensure_model_available(self.ollama_model):
                raise DataStorageError(f"Ollama model {self.ollama_model} not available")
            
            # Get agent configuration
            config = self.db.get_agent_config('ollama_commit_analyzer')
            if not config:
                raise DataStorageError("Ollama configuration not found")
            
            # Prepare analysis prompt
            prompt = f"""
Analyze the following commit:

Hash: {commit_data['commit_hash']}
Author: {commit_data['author']}
Message: {commit_data['message']}
Branch: {commit_data.get('branch', 'unknown')}
Timestamp: {commit_data['timestamp_commit']}
Changed Files: {len(commit_data.get('changed_files', []))} files

Please provide insights about:
1. Commit message quality and clarity
2. Change impact and scope
3. Development patterns and habits
4. Team collaboration indicators
5. Project health and progress

Provide concise, actionable feedback.
"""
            
            # Query Ollama
            analysis = self.query_ollama(
                model=self.ollama_model,
                prompt=prompt,
                system_prompt=config['configuration']['system_prompt']
            )
            
            return {
                'agent_type': 'ollama',
                'analysis_type': 'commit_patterns',
                'analysis': analysis,
                'timestamp': datetime.now().isoformat(),
                'model_used': self.ollama_model
            }
            
        except Exception as e:
            raise DataStorageError(f"Failed to analyze commit with Ollama: {str(e)}")
    
    def process_commit_with_agents(self, commit_id: int, commit_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process a commit with both Code Llama and Ollama agents."""
        try:
            results = []
            
            # Analyze with Code Llama
            try:
                code_analysis = self.analyze_commit_with_code_llama(
                    commit_data, 
                    commit_data.get('changed_files', [])
                )
                
                # Save interaction to database
                interaction_id = self.db.save_agent_interaction(
                    commit_id=commit_id,
                    agent_type='code_llama',
                    interaction_type='code_analysis',
                    input_data={'commit_data': commit_data},
                    output_data=code_analysis,
                    status='completed'
                )
                
                results.append({
                    'interaction_id': interaction_id,
                    'agent': 'code_llama',
                    'analysis': code_analysis
                })
                
            except Exception as e:
                print(f"Code Llama analysis failed: {str(e)}")
                # Save failed interaction
                self.db.save_agent_interaction(
                    commit_id=commit_id,
                    agent_type='code_llama',
                    interaction_type='code_analysis',
                    input_data={'commit_data': commit_data},
                    output_data={'error': str(e)},
                    status='failed'
                )
            
            # Analyze with Ollama
            try:
                commit_analysis = self.analyze_commit_with_ollama(commit_data)
                
                # Save interaction to database
                interaction_id = self.db.save_agent_interaction(
                    commit_id=commit_id,
                    agent_type='ollama',
                    interaction_type='commit_analysis',
                    input_data={'commit_data': commit_data},
                    output_data=commit_analysis,
                    status='completed'
                )
                
                results.append({
                    'interaction_id': interaction_id,
                    'agent': 'ollama',
                    'analysis': commit_analysis
                })
                
            except Exception as e:
                print(f"Ollama analysis failed: {str(e)}")
                # Save failed interaction
                self.db.save_agent_interaction(
                    commit_id=commit_id,
                    agent_type='ollama',
                    interaction_type='commit_analysis',
                    input_data={'commit_data': commit_data},
                    output_data={'error': str(e)},
                    status='failed'
                )
            
            return results
            
        except Exception as e:
            raise DataStorageError(f"Failed to process commit with agents: {str(e)}")
    
    def process_unanalyzed_commits(self) -> List[Dict[str, Any]]:
        """Process all commits that haven't been analyzed by agents yet."""
        try:
            # Get commits without agent interactions
            with self.db.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT c.* FROM commits c
                    LEFT JOIN agent_interactions ai ON c.id = ai.commit_id
                    WHERE ai.id IS NULL
                    ORDER BY c.timestamp_commit DESC
                """)
                
                unanalyzed_commits = cursor.fetchall()
            
            results = []
            for commit_row in unanalyzed_commits:
                try:
                    commit_data = {
                        'id': commit_row[0],
                        'commit_hash': commit_row[1],
                        'author': commit_row[2],
                        'message': commit_row[3],
                        'timestamp_commit': commit_row[4],
                        'branch': commit_row[6],
                        'repository_path': commit_row[7],
                        'changed_files': json.loads(commit_row[8]) if commit_row[8] else [],
                        'metadata': json.loads(commit_row[9]) if commit_row[9] else {}
                    }
                    
                    agent_results = self.process_commit_with_agents(
                        commit_data['id'], 
                        commit_data
                    )
                    
                    results.extend(agent_results)
                    
                except Exception as e:
                    print(f"Failed to process commit {commit_row[1]}: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            raise DataStorageError(f"Failed to process unanalyzed commits: {str(e)}")
    
    def get_agent_statistics(self) -> Dict[str, Any]:
        """Get agent processing statistics."""
        try:
            with self.db.conn.cursor() as cursor:
                # Total interactions
                cursor.execute("SELECT COUNT(*) FROM agent_interactions")
                total_interactions = cursor.fetchone()[0]
                
                # Interactions by agent type
                cursor.execute("""
                    SELECT agent_type, COUNT(*) as count 
                    FROM agent_interactions 
                    GROUP BY agent_type
                """)
                interactions_by_agent = dict(cursor.fetchall())
                
                # Success rate
                cursor.execute("""
                    SELECT status, COUNT(*) as count 
                    FROM agent_interactions 
                    GROUP BY status
                """)
                status_counts = dict(cursor.fetchall())
                
                # Recent activity
                cursor.execute("""
                    SELECT COUNT(*) as recent_interactions 
                    FROM agent_interactions 
                    WHERE timestamp > NOW() - INTERVAL '24 hours'
                """)
                recent_interactions = cursor.fetchone()[0]
            
            return {
                'total_interactions': total_interactions,
                'interactions_by_agent': interactions_by_agent,
                'status_counts': status_counts,
                'recent_interactions_24h': recent_interactions,
                'ollama_status': self.check_ollama_status()
            }
            
        except Exception as e:
            raise DataStorageError(f"Failed to get agent statistics: {str(e)}")
    
    def close(self):
        """Close database connection."""
        if self.db:
            self.db.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
