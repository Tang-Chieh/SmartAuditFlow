import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)
SOURCE_FILE_BLOCK_RE = re.compile(
    r"^// ===== BEGIN SOURCE FILE: (.+?) =====\r?\n(.*?)^// ===== END SOURCE FILE: \1 =====$",
    re.MULTILINE | re.DOTALL,
)


PRICE_MANIPULATION_SCOPE = """
Audit ONLY for price-manipulation vulnerabilities in financially sensitive
smart-contract logic. Look for values derived from attacker-influenceable AMM/
DEX state (reserves, token balances, liquidity, spot prices, slot0/getReserves),
flash-loan or swap-induced temporary state changes, LP-token/vault-share/collateral
valuation, and downstream borrowing, minting, redemption, withdrawal, liquidation,
or reward calculations. Check whether manipulation-resistant controls are absent
or ineffective (for example TWAP, independent oracle sources, freshness and
deviation checks, liquidity/slippage bounds, or safe state-update ordering).

Report a vulnerability only when the supplied source shows a concrete data/control
path from attacker-influenceable state to a security-critical financial outcome.
Do not report generic reentrancy, access-control, gas, style, or other unrelated
issues. Do not claim tests, static-analysis results, external knowledge-base matches,
or facts that were not supplied. If evidence is insufficient, say so and do not
promote speculation into a finding.
""".strip()

class WorkflowNode(ABC):
    """Base class for all workflow nodes"""
    
    def __init__(self, node_id: str, node_type: str, model_manager=None):
        self.node_id = node_id
        self.node_type = node_type
        self.model_manager = model_manager
    
    @abstractmethod
    def execute_sync(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the node synchronously"""
        pass

class InitialAnalysisNode(WorkflowNode):
    """Initial analysis of the smart contract"""
    
    def execute_sync(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform initial analysis of the smart contract"""
        try:
            code_snippet = context.get('code_snippet', '')
            static_tool = context.get('static_tool', '')
            model_choice = context.get('model_choice', 'auto')
            
            # Create prompt for initial analysis
            prompt = f"""
            You are beginning a focused smart-contract audit.

            Audit scope:
            {PRICE_MANIPULATION_SCOPE}

            Solidity source bundle (file boundaries are marked in the text):
            {code_snippet}

            Static analysis results (may be empty; never imply a tool ran if it did not):
            {static_tool}

            Return a concise, evidence-led map of: (1) contracts/functions that read
            price, reserve, balance, liquidity, oracle, or pool state; (2) financial
            operations that consume those values; (3) the data/control path between
            them; and (4) safeguards that are visibly present or absent. Cite the
            exact source file and symbols. Separate observed facts from hypotheses.
            Do not audit unrelated vulnerability classes.
            """
            
            # Call AI model
            response = self.model_manager.call_model_sync(prompt)
            
            return {
                'analysis': response,
                'code_snippet': code_snippet,
                'static_tool': static_tool,
                'model_used': model_choice
            }
            
        except Exception as e:
            logger.error(f"Initial analysis failed: {str(e)}")
            return {
                'analysis': f"Initial analysis failed: {str(e)}",
                'code_snippet': context.get('code_snippet', ''),
                'static_tool': context.get('static_tool', ''),
                'model_used': context.get('model_choice', 'unknown')
            }

class AuditPlanNode(WorkflowNode):
    """Create detailed audit plan"""
    
    def execute_sync(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive audit plan"""
        try:
            initial_analysis = context.get('1728096797608', {}).get('analysis', '')
            code_snippet = context.get('code_snippet', '')
            
            prompt = f"""
            Based on the initial analysis, create an evidence-led audit plan restricted
            to the following vulnerability class:
            {PRICE_MANIPULATION_SCOPE}

            Initial Analysis:
            {initial_analysis}

            Solidity source bundle:
            {code_snippet}

            Produce up to 12 numbered, non-duplicative tasks. Prioritize tracing
            attacker-controlled reserve/spot-price changes into a financial action;
            checking LP/vault/collateral valuation math; checking flash-loan or
            same-transaction manipulation; and verifying TWAP/oracle freshness,
            deviation, liquidity, and update-order protections. Each task must name
            the candidate contract/function and specify the concrete evidence needed
            to confirm or reject the hypothesis. Do not add general audit or gas tasks.
            """
            
            response = self.model_manager.call_model_sync(prompt)
            
            return {
                'audit_plan': response,
                'tasks': self._extract_tasks(response)
            }
            
        except Exception as e:
            logger.error(f"Audit plan creation failed: {str(e)}")
            return {
                'audit_plan': f"Audit plan creation failed: {str(e)}",
                'tasks': []
            }
    
    def _extract_tasks(self, audit_plan: str) -> List[str]:
        """Extract individual tasks from audit plan"""
        tasks = []
        lines = audit_plan.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Clean up the task text
                task = line.lstrip('0123456789.-• ').strip()
                if task and len(task) > 10:  # Ensure meaningful tasks
                    tasks.append(task)
        return tasks[:12]  # Limit to 12 tasks for manageable execution

class ParameterExtractorNode(WorkflowNode):
    """Extract and format parameters for iteration"""
    
    def execute_sync(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract parameters for detailed audit tasks"""
        try:
            audit_plan = context.get('1728113785964', {}).get('audit_plan', '')
            tasks = context.get('1728113785964', {}).get('tasks', [])
            
            # Format tasks for iteration with priorities
            formatted_tasks = []
            priority_keywords = {
                'high': ['price', 'oracle', 'reserve', 'spot', 'twap', 'flash loan', 'collateral', 'liquidity', 'valuation'],
                'medium': ['deviation', 'freshness', 'slippage', 'lp token', 'vault share', 'reward'],
                'low': ['documentation', 'style', 'naming']
            }
            
            for i, task in enumerate(tasks):
                # Determine priority based on keywords
                priority = 'medium'  # default
                task_lower = task.lower()
                for p, keywords in priority_keywords.items():
                    if any(keyword in task_lower for keyword in keywords):
                        priority = p
                        break
                
                formatted_tasks.append({
                    'id': i + 1,
                    'task': task,
                    'priority': priority,
                    'status': 'pending'
                })
            
            # Sort by priority (high first)
            priority_order = {'high': 0, 'medium': 1, 'low': 2}
            formatted_tasks.sort(key=lambda x: priority_order.get(x['priority'], 1))
            
            return {
                'tasks': formatted_tasks,
                'total_tasks': len(formatted_tasks),
                'current_task': 0,
                'high_priority_count': len([t for t in formatted_tasks if t['priority'] == 'high']),
                'medium_priority_count': len([t for t in formatted_tasks if t['priority'] == 'medium']),
                'low_priority_count': len([t for t in formatted_tasks if t['priority'] == 'low'])
            }
            
        except Exception as e:
            logger.error(f"Parameter extraction failed: {str(e)}")
            return {
                'tasks': [],
                'total_tasks': 0,
                'current_task': 0
            }

class IterationNode(WorkflowNode):
    """Execute individual audit tasks"""
    
    def execute_sync(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute all audit tasks"""
        try:
            tasks = context.get('1728114018925', {}).get('tasks', [])
            code_snippet = context.get('code_snippet', '')
            static_tool = context.get('static_tool', '')
            results = []
            
            for task in tasks:
                try:
                    prompt = f"""
                    You are performing one focused price-manipulation audit task.
                    Scope and exclusions:
                    {PRICE_MANIPULATION_SCOPE}

                    Audit Task: {task.get('task', '')}
                    Priority: {task.get('priority', 'medium')}

                    Solidity source bundle (paths and original file boundaries are marked):
                    {code_snippet}

                    Static analysis results (may be empty):
                    {static_tool}

                    Trace the exact source/value flow and state transition relevant to
                    this task. State whether the supplied code demonstrates an
                    exploitable price-manipulation path, is protected, or lacks enough
                    evidence. A positive result must cite the marked source path,
                    contract, function, and relevant original source lines when they
                    can be determined. Explain attacker prerequisites, transaction
                    sequence, affected financial operation, and concrete impact.
                    Suggest a specific mitigation only for a demonstrated issue;
                    distinguish a recommendation from an existing code behavior.
                    Do not invent a static-analysis confirmation. If static analysis
                    input is empty, base conclusions only on the Solidity source.
                    """
                    
                    response = self.model_manager.call_model_sync(prompt)
                    
                    results.append({
                        'task_id': task.get('id'),
                        'task': task.get('task'),
                        'priority': task.get('priority'),
                        'result': response,
                        'status': 'completed'
                    })
                    
                except Exception as e:
                    results.append({
                        'task_id': task.get('id'),
                        'task': task.get('task'),
                        'priority': task.get('priority'),
                        'result': f"Task execution failed: {str(e)}",
                        'status': 'failed'
                    })
            
            return {
                'task_results': results,
                'completed_tasks': len([r for r in results if r['status'] == 'completed']),
                'failed_tasks': len([r for r in results if r['status'] == 'failed']),
                'high_priority_completed': len([r for r in results if r['status'] == 'completed' and r.get('priority') == 'high']),
                'total_high_priority': len([r for r in results if r.get('priority') == 'high'])
            }
            
        except Exception as e:
            logger.error(f"Task iteration failed: {str(e)}")
            return {
                'task_results': [],
                'completed_tasks': 0,
                'failed_tasks': 1
            }

class FormatConverterNode(WorkflowNode):
    """Format final audit report with correct findings structure"""
    
    def execute_sync(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final formatted audit report with proper findings format"""
        try:
            task_results = context.get('1728114855021', {}).get('task_results', [])
            code_snippet = context.get('code_snippet', '')
            static_tool = context.get('static_tool', '')
            model_choice = context.get('model_choice', 'auto')
            
            # Ask the model for evaluator-compatible finding objects. The runtime
            # PredictionCase envelope (repo_id and detector metadata) is attached
            # by the dataset runner, not inferred from source code.
            prompt = f"""
            Consolidate the audit results into final findings. Keep the analysis
            strictly within this scope:
            {PRICE_MANIPULATION_SCOPE}

            Solidity source bundle with original file-path markers:
            {code_snippet}

            Static analysis results (may be empty):
            {static_tool}

            Audit Results Summary:
            - Total tasks completed: {len([r for r in task_results if r['status'] == 'completed'])}
            - High priority tasks: {len([r for r in task_results if r.get('priority') == 'high'])}

            Detailed Task Results:
            {json.dumps(task_results, indent=2)}

            Return ONLY a JSON array. Each array item MUST follow this exact schema:

            [
              {{
                "finding_id": "SAF-001",
                "title": "Short vulnerability title",
                "description": "Evidence-based root cause and exploit path, using only supplied source and results",
                "impact": "Concrete consequence to assets or protocol operations",
                "vulnerable_code": [
                  {{"file": "path/from/source/marker.sol", "contract": "ContractName", "function": "functionName", "start_line": null, "end_line": null}}
                ],
                "mitigation": "Specific recommended code or oracle-control change; do not imply it already exists",
                "severity": "High / Medium / Low"
              }}
            ]

            Requirements:
            - Use only the supplied source and task results. No knowledge base was
              provided unless explicitly present above; do not claim otherwise.
            - Only include a finding when a concrete price-manipulation path is
              supported by evidence. Return [] if none is supported.
            - `vulnerable_code` must identify the actual source file, contract, and
              primary vulnerable function. Include start_line/end_line only when
              confident; otherwise set both to null. Never invent a location.
            - `mitigation` is required and must be an actionable recommendation
              grounded in the described root cause, not a claim that code was fixed.
            - Each string field must be non-empty. Severity must be High, Medium,
              or Low. Do not create findings for unrelated vulnerability classes.
            """
            
            response = self.model_manager.call_model_sync(prompt)
            
            # Try to extract JSON findings from response
            findings = self._extract_json_findings(response)
            parse_warnings = []
            if findings is None:
                logger.error("Final model response did not contain a valid JSON findings array")
                parse_warnings.append("Final response was not a valid JSON findings array")
                findings = []

            predictions, rejected = self._validate_prediction_findings(findings, code_snippet)
            rejected = parse_warnings + rejected
            validated_findings = [self._to_legacy_finding(item) for item in predictions]
            
            return {
                'Findings': validated_findings,
                'Predictions': predictions,
                'PredictionSchema': 'benchmark_eval.PredictionCase.predictions/v1',
                'OutputWarnings': rejected,
                'FindingNumber': len(validated_findings),
                'FullReport': response,
                'ModelUsed': model_choice,
                'CriticalIssues': len([f for f in validated_findings if f.get('Severity') == 'High']),
                'MediumIssues': len([f for f in validated_findings if f.get('Severity') == 'Medium']),
                'LowIssues': len([f for f in validated_findings if f.get('Severity') == 'Low']),
                'ExecutionSummary': {
                    'total_tasks': len(task_results),
                    'completed_tasks': len([r for r in task_results if r['status'] == 'completed']),
                    'failed_tasks': len([r for r in task_results if r['status'] == 'failed'])
                }
            }
            
        except Exception as e:
            logger.error(f"Report formatting failed: {str(e)}")
            return {
                'Findings': [],
                'Predictions': [],
                'PredictionSchema': 'benchmark_eval.PredictionCase.predictions/v1',
                'OutputWarnings': [f"Report formatting failed: {str(e)}"],
                'FindingNumber': 0,
                'FullReport': f'Report generation failed: {str(e)}',
                'ModelUsed': context.get('model_choice', 'unknown'),
                'CriticalIssues': 0,
                'MediumIssues': 0,
                'LowIssues': 0
            }
    
    def _extract_json_findings(self, response: str) -> Optional[List[Dict[str, Any]]]:
        """Extract a JSON array; distinguish a valid empty array from parse failure."""
        try:
            decoder = json.JSONDecoder()
            for start, char in enumerate(response):
                if char != '[':
                    continue
                try:
                    findings, _ = decoder.raw_decode(response[start:])
                except json.JSONDecodeError:
                    continue
                if isinstance(findings, list) and all(isinstance(item, dict) for item in findings):
                    return findings
        except Exception as e:
            logger.warning(f"Failed to extract JSON findings: {e}")
        return None

    def _validate_prediction_findings(
        self, findings: List[Dict[str, Any]], code_snippet: str = ""
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Keep only complete evaluator-shaped findings; never synthesize missing evidence."""
        required_text = ("finding_id", "title", "description", "impact", "mitigation")
        valid_severities = {"High", "Medium", "Low"}
        source_bodies = {
            match.group(1): match.group(2)
            for match in SOURCE_FILE_BLOCK_RE.finditer(code_snippet)
        }
        validated: List[Dict[str, Any]] = []
        rejected: List[str] = []
        for index, finding in enumerate(findings, 1):
            if not isinstance(finding, dict):
                rejected.append(f"finding[{index}] is not an object")
                continue
            item = {
                key: finding.get(key, "").strip()
                if isinstance(finding.get(key, ""), str) else ""
                for key in required_text
            }
            missing = [key for key, value in item.items() if not value]
            code_refs = finding.get("vulnerable_code")
            if missing or not isinstance(code_refs, list) or not code_refs:
                rejected.append(f"finding[{index}] missing required text or vulnerable_code: {', '.join(missing) or 'vulnerable_code'}")
                continue
            normalized_refs = []
            ref_error = False
            for ref in code_refs:
                if not isinstance(ref, dict) or not all(
                    isinstance(ref.get(key), str) and ref[key].strip()
                    for key in ("file", "contract", "function")
                ):
                    ref_error = True
                    break
                source_path = ref["file"].strip()
                if source_bodies and source_path not in source_bodies:
                    ref_error = True
                    break
                start_line, end_line = ref.get("start_line"), ref.get("end_line")
                if (start_line is None) != (end_line is None):
                    ref_error = True
                    break
                if start_line is not None and (
                    not isinstance(start_line, int) or isinstance(start_line, bool)
                    or not isinstance(end_line, int) or isinstance(end_line, bool)
                    or start_line < 1 or end_line < start_line
                ):
                    ref_error = True
                    break
                if start_line is not None and source_path in source_bodies:
                    source_line_count = len(source_bodies[source_path].splitlines())
                    if end_line > source_line_count:
                        ref_error = True
                        break
                normalized_refs.append({
                    "file": ref["file"].strip(),
                    "contract": ref["contract"].strip(),
                    "function": ref["function"].strip(),
                    "start_line": start_line,
                    "end_line": end_line,
                })
            if ref_error:
                rejected.append(f"finding[{index}] has an invalid vulnerable_code location")
                continue
            severity = str(finding.get("severity", "")).strip()
            if severity and severity not in valid_severities:
                severity = "Medium"
            item["vulnerable_code"] = normalized_refs
            if severity:
                item["severity"] = severity
            validated.append(item)
        return validated, rejected

    @staticmethod
    def _to_legacy_finding(item: Dict[str, Any]) -> Dict[str, Any]:
        refs = item.get("vulnerable_code", [])
        locations = []
        for ref in refs:
            line_text = ""
            if ref.get("start_line") is not None:
                line_text = f":{ref['start_line']}-{ref['end_line']}"
            locations.append(f"{ref['file']} — {ref['contract']}.{ref['function']}{line_text}")
        return {
            "Issue": item["title"],
            "Severity": item.get("severity", "Medium"),
            "Description": item["description"],
            "Impact": item["impact"],
            "Location": "; ".join(locations),
            "Mitigation": item["mitigation"],
            "finding_id": item["finding_id"],
        }
    
