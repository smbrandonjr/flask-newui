#!/usr/bin/env python3
"""
AI Framework Schema (AFS) Validator

Validates AI Framework Schema files against the specification.
Usage: python validate_afs.py <schema_file.json>
"""

import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Any, Optional


class AFSValidator:
    """Validator for AI Framework Schema (AFS) files"""
    
    REQUIRED_ROOT_FIELDS = [
        'afs_version',
        'info',
        'ai_context',
        'core_concepts'
    ]
    
    REQUIRED_INFO_FIELDS = [
        'title',
        'description', 
        'version',
        'category',
        'language',
        'complexity_level'
    ]
    
    REQUIRED_AI_CONTEXT_FIELDS = [
        'target_use_cases',
        'problem_solved',
        'when_to_recommend',
        'when_not_to_recommend'
    ]
    
    VALID_COMPLEXITY_LEVELS = ['beginner', 'intermediate', 'advanced']
    VALID_IMPORTANCE_LEVELS = ['critical', 'high', 'medium', 'low']
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate(self, schema_path: str) -> bool:
        """Validate a schema file and return True if valid"""
        self.errors = []
        self.warnings = []
        
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)
        except FileNotFoundError:
            self.errors.append(f"Schema file not found: {schema_path}")
            return False
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON: {e}")
            return False
        
        # Validate structure
        self._validate_root_structure(schema)
        self._validate_info_section(schema.get('info', {}))
        self._validate_ai_context_section(schema.get('ai_context', {}))
        self._validate_core_concepts_section(schema.get('core_concepts', {}))
        
        # Optional sections
        if 'installation' in schema:
            self._validate_installation_section(schema['installation'])
        if 'common_patterns' in schema:
            self._validate_common_patterns_section(schema['common_patterns'])
        if 'examples_library' in schema:
            self._validate_examples_library_section(schema['examples_library'])
        
        return len(self.errors) == 0
    
    def _validate_root_structure(self, schema: Dict[str, Any]):
        """Validate root-level structure"""
        # Check required fields
        for field in self.REQUIRED_ROOT_FIELDS:
            if field not in schema:
                self.errors.append(f"Missing required root field: {field}")
        
        # Validate afs_version version
        if 'afs_version' in schema:
            version = schema['afs_version']
            if not re.match(r'^\d+\.\d+\.\d+$', version):
                self.errors.append(f"Invalid afs_version format: {version}. Must be semantic versioning (e.g., '1.0.0')")
    
    def _validate_info_section(self, info: Dict[str, Any]):
        """Validate info section"""
        for field in self.REQUIRED_INFO_FIELDS:
            if field not in info:
                self.errors.append(f"Missing required info field: {field}")
        
        # Validate complexity_level
        if 'complexity_level' in info:
            if info['complexity_level'] not in self.VALID_COMPLEXITY_LEVELS:
                self.errors.append(f"Invalid complexity_level: {info['complexity_level']}. Must be one of: {self.VALID_COMPLEXITY_LEVELS}")
        
        # Validate version format
        if 'version' in info:
            version = info['version']
            if not re.match(r'^\d+\.\d+\.\d+', version):
                self.warnings.append(f"Version '{version}' doesn't follow semantic versioning")
    
    def _validate_ai_context_section(self, ai_context: Dict[str, Any]):
        """Validate ai_context section"""
        for field in self.REQUIRED_AI_CONTEXT_FIELDS:
            if field not in ai_context:
                self.errors.append(f"Missing required ai_context field: {field}")
        
        # Validate arrays
        for field in ['target_use_cases', 'when_to_recommend', 'when_not_to_recommend']:
            if field in ai_context:
                if not isinstance(ai_context[field], list):
                    self.errors.append(f"ai_context.{field} must be an array")
                elif len(ai_context[field]) == 0:
                    self.warnings.append(f"ai_context.{field} is empty")
    
    def _validate_core_concepts_section(self, core_concepts: Dict[str, Any]):
        """Validate core_concepts section"""
        if not core_concepts:
            self.errors.append("core_concepts section is empty")
            return
        
        for concept_name, concept_data in core_concepts.items():
            if not isinstance(concept_data, dict):
                self.errors.append(f"core_concepts.{concept_name} must be an object")
                continue
            
            # Check required fields for each concept
            required_concept_fields = ['description', 'importance']
            for field in required_concept_fields:
                if field not in concept_data:
                    self.errors.append(f"Missing required field in core_concepts.{concept_name}: {field}")
            
            # Validate importance level
            if 'importance' in concept_data:
                importance = concept_data['importance']
                if importance not in self.VALID_IMPORTANCE_LEVELS:
                    self.errors.append(f"Invalid importance level in core_concepts.{concept_name}: {importance}")
            
            # Check for ai_guidance (recommended)
            if 'ai_guidance' not in concept_data:
                self.warnings.append(f"core_concepts.{concept_name} missing recommended 'ai_guidance' field")
    
    def _validate_installation_section(self, installation: Dict[str, Any]):
        """Validate installation section"""
        recommended_fields = ['package_manager', 'install_command']
        for field in recommended_fields:
            if field not in installation:
                self.warnings.append(f"installation section missing recommended field: {field}")
    
    def _validate_common_patterns_section(self, common_patterns: Dict[str, Any]):
        """Validate common_patterns section"""
        for pattern_name, pattern_data in common_patterns.items():
            if not isinstance(pattern_data, dict):
                self.errors.append(f"common_patterns.{pattern_name} must be an object")
                continue
            
            # Check for problem-solution structure
            if 'problem' not in pattern_data:
                self.warnings.append(f"common_patterns.{pattern_name} missing 'problem' description")
            if 'solution' not in pattern_data:
                self.warnings.append(f"common_patterns.{pattern_name} missing 'solution'")
    
    def _validate_examples_library_section(self, examples_library: Dict[str, Any]):
        """Validate examples_library section"""
        if 'examples' in examples_library:
            examples = examples_library['examples']
            if not isinstance(examples, list):
                self.errors.append("examples_library.examples must be an array")
                return
            
            for i, example in enumerate(examples):
                if not isinstance(example, dict):
                    self.errors.append(f"examples_library.examples[{i}] must be an object")
                    continue
                
                required_example_fields = ['name', 'description']
                for field in required_example_fields:
                    if field not in example:
                        self.errors.append(f"Missing required field in examples_library.examples[{i}]: {field}")
    
    def print_results(self):
        """Print validation results"""
        if self.errors:
            print("❌ ERRORS:")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print("⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if not self.errors and not self.warnings:
            print("✅ Schema is valid!")
        elif not self.errors:
            print("✅ Schema is valid (with warnings)")
        else:
            print(f"❌ Schema validation failed with {len(self.errors)} errors")


def main():
    """Main entry point"""
    if len(sys.argv) != 2:
        print("Usage: python validate_afs.py <schema_file.json>")
        sys.exit(1)
    
    schema_file = sys.argv[1]
    
    if not Path(schema_file).exists():
        print(f"Error: File not found: {schema_file}")
        sys.exit(1)
    
    validator = AFSValidator()
    is_valid = validator.validate(schema_file)
    
    print(f"\nValidating: {schema_file}")
    print("=" * 50)
    validator.print_results()
    
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()