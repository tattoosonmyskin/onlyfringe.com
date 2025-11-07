"""
AI Fact-Checking Module using OpenAI API
"""
import json
import openai
import validators
from config import Config

class FactChecker:
    """AI-powered fact checker for arguments and rebuttals"""
    
    def __init__(self):
        if Config.OPENAI_API_KEY:
            openai.api_key = Config.OPENAI_API_KEY
        else:
            print("Warning: OPENAI_API_KEY not set. Fact-checking will not work.")
    
    def check_argument(self, content, sources):
        """
        Check an argument for factual accuracy and logical coherence
        
        Args:
            content: The argument text
            sources: List of source dictionaries with 'url', 'title', 'description'
            
        Returns:
            dict with 'is_valid', 'score', 'issues', 'recommendations'
        """
        if not Config.OPENAI_API_KEY:
            return {
                'is_valid': False,
                'score': 0,
                'issues': ['OpenAI API key not configured'],
                'recommendations': ['Configure OPENAI_API_KEY to enable fact-checking']
            }
        
        # Format sources for AI analysis
        sources_text = "\n".join([
            f"- {s.get('title', 'Untitled')}: {s.get('url', 'No URL')} - {s.get('description', 'No description')}"
            for s in sources
        ])
        
        prompt = f"""You are a rigorous fact-checker for a debate platform. Analyze the following argument for:
1. Factual accuracy - Are the claims verifiable and true?
2. Logical coherence - Is the reasoning sound and well-structured?
3. Source quality - Are the sources credible and relevant?
4. Context completeness - Does the argument provide full context?
5. Evidence-based reasoning - Are claims supported by evidence?

Argument:
{content}

Sources provided:
{sources_text}

Provide your analysis in the following JSON format:
{{
    "is_valid": true/false,
    "score": 0-100,
    "issues": ["list of any issues found"],
    "recommendations": ["list of recommendations for improvement"],
    "factual_accuracy": "assessment of factual claims",
    "logical_coherence": "assessment of logical structure",
    "source_quality": "assessment of sources",
    "context_completeness": "assessment of context provided"
}}
"""
        
        try:
            response = openai.chat.completions.create(
                model=Config.AI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert fact-checker and logical reasoning analyst. Provide thorough, unbiased analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=Config.AI_TEMPERATURE,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            return {
                'is_valid': False,
                'score': 0,
                'issues': [f'Error during fact-checking: {str(e)}'],
                'recommendations': ['Please try again or contact support']
            }
    
    def check_rebuttal(self, rebuttal_content, original_argument, sources):
        """
        Check a rebuttal for factual accuracy and logical response to original argument
        
        Args:
            rebuttal_content: The rebuttal text
            original_argument: The original argument being rebutted
            sources: List of source dictionaries
            
        Returns:
            dict with validation results
        """
        if not Config.OPENAI_API_KEY:
            return {
                'is_valid': False,
                'score': 0,
                'issues': ['OpenAI API key not configured'],
                'recommendations': ['Configure OPENAI_API_KEY to enable fact-checking']
            }
        
        sources_text = "\n".join([
            f"- {s.get('title', 'Untitled')}: {s.get('url', 'No URL')} - {s.get('description', 'No description')}"
            for s in sources
        ])
        
        prompt = f"""You are a rigorous fact-checker for a debate platform. Analyze the following rebuttal for:
1. Factual accuracy - Are the claims verifiable and true?
2. Logical response - Does it address the original argument effectively?
3. Evidence-based reasoning - Are counter-claims supported by evidence?
4. Source quality - Are the sources credible and relevant?
5. Avoidance of rhetoric - Does it focus on facts rather than emotional appeals?

Original Argument:
{original_argument}

Rebuttal:
{rebuttal_content}

Sources provided for rebuttal:
{sources_text}

Provide your analysis in the following JSON format:
{{
    "is_valid": true/false,
    "score": 0-100,
    "issues": ["list of any issues found"],
    "recommendations": ["list of recommendations for improvement"],
    "addresses_original": "does the rebuttal address the original argument",
    "factual_accuracy": "assessment of factual claims",
    "evidence_quality": "assessment of evidence provided"
}}
"""
        
        try:
            response = openai.chat.completions.create(
                model=Config.AI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert fact-checker and logical reasoning analyst. Provide thorough, unbiased analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=Config.AI_TEMPERATURE,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            return {
                'is_valid': False,
                'score': 0,
                'issues': [f'Error during fact-checking: {str(e)}'],
                'recommendations': ['Please try again or contact support']
            }
    
    def validate_sources(self, sources):
        """
        Validate that sources are credible and relevant
        
        Args:
            sources: List of source dictionaries
            
        Returns:
            dict with validation results for each source
        """
        results = []
        for source in sources:
            url = source.get('url', '')
            # validators.url returns True if valid, or ValidationError if invalid
            # We need to convert this to boolean
            validation_result = validators.url(url) if url else False
            is_valid_url = validation_result is True
            
            results.append({
                'url': url,
                'is_valid_url': is_valid_url,
                'title': source.get('title'),
                'has_description': bool(source.get('description'))
            })
        
        return results
