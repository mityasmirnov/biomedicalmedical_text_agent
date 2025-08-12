"""
Prompt Optimization Module for Biomedical Text Agent

This module implements prompt optimization using contextual bandit algorithms
and stores multiple prompt variants for each agent. It includes few-shot
example management and automatic prompt selection based on performance feedback.

Location: src/core/prompt_optimization.py
"""

import json
import logging
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import numpy as np
from datetime import datetime
import random
from collections import defaultdict


@dataclass
class PromptVariant:
    """Represents a prompt variant with its performance metrics."""
    prompt_id: str
    agent_type: str
    field_name: str
    system_prompt: str
    user_prompt_template: str
    few_shot_examples: List[Dict[str, Any]]
    performance_score: float
    usage_count: int
    success_count: int
    created_at: str
    last_used: Optional[str] = None
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FewShotExample:
    """Represents a few-shot example for prompt enhancement."""
    example_id: str
    agent_type: str
    field_name: str
    input_text: str
    expected_output: Dict[str, Any]
    context: str
    quality_score: float
    usage_count: int
    created_at: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ContextualBandit:
    """
    Contextual bandit algorithm for prompt selection.
    Uses Upper Confidence Bound (UCB) with context features.
    """
    
    def __init__(self, exploration_factor: float = 2.0):
        """
        Initialize contextual bandit.
        
        Args:
            exploration_factor: Controls exploration vs exploitation trade-off
        """
        self.exploration_factor = exploration_factor
        self.arm_rewards: Dict[str, List[float]] = defaultdict(list)
        self.arm_contexts: Dict[str, List[List[float]]] = defaultdict(list)
    
    def select_prompt(self, 
                     available_prompts: List[PromptVariant], 
                     context_features: List[float]) -> PromptVariant:
        """
        Select the best prompt variant using UCB algorithm.
        
        Args:
            available_prompts: List of available prompt variants
            context_features: Context features for the current task
            
        Returns:
            Selected prompt variant
        """
        if not available_prompts:
            raise ValueError("No available prompts")
        
        if len(available_prompts) == 1:
            return available_prompts[0]
        
        # Calculate UCB scores for each prompt
        ucb_scores = []
        total_plays = sum(prompt.usage_count for prompt in available_prompts)
        
        for prompt in available_prompts:
            if prompt.usage_count == 0:
                # Unplayed arms get highest priority
                ucb_scores.append(float('inf'))
            else:
                # Calculate mean reward
                mean_reward = prompt.performance_score
                
                # Calculate confidence interval
                confidence = self.exploration_factor * np.sqrt(
                    np.log(total_plays) / prompt.usage_count
                )
                
                # Add context similarity bonus
                context_bonus = self._calculate_context_bonus(
                    prompt.prompt_id, context_features
                )
                
                ucb_score = mean_reward + confidence + context_bonus
                ucb_scores.append(ucb_score)
        
        # Select prompt with highest UCB score
        best_idx = np.argmax(ucb_scores)
        return available_prompts[best_idx]
    
    def update_reward(self, 
                     prompt_id: str, 
                     reward: float, 
                     context_features: List[float]):
        """
        Update the reward for a prompt variant.
        
        Args:
            prompt_id: ID of the prompt variant
            reward: Reward value (0.0 to 1.0)
            context_features: Context features used
        """
        self.arm_rewards[prompt_id].append(reward)
        self.arm_contexts[prompt_id].append(context_features)
    
    def _calculate_context_bonus(self, 
                               prompt_id: str, 
                               current_context: List[float]) -> float:
        """Calculate context similarity bonus."""
        if prompt_id not in self.arm_contexts or not self.arm_contexts[prompt_id]:
            return 0.0
        
        # Calculate average similarity with previous contexts
        similarities = []
        for past_context in self.arm_contexts[prompt_id]:
            similarity = self._cosine_similarity(current_context, past_context)
            similarities.append(similarity)
        
        # Return average similarity as bonus
        return np.mean(similarities) * 0.1  # Small bonus factor


    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = np.sqrt(sum(a * a for a in vec1))
        norm2 = np.sqrt(sum(b * b for b in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)


class PromptOptimizer:
    """
    Main prompt optimization system that manages prompt variants,
    few-shot examples, and performance tracking.
    """
    
    def __init__(self, storage_path: str = "data/prompt_optimization"):
        """
        Initialize prompt optimizer.
        
        Args:
            storage_path: Path to store optimization data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Database for storing prompt data
        self.db_path = self.storage_path / "prompts.db"
        self._init_database()
        
        # Contextual bandit for prompt selection
        self.bandit = ContextualBandit()
        
        # Load existing data
        self._load_bandit_data()
        
        # Default prompt templates
        self._init_default_prompts()
    
    def _init_database(self):
        """Initialize SQLite database for prompt storage."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Prompt variants table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prompt_variants (
                    prompt_id TEXT PRIMARY KEY,
                    agent_type TEXT NOT NULL,
                    field_name TEXT NOT NULL,
                    system_prompt TEXT NOT NULL,
                    user_prompt_template TEXT NOT NULL,
                    few_shot_examples TEXT,
                    performance_score REAL DEFAULT 0.0,
                    usage_count INTEGER DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    last_used TEXT,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Few-shot examples table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS few_shot_examples (
                    example_id TEXT PRIMARY KEY,
                    agent_type TEXT NOT NULL,
                    field_name TEXT NOT NULL,
                    input_text TEXT NOT NULL,
                    expected_output TEXT NOT NULL,
                    context TEXT,
                    quality_score REAL DEFAULT 1.0,
                    usage_count INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Performance tracking table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prompt_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_id TEXT NOT NULL,
                    context_features TEXT,
                    reward REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (prompt_id) REFERENCES prompt_variants (prompt_id)
                )
            """)
            
            # Create indices
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_field ON prompt_variants(agent_type, field_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_performance_prompt ON prompt_performance(prompt_id)")
            
            conn.commit()
    
    def _load_bandit_data(self):
        """Load historical performance data for the bandit algorithm."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT prompt_id, context_features, reward 
                FROM prompt_performance 
                ORDER BY timestamp
            """)
            
            for prompt_id, context_features_json, reward in cursor.fetchall():
                try:
                    context_features = json.loads(context_features_json)
                    self.bandit.update_reward(prompt_id, reward, context_features)
                except json.JSONDecodeError:
                    continue
    
    def _init_default_prompts(self):
        """Initialize default prompt variants for each agent type."""
        default_prompts = {
            'demographics': {
                'basic': {
                    'system_prompt': """You are a biomedical information extraction agent specialized in extracting demographic information from patient case descriptions. Extract only the information that is explicitly stated in the text.""",
                    'user_prompt_template': """Extract demographic information from this patient case:

{patient_text}

Return a JSON object with these fields:
- sex: 1 for male, 0 for female, null if not specified
- age_of_onset: age when symptoms first appeared (in years)
- age_at_diagnosis: age when diagnosis was made (in years)
- ethnicity: patient's ethnic background if mentioned
- consanguinity: 1 if parents are related, 0 if not, null if not mentioned

Only include information that is explicitly stated. Use null for missing information."""
                },
                'detailed': {
                    'system_prompt': """You are an expert biomedical information extraction agent. Your task is to carefully extract demographic information from patient case descriptions. Pay attention to context clues and medical terminology. Be precise and conservative in your extractions.""",
                    'user_prompt_template': """Analyze this patient case and extract demographic information:

{patient_text}

Instructions:
1. Look for explicit mentions of sex/gender
2. Distinguish between age of onset and age at diagnosis
3. Note any ethnic or geographic background information
4. Check for family history indicating consanguinity

Return JSON with:
- sex: 1 (male), 0 (female), null (not specified)
- age_of_onset: numeric age in years when symptoms started
- age_at_diagnosis: numeric age in years when diagnosed
- ethnicity: ethnic/geographic background as stated
- consanguinity: 1 (consanguineous), 0 (non-consanguineous), null (unknown)"""
                }
            },
            'genetics': {
                'basic': {
                    'system_prompt': """You are a genetics information extraction agent. Extract genetic information including genes, mutations, and inheritance patterns from patient case descriptions.""",
                    'user_prompt_template': """Extract genetic information from this patient case:

{patient_text}

Return JSON with:
- gene: gene symbol (e.g., SURF1, NDUFS1)
- mutations: specific mutation notation
- inheritance: inheritance pattern (autosomal recessive, autosomal dominant, X-linked, etc.)
- zygosity: homozygous, heterozygous, compound heterozygous, or null
- genetic_testing: type of genetic testing performed

Use null for any field not explicitly mentioned."""
                },
                'hgvs_focused': {
                    'system_prompt': """You are a specialized genetics extraction agent with expertise in HGVS nomenclature and genetic terminology. Extract genetic information with attention to proper gene symbols and mutation notation.""",
                    'user_prompt_template': """Extract genetic information from this patient case, paying special attention to gene nomenclature and mutation notation:

{patient_text}

Guidelines:
- Use official gene symbols (HGNC approved)
- Preserve HGVS notation for mutations when available
- Identify inheritance patterns from family history
- Note zygosity information when provided

Return JSON with:
- gene: official gene symbol
- mutations: mutation in HGVS format if available, otherwise as stated
- inheritance: inheritance pattern from family history
- zygosity: homozygous/heterozygous/compound heterozygous
- genetic_testing: testing method (WES, WGS, Sanger, etc.)"""
                }
            },
            'phenotypes': {
                'basic': {
                    'system_prompt': """You are a phenotype extraction agent. Extract clinical phenotypes, symptoms, and diagnostic findings from patient case descriptions.""",
                    'user_prompt_template': """Extract phenotypic information from this patient case:

{patient_text}

Return JSON with:
- phenotypes: list of clinical phenotypes/features
- symptoms: list of symptoms reported
- diagnostic_findings: diagnostic test results or findings
- lab_values: laboratory test results if mentioned

Focus on medical terminology and clinical observations."""
                },
                'hpo_focused': {
                    'system_prompt': """You are a clinical phenotype extraction agent with expertise in HPO (Human Phenotype Ontology) terminology. Extract phenotypes using precise medical terminology that can be mapped to HPO terms.""",
                    'user_prompt_template': """Extract clinical phenotypes from this patient case, using precise medical terminology:

{patient_text}

Guidelines:
- Use standard medical terminology for phenotypes
- Separate symptoms from objective findings
- Include developmental and neurological features
- Note any imaging or laboratory abnormalities

Return JSON with:
- phenotypes: list of clinical phenotypes (use medical terms)
- symptoms: subjective symptoms reported
- diagnostic_findings: objective clinical findings
- lab_values: laboratory abnormalities with values if given"""
                }
            },
            'treatments': {
                'basic': {
                    'system_prompt': """You are a treatment extraction agent. Extract information about treatments, medications, and patient outcomes from case descriptions.""",
                    'user_prompt_template': """Extract treatment information from this patient case:

{patient_text}

Return JSON with:
- treatment_description: description of treatments given
- medications: list of medications with dosages if mentioned
- treatment_response: patient's response to treatment
- outcome: overall clinical outcome or current status"""
                },
                'detailed': {
                    'system_prompt': """You are a comprehensive treatment and outcome extraction agent. Extract detailed information about therapeutic interventions, medication regimens, and patient outcomes including survival data.""",
                    'user_prompt_template': """Extract comprehensive treatment and outcome information:

{patient_text}

Focus on:
- Specific medications and dosages
- Non-pharmacological interventions
- Treatment response and efficacy
- Survival outcomes and follow-up data
- Adverse effects if mentioned

Return JSON with:
- treatment_description: detailed treatment description
- medications: list of medications with dosages
- treatment_response: response to treatment
- outcome: clinical outcome and survival status"""
                }
            }
        }
        
        # Add default prompts to database if they don't exist
        for agent_type, variants in default_prompts.items():
            for variant_name, prompt_data in variants.items():
                prompt_id = f"{agent_type}_{variant_name}_default"
                
                if not self._prompt_exists(prompt_id):
                    self.add_prompt_variant(
                        prompt_id=prompt_id,
                        agent_type=agent_type,
                        field_name="all",
                        system_prompt=prompt_data['system_prompt'],
                        user_prompt_template=prompt_data['user_prompt_template']
                    )
    
    def _prompt_exists(self, prompt_id: str) -> bool:
        """Check if a prompt variant exists in the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM prompt_variants WHERE prompt_id = ?", (prompt_id,))
            return cursor.fetchone() is not None
    
    def add_prompt_variant(self, 
                          prompt_id: str,
                          agent_type: str,
                          field_name: str,
                          system_prompt: str,
                          user_prompt_template: str,
                          few_shot_examples: Optional[List[Dict[str, Any]]] = None) -> bool:
        """
        Add a new prompt variant.
        
        Args:
            prompt_id: Unique identifier for the prompt
            agent_type: Type of agent (demographics, genetics, etc.)
            field_name: Specific field or "all" for general prompts
            system_prompt: System prompt text
            user_prompt_template: User prompt template with placeholders
            few_shot_examples: Optional few-shot examples
            
        Returns:
            True if added successfully, False if already exists
        """
        if self._prompt_exists(prompt_id):
            return False
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO prompt_variants 
                (prompt_id, agent_type, field_name, system_prompt, user_prompt_template, 
                 few_shot_examples, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                prompt_id,
                agent_type,
                field_name,
                system_prompt,
                user_prompt_template,
                json.dumps(few_shot_examples or []),
                datetime.now().isoformat()
            ))
            conn.commit()
        
        logging.info(f"Added prompt variant: {prompt_id}")
        return True
    
    def get_best_prompt(self, 
                       agent_type: str, 
                       field_name: Optional[str] = None,
                       context_features: Optional[List[float]] = None) -> Optional[PromptVariant]:
        """
        Get the best prompt variant for the given agent and field.
        
        Args:
            agent_type: Type of agent
            field_name: Specific field name (optional)
            context_features: Context features for bandit selection
            
        Returns:
            Best prompt variant or None if none available
        """
        # Get available prompts
        available_prompts = self._get_available_prompts(agent_type, field_name)
        
        if not available_prompts:
            return None
        
        # Use contextual bandit to select best prompt
        if context_features is None:
            context_features = self._extract_default_context_features(agent_type)
        
        selected_prompt = self.bandit.select_prompt(available_prompts, context_features)
        
        # Update usage count
        self._update_prompt_usage(selected_prompt.prompt_id)
        
        return selected_prompt
    
    def _get_available_prompts(self, 
                             agent_type: str, 
                             field_name: Optional[str] = None) -> List[PromptVariant]:
        """Get available prompt variants for the given criteria."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if field_name:
                cursor.execute("""
                    SELECT * FROM prompt_variants 
                    WHERE agent_type = ? AND (field_name = ? OR field_name = 'all') 
                    AND is_active = 1
                    ORDER BY performance_score DESC
                """, (agent_type, field_name))
            else:
                cursor.execute("""
                    SELECT * FROM prompt_variants 
                    WHERE agent_type = ? AND is_active = 1
                    ORDER BY performance_score DESC
                """, (agent_type,))
            
            columns = [desc[0] for desc in cursor.description]
            prompts = []
            
            for row in cursor.fetchall():
                prompt_data = dict(zip(columns, row))
                prompt_data['few_shot_examples'] = json.loads(prompt_data['few_shot_examples'] or '[]')
                prompts.append(PromptVariant(**prompt_data))
            
            return prompts
    
    def _extract_default_context_features(self, agent_type: str) -> List[float]:
        """Extract default context features for an agent type."""
        # Simple feature vector based on agent type
        features = [0.0] * 10  # 10-dimensional feature vector
        
        # Agent type features
        agent_types = ['demographics', 'genetics', 'phenotypes', 'treatments']
        if agent_type in agent_types:
            features[agent_types.index(agent_type)] = 1.0
        
        # Add some random variation for exploration
        for i in range(4, 10):
            features[i] = random.random() * 0.1
        
        return features
    
    def _update_prompt_usage(self, prompt_id: str):
        """Update the usage count for a prompt variant."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE prompt_variants 
                SET usage_count = usage_count + 1, last_used = ?
                WHERE prompt_id = ?
            """, (datetime.now().isoformat(), prompt_id))
            conn.commit()
    
    def update_prompt_performance(self, 
                                prompt_id: str, 
                                success: bool,
                                context_features: Optional[List[float]] = None):
        """
        Update the performance of a prompt variant based on extraction success.
        
        Args:
            prompt_id: ID of the prompt variant
            success: Whether the extraction was successful
            context_features: Context features used
        """
        reward = 1.0 if success else 0.0
        
        if context_features is None:
            context_features = [0.0] * 10  # Default features
        
        # Update bandit
        self.bandit.update_reward(prompt_id, reward, context_features)
        
        # Update database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Record performance
            cursor.execute("""
                INSERT INTO prompt_performance (prompt_id, context_features, reward, timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                prompt_id,
                json.dumps(context_features),
                reward,
                datetime.now().isoformat()
            ))
            
            # Update prompt variant stats
            if success:
                cursor.execute("""
                    UPDATE prompt_variants 
                    SET success_count = success_count + 1
                    WHERE prompt_id = ?
                """, (prompt_id,))
            
            # Recalculate performance score
            cursor.execute("""
                SELECT usage_count, success_count FROM prompt_variants 
                WHERE prompt_id = ?
            """, (prompt_id,))
            
            result = cursor.fetchone()
            if result:
                usage_count, success_count = result
                performance_score = success_count / usage_count if usage_count > 0 else 0.0
                
                cursor.execute("""
                    UPDATE prompt_variants 
                    SET performance_score = ?
                    WHERE prompt_id = ?
                """, (performance_score, prompt_id))
            
            conn.commit()
    
    def add_few_shot_example(self, 
                           agent_type: str,
                           field_name: str,
                           input_text: str,
                           expected_output: Dict[str, Any],
                           context: str = "",
                           quality_score: float = 1.0) -> str:
        """
        Add a few-shot example for prompt enhancement.
        
        Args:
            agent_type: Type of agent
            field_name: Field name
            input_text: Input text for the example
            expected_output: Expected output
            context: Additional context
            quality_score: Quality score (0.0 to 1.0)
            
        Returns:
            Example ID
        """
        example_id = f"{agent_type}_{field_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO few_shot_examples 
                (example_id, agent_type, field_name, input_text, expected_output, 
                 context, quality_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                example_id,
                agent_type,
                field_name,
                input_text,
                json.dumps(expected_output),
                context,
                quality_score,
                datetime.now().isoformat()
            ))
            conn.commit()
        
        return example_id
    
    def get_few_shot_examples(self, 
                            agent_type: str, 
                            field_name: Optional[str] = None,
                            max_examples: int = 3) -> List[FewShotExample]:
        """
        Get few-shot examples for prompt enhancement.
        
        Args:
            agent_type: Type of agent
            field_name: Specific field name (optional)
            max_examples: Maximum number of examples to return
            
        Returns:
            List of few-shot examples
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if field_name:
                cursor.execute("""
                    SELECT * FROM few_shot_examples 
                    WHERE agent_type = ? AND field_name = ?
                    ORDER BY quality_score DESC, usage_count ASC
                    LIMIT ?
                """, (agent_type, field_name, max_examples))
            else:
                cursor.execute("""
                    SELECT * FROM few_shot_examples 
                    WHERE agent_type = ?
                    ORDER BY quality_score DESC, usage_count ASC
                    LIMIT ?
                """, (agent_type, max_examples))
            
            columns = [desc[0] for desc in cursor.description]
            examples = []
            
            for row in cursor.fetchall():
                example_data = dict(zip(columns, row))
                example_data['expected_output'] = json.loads(example_data['expected_output'])
                examples.append(FewShotExample(**example_data))
            
            # Update usage count
            for example in examples:
                cursor.execute("""
                    UPDATE few_shot_examples 
                    SET usage_count = usage_count + 1
                    WHERE example_id = ?
                """, (example.example_id,))
            
            conn.commit()
            
            return examples
    
    def enhance_prompt_with_examples(self, 
                                   prompt_variant: PromptVariant,
                                   patient_text: str,
                                   max_examples: int = 3) -> Tuple[str, str]:
        """
        Enhance a prompt with few-shot examples.
        
        Args:
            prompt_variant: Base prompt variant
            patient_text: Patient text to process
            max_examples: Maximum number of examples to include
            
        Returns:
            Tuple of (enhanced_system_prompt, enhanced_user_prompt)
        """
        # Get relevant few-shot examples
        examples = self.get_few_shot_examples(
            prompt_variant.agent_type,
            prompt_variant.field_name if prompt_variant.field_name != 'all' else None,
            max_examples
        )
        
        enhanced_system_prompt = prompt_variant.system_prompt
        enhanced_user_prompt = prompt_variant.user_prompt_template.format(patient_text=patient_text)
        
        if examples:
            examples_text = "\n\nHere are some examples of correct extractions:\n\n"
            
            for i, example in enumerate(examples, 1):
                examples_text += f"Example {i}:\n"
                examples_text += f"Input: {example.input_text[:200]}...\n"
                examples_text += f"Output: {json.dumps(example.expected_output, indent=2)}\n\n"
            
            enhanced_user_prompt = examples_text + enhanced_user_prompt
        
        return enhanced_system_prompt, enhanced_user_prompt
    
    def get_optimization_statistics(self) -> Dict[str, Any]:
        """Get statistics about prompt optimization."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Count prompt variants by agent type
            cursor.execute("""
                SELECT agent_type, COUNT(*) as count, AVG(performance_score) as avg_score
                FROM prompt_variants 
                WHERE is_active = 1
                GROUP BY agent_type
            """)
            
            agent_stats = {}
            for agent_type, count, avg_score in cursor.fetchall():
                agent_stats[agent_type] = {
                    'variant_count': count,
                    'average_performance': avg_score or 0.0
                }
            
            # Count few-shot examples
            cursor.execute("""
                SELECT agent_type, COUNT(*) as count, AVG(quality_score) as avg_quality
                FROM few_shot_examples
                GROUP BY agent_type
            """)
            
            example_stats = {}
            for agent_type, count, avg_quality in cursor.fetchall():
                example_stats[agent_type] = {
                    'example_count': count,
                    'average_quality': avg_quality or 0.0
                }
            
            # Overall statistics
            cursor.execute("SELECT COUNT(*) FROM prompt_variants WHERE is_active = 1")
            total_variants = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM few_shot_examples")
            total_examples = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM prompt_performance")
            total_performances = cursor.fetchone()[0]
            
            return {
                'total_prompt_variants': total_variants,
                'total_few_shot_examples': total_examples,
                'total_performance_records': total_performances,
                'agent_statistics': agent_stats,
                'example_statistics': example_stats
            }

