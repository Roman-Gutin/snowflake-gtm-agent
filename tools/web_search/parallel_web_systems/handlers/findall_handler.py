"""
Parallel Web Systems FindAll API Handler for Snowflake UDFs

This module provides entity discovery and enrichment capabilities using the 
Parallel Web Systems FindAll API. Designed to work as Snowflake UDFs with 
secret-based authentication.

Supported Operations:
- Create FindAll runs to discover entities matching criteria
- Get FindAll run status and results
- Extend FindAll runs with additional matches
- Enrich FindAll results with additional data
"""

import json
import requests
import time


class FindAllHandler:
    """
    Handler class for Parallel Web Systems FindAll API operations in Snowflake UDFs.
    
    Uses Snowflake secrets for API key authentication.
    Returns structured JSON responses with success/error handling.
    """
    
    BASE_URL = "https://api.parallel.ai"
    TIMEOUT = 120  # seconds
    BETA_HEADER = "findall-2025-09-15"
    DEFAULT_GENERATOR = "core"
    DEFAULT_MATCH_LIMIT = 10
    
    def __init__(self, snowflake_module=None):
        """
        Initialize the handler.
        
        Args:
            snowflake_module: The _snowflake module (injected in Snowflake UDF context)
        """
        self._snowflake = snowflake_module
    
    def _get_api_key(self):
        """Get API key from Snowflake secret."""
        if self._snowflake is None:
            raise RuntimeError("Snowflake module not initialized")
        return self._snowflake.get_generic_secret_string('api_key')
    
    def _get_headers(self):
        """Get common headers for API requests."""
        return {
            "x-api-key": self._get_api_key(),
            "Content-Type": "application/json",
            "parallel-beta": self.BETA_HEADER
        }
    
    def create_findall_run(
        self,
        objective: str,
        entity_type: str,
        match_conditions: list,
        generator: str = None,
        match_limit: int = None,
        exclude_list: list = None,
        metadata: dict = None
    ) -> dict:
        """
        Create a new FindAll run to discover entities matching criteria.
        
        Args:
            objective: Natural language description of what to find
            entity_type: Type of entity (e.g., "companies", "people")
            match_conditions: List of conditions each entity must match
            generator: Generator to use (base, core, pro, preview). Default: core
            match_limit: Maximum matches to find (5-1000). Default: 10
            exclude_list: List of entity names/IDs to exclude
            metadata: Optional metadata to attach to the run
            
        Returns:
            dict: Response with findall_id and status
        """
        generator = generator or self.DEFAULT_GENERATOR
        match_limit = match_limit or self.DEFAULT_MATCH_LIMIT
        
        try:
            payload = {
                "objective": objective,
                "entity_type": entity_type,
                "match_conditions": match_conditions,
                "generator": generator,
                "match_limit": match_limit
            }
            
            if exclude_list:
                payload["exclude_list"] = exclude_list
            if metadata:
                payload["metadata"] = metadata
            
            response = requests.post(
                f"{self.BASE_URL}/v1beta/findall/runs",
                headers=self._get_headers(),
                json=payload,
                timeout=self.TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'findall_id': result.get('findall_id'),
                    'status': result.get('status', {}).get('status'),
                    'is_active': result.get('status', {}).get('is_active'),
                    'generator': result.get('generator'),
                    'created_at': result.get('created_at')
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'objective': objective
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'objective': objective
            }
    
    def get_findall_status(self, findall_id: str) -> dict:
        """
        Get the status of a FindAll run.
        
        Args:
            findall_id: The FindAll run ID
            
        Returns:
            dict: Status information including metrics
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/v1beta/findall/runs/{findall_id}",
                headers=self._get_headers(),
                timeout=self.TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                status_obj = result.get('status', {})
                return {
                    'success': True,
                    'findall_id': findall_id,
                    'status': status_obj.get('status'),
                    'is_active': status_obj.get('is_active'),
                    'metrics': status_obj.get('metrics', {}),
                    'modified_at': result.get('modified_at')
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'findall_id': findall_id
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e), 'findall_id': findall_id}

    def get_findall_results(self, findall_id: str) -> dict:
        """
        Get the results of a FindAll run.

        Args:
            findall_id: The FindAll run ID

        Returns:
            dict: Results including matched candidates
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/v1beta/findall/runs/{findall_id}/result",
                headers=self._get_headers(),
                timeout=self.TIMEOUT
            )

            if response.status_code == 200:
                result = response.json()
                run = result.get('run', {})
                candidates = result.get('candidates', [])

                # Filter to only matched candidates
                matched = [c for c in candidates if c.get('match_status') == 'matched']

                return {
                    'success': True,
                    'findall_id': findall_id,
                    'status': run.get('status', {}).get('status'),
                    'is_active': run.get('status', {}).get('is_active'),
                    'total_candidates': len(candidates),
                    'matched_count': len(matched),
                    'candidates': matched
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'findall_id': findall_id
                }

        except Exception as e:
            return {'success': False, 'error': str(e), 'findall_id': findall_id}

    def extend_findall(self, findall_id: str, additional_match_limit: int) -> dict:
        """
        Extend a FindAll run to find more matches.

        Args:
            findall_id: The FindAll run ID
            additional_match_limit: Number of additional matches to find

        Returns:
            dict: Updated schema information
        """
        try:
            payload = {"additional_match_limit": additional_match_limit}

            response = requests.post(
                f"{self.BASE_URL}/v1beta/findall/runs/{findall_id}/extend",
                headers=self._get_headers(),
                json=payload,
                timeout=self.TIMEOUT
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'findall_id': findall_id,
                    'new_match_limit': result.get('match_limit'),
                    'objective': result.get('objective'),
                    'entity_type': result.get('entity_type')
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'findall_id': findall_id
                }

        except Exception as e:
            return {'success': False, 'error': str(e), 'findall_id': findall_id}

    def enrich_findall(
        self,
        findall_id: str,
        output_schema: dict,
        processor: str = "core"
    ) -> dict:
        """
        Add enrichment to a FindAll run to gather additional data about matches.

        Args:
            findall_id: The FindAll run ID
            output_schema: JSON schema defining what data to extract
            processor: Processor to use (base, core, pro). Default: core

        Returns:
            dict: Updated schema with enrichments
        """
        try:
            payload = {
                "processor": processor,
                "output_schema": output_schema
            }

            response = requests.post(
                f"{self.BASE_URL}/v1beta/findall/runs/{findall_id}/enrich",
                headers=self._get_headers(),
                json=payload,
                timeout=self.TIMEOUT
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'findall_id': findall_id,
                    'enrichments': result.get('enrichments', []),
                    'objective': result.get('objective')
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'findall_id': findall_id
                }

        except Exception as e:
            return {'success': False, 'error': str(e), 'findall_id': findall_id}

    def cancel_findall(self, findall_id: str) -> dict:
        """
        Cancel a FindAll run.

        Args:
            findall_id: The FindAll run ID

        Returns:
            dict: Cancellation status
        """
        try:
            response = requests.post(
                f"{self.BASE_URL}/v1beta/findall/runs/{findall_id}/cancel",
                headers=self._get_headers(),
                timeout=self.TIMEOUT
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'findall_id': findall_id,
                    'status': result.get('status', {}).get('status'),
                    'message': 'FindAll run cancelled'
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'findall_id': findall_id
                }

        except Exception as e:
            return {'success': False, 'error': str(e), 'findall_id': findall_id}

    def wait_for_completion(
        self,
        findall_id: str,
        poll_interval: int = 5,
        max_wait: int = 300
    ) -> dict:
        """
        Wait for a FindAll run to complete and return results.

        Args:
            findall_id: The FindAll run ID
            poll_interval: Seconds between status checks. Default: 5
            max_wait: Maximum seconds to wait. Default: 300

        Returns:
            dict: Final results when complete
        """
        start_time = time.time()

        while time.time() - start_time < max_wait:
            status = self.get_findall_status(findall_id)

            if not status.get('success'):
                return status

            if not status.get('is_active'):
                # Run is complete, get results
                return self.get_findall_results(findall_id)

            time.sleep(poll_interval)

        return {
            'success': False,
            'error': f'Timeout after {max_wait} seconds',
            'findall_id': findall_id
        }


# ============================================================================
# UDF Entry Points - These functions are called directly by Snowflake UDFs
# ============================================================================

def create_findall_run(
    objective, entity_type, match_conditions_json, generator, match_limit, _snowflake_module
):
    """UDF entry point for creating a FindAll run."""
    handler = FindAllHandler(_snowflake_module)
    match_conditions = json.loads(match_conditions_json) if isinstance(match_conditions_json, str) else match_conditions_json
    result = handler.create_findall_run(
        objective=objective,
        entity_type=entity_type,
        match_conditions=match_conditions,
        generator=generator,
        match_limit=match_limit
    )
    return json.dumps(result)


def get_findall_status(findall_id, _snowflake_module):
    """UDF entry point for getting FindAll status."""
    handler = FindAllHandler(_snowflake_module)
    result = handler.get_findall_status(findall_id)
    return json.dumps(result)


def get_findall_results(findall_id, _snowflake_module):
    """UDF entry point for getting FindAll results."""
    handler = FindAllHandler(_snowflake_module)
    result = handler.get_findall_results(findall_id)
    return json.dumps(result)


def extend_findall(findall_id, additional_match_limit, _snowflake_module):
    """UDF entry point for extending a FindAll run."""
    handler = FindAllHandler(_snowflake_module)
    result = handler.extend_findall(findall_id, additional_match_limit)
    return json.dumps(result)


def enrich_findall(findall_id, output_schema_json, processor, _snowflake_module):
    """UDF entry point for adding enrichment to a FindAll run."""
    handler = FindAllHandler(_snowflake_module)
    output_schema = json.loads(output_schema_json) if isinstance(output_schema_json, str) else output_schema_json
    result = handler.enrich_findall(findall_id, output_schema, processor)
    return json.dumps(result)


def cancel_findall(findall_id, _snowflake_module):
    """UDF entry point for cancelling a FindAll run."""
    handler = FindAllHandler(_snowflake_module)
    result = handler.cancel_findall(findall_id)
    return json.dumps(result)


def wait_for_findall_completion(findall_id, poll_interval, max_wait, _snowflake_module):
    """UDF entry point for waiting for FindAll completion."""
    handler = FindAllHandler(_snowflake_module)
    result = handler.wait_for_completion(findall_id, poll_interval, max_wait)
    return json.dumps(result)

