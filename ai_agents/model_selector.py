#!/usr/bin/env python3
"""
LLM Model Selection System
Provides comprehensive model selection for all available providers
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

class ModelSelector:
    def __init__(self):
        """Initialize with all available models"""
        self.models = self._get_available_models()
        self.default_model = "claude-opus-4-1-20250805"  # Opus 4.1 as default
    
    def _get_available_models(self) -> Dict[str, List[Dict[str, str]]]:
        """Get all available models organized by provider"""
        return {
            "anthropic": [
                {
                    "id": "claude-opus-4-1-20250805",
                    "name": "Claude Opus 4.1",
                    "description": "Most capable model, best for complex analysis",
                    "context_window": "200k tokens",
                    "cost": "High"
                },
                {
                    "id": "claude-3-7-sonnet-20250219", 
                    "name": "Claude Sonnet 3.7",
                    "description": "Balanced performance and cost",
                    "context_window": "200k tokens",
                    "cost": "Medium"
                },
                {
                    "id": "claude-3-5-sonnet-20241022",
                    "name": "Claude Sonnet 3.5", 
                    "description": "Good performance, lower cost",
                    "context_window": "200k tokens",
                    "cost": "Medium"
                },
                {
                    "id": "claude-3-5-haiku-20241022",
                    "name": "Claude Haiku 3.5",
                    "description": "Fast and efficient, lower cost",
                    "context_window": "200k tokens", 
                    "cost": "Low"
                }
            ],
            "openai": [
                {
                    "id": "gpt-4o",
                    "name": "GPT-4o",
                    "description": "Most capable OpenAI model",
                    "context_window": "128k tokens",
                    "cost": "High"
                },
                {
                    "id": "gpt-4o-mini",
                    "name": "GPT-4o Mini",
                    "description": "Efficient and cost-effective",
                    "context_window": "128k tokens",
                    "cost": "Low"
                },
                {
                    "id": "gpt-4-turbo",
                    "name": "GPT-4 Turbo",
                    "description": "High performance with good context",
                    "context_window": "128k tokens",
                    "cost": "High"
                },
                {
                    "id": "gpt-3.5-turbo",
                    "name": "GPT-3.5 Turbo",
                    "description": "Fast and cost-effective",
                    "context_window": "16k tokens",
                    "cost": "Low"
                }
            ]
        }
    
    def display_model_menu(self) -> None:
        """Display interactive model selection menu"""
        print("\n" + "="*60)
        print("LLM MODEL SELECTION")
        print("="*60)
        
        option_number = 1
        model_options = {}
        
        for provider, models in self.models.items():
            print(f"\n{provider.upper()} MODELS:")
            print("-" * 20)
            
            for model in models:
                model_options[option_number] = {
                    "provider": provider,
                    "model": model
                }
                
                print(f"{option_number:2d}. {model['name']}")
                print(f"    ID: {model['id']}")
                print(f"    Description: {model['description']}")
                print(f"    Context: {model['context_window']}, Cost: {model['cost']}")
                print()
                
                option_number += 1
        
        print(f"Default: Claude Opus 4.1 (Option 1)")
        print("="*60)
    
    def get_model_selection(self, use_default: bool = False) -> Tuple[str, str]:
        """
        Get model selection from user or return default
        
        Args:
            use_default: If True, return default model without prompting
            
        Returns:
            Tuple of (provider, model_id)
        """
        if use_default:
            return "anthropic", self.default_model
        
        self.display_model_menu()
        
        while True:
            try:
                choice = input(f"\nSelect model (1-{len(self._get_all_models())}, or 'default' for Opus 4.1): ").strip()
                
                if choice.lower() == 'default' or choice == '':
                    return "anthropic", self.default_model
                
                choice_num = int(choice)
                all_models = self._get_all_models()
                
                if 1 <= choice_num <= len(all_models):
                    selected = all_models[choice_num - 1]
                    return selected["provider"], selected["model"]["id"]
                else:
                    print(f"Please enter a number between 1 and {len(all_models)}")
                    
            except ValueError:
                print("Please enter a valid number or 'default'")
            except KeyboardInterrupt:
                print("\nUsing default model (Claude Opus 4.1)")
                return "anthropic", self.default_model
    
    def _get_all_models(self) -> List[Dict[str, any]]:
        """Get all models as a flat list with provider info"""
        all_models = []
        for provider, models in self.models.items():
            for model in models:
                all_models.append({
                    "provider": provider,
                    "model": model
                })
        return all_models
    
    def get_model_info(self, provider: str, model_id: str) -> Optional[Dict[str, str]]:
        """Get detailed info for a specific model"""
        if provider in self.models:
            for model in self.models[provider]:
                if model["id"] == model_id:
                    return model
        return None
    
    def validate_model(self, provider: str, model_id: str) -> bool:
        """Validate that a model exists and is available"""
        if provider in self.models:
            for model in self.models[provider]:
                if model["id"] == model_id:
                    return True
        return False
    
    def get_recommended_models(self) -> List[Tuple[str, str]]:
        """Get list of recommended models for different use cases"""
        return [
            ("anthropic", "claude-opus-4-1-20250805"),  # Best overall
            ("anthropic", "claude-3-7-sonnet-20250219"),  # Balanced
            ("openai", "gpt-4o"),  # Best OpenAI
            ("openai", "gpt-4o-mini"),  # Cost-effective
        ]
    
    def get_models_by_cost(self, cost_level: str) -> List[Tuple[str, str]]:
        """Get models filtered by cost level (High, Medium, Low)"""
        models = []
        for provider, model_list in self.models.items():
            for model in model_list:
                if model["cost"].lower() == cost_level.lower():
                    models.append((provider, model["id"]))
        return models
