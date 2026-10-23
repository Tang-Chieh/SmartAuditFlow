import os
import logging
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import time

logger = logging.getLogger(__name__)

class ModelManager:
    """Manages multiple AI model providers with unified interface"""
    
    def __init__(self):
        self.preferred_model = 'auto'
        self.models = {}
        self.available_models = {}
        self.initialization_errors = {}
        
        # Initialize all available models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize all available AI models"""
        print("🔧 Initializing AI models...")
        
        # Initialize OpenAI
        self._init_openai()

        # Initialize the local Codex OAuth gateway as a separate, explicit
        # OpenAI-compatible provider. It is never used as an implicit fallback.
        self._init_codex_gateway()
        
        # Initialize Gemini (OpenAI-compatible)
        self._init_gemini()
        
        # Initialize DeepSeek (OpenAI-compatible)
        self._init_deepseek()
        
        # Initialize Claude (Anthropic API)
        self._init_claude()
        
        # Log initialization summary
        available_count = sum(self.available_models.values())
        total_count = len(self.available_models)
        print(f"🤖 Model initialization complete: {available_count}/{total_count} models available")
        
        if available_count == 0:
            print("⚠️ No AI models are available. Please check your API keys.")
    
    def _init_openai(self):
        """Initialize OpenAI model"""
        try:
            import openai
            api_key = os.getenv('OPENAI_API_KEY')
            
            if not api_key:
                self.available_models['openai'] = False
                self.initialization_errors['openai'] = "OPENAI_API_KEY not found in environment"
                print("❌ OPENAI_API_KEY not found")
                return
            
            self.models['openai'] = openai.OpenAI(api_key=api_key)
            self.available_models['openai'] = True
            
            # Also initialize additional OpenAI models using the same client
            self.models['gpt-4o-mini'] = openai.OpenAI(api_key=api_key)
            self.available_models['gpt-4o-mini'] = True
            
            self.models['gpt-4.1'] = openai.OpenAI(api_key=api_key)
            self.available_models['gpt-4.1'] = True
            
            self.models['o4'] = openai.OpenAI(api_key=api_key)
            self.available_models['o4'] = True
            
            self.models['o3-mini'] = openai.OpenAI(api_key=api_key)
            self.available_models['o3-mini'] = True
            
            print("✅ OpenAI model initialized successfully")
            print("✅ GPT-4o-mini model initialized successfully")
            print("✅ GPT-4.1 model initialized successfully")
            print("✅ O4 model initialized successfully")
            print("✅ O3-mini model initialized successfully")
            
        except ImportError:
            self.available_models['openai'] = False
            self.available_models['gpt-4o-mini'] = False
            self.available_models['gpt-4.1'] = False
            self.available_models['o4'] = False
            self.available_models['o3-mini'] = False
            self.initialization_errors['openai'] = "OpenAI library not installed"
            self.initialization_errors['gpt-4o-mini'] = "OpenAI library not installed"
            self.initialization_errors['gpt-4.1'] = "OpenAI library not installed"
            self.initialization_errors['o4'] = "OpenAI library not installed"
            self.initialization_errors['o3-mini'] = "OpenAI library not installed"
            print("❌ OpenAI library not available")
        except Exception as e:
            self.available_models['openai'] = False
            self.available_models['gpt-4o-mini'] = False
            self.available_models['gpt-4.1'] = False
            self.available_models['o4'] = False
            self.available_models['o3-mini'] = False
            self.initialization_errors['openai'] = str(e)
            self.initialization_errors['gpt-4o-mini'] = str(e)
            self.initialization_errors['gpt-4.1'] = str(e)
            self.initialization_errors['o4'] = str(e)
            self.initialization_errors['o3-mini'] = str(e)
            print(f"❌ Failed to initialize OpenAI: {e}")

    def _init_codex_gateway(self):
        """Initialize an explicit local Codex OAuth gateway provider.

        The gateway bearer token is supplied through CODEX_GATEWAY_API_KEY;
        this is a local gateway credential, not an OpenAI API key. Restricting
        the URL to loopback prevents accidentally sending it to a remote host.
        """
        try:
            from urllib.parse import urlparse
            import openai

            api_key = os.getenv('CODEX_GATEWAY_API_KEY')
            base_url = os.getenv('CODEX_GATEWAY_BASE_URL', 'http://127.0.0.1:4000/v1')
            parsed = urlparse(base_url)
            if not api_key:
                self.available_models['codex-gateway'] = False
                self.initialization_errors['codex-gateway'] = 'CODEX_GATEWAY_API_KEY not found in environment'
                return
            if parsed.scheme != 'http' or parsed.hostname not in {'127.0.0.1', 'localhost', '::1'}:
                self.available_models['codex-gateway'] = False
                self.initialization_errors['codex-gateway'] = 'Codex gateway must use an http loopback URL'
                return

            self.models['codex-gateway'] = openai.OpenAI(api_key=api_key, base_url=base_url)
            self.available_models['codex-gateway'] = True
            print('✅ Local Codex OAuth gateway initialized (loopback only)')
        except ImportError:
            self.available_models['codex-gateway'] = False
            self.initialization_errors['codex-gateway'] = 'OpenAI library not installed'
        except Exception as e:
            self.available_models['codex-gateway'] = False
            self.initialization_errors['codex-gateway'] = str(e)
    
    def _init_gemini(self):
        """Initialize Gemini model (OpenAI-compatible interface)"""
        try:
            import openai
            api_key = os.getenv('GEMINI_API_KEY')
            base_url = os.getenv('GEMINI_BASE_URL', 'https://generativelanguage.googleapis.com/v1beta/openai/')
            
            if not api_key:
                self.available_models['gemini'] = False
                self.initialization_errors['gemini'] = "GEMINI_API_KEY not found in environment"
                print("❌ GEMINI_API_KEY not found")
                return
            
            self.models['gemini'] = openai.OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            self.available_models['gemini'] = True
            print("✅ Gemini model initialized successfully (OpenAI-compatible)")
            
        except ImportError:
            self.available_models['gemini'] = False
            self.initialization_errors['gemini'] = "OpenAI library not installed"
            print("❌ OpenAI library not available for Gemini")
        except Exception as e:
            self.available_models['gemini'] = False
            self.initialization_errors['gemini'] = str(e)
            print(f"❌ Failed to initialize Gemini: {e}")
    
    def _init_deepseek(self):
        """Initialize DeepSeek model (OpenAI-compatible interface)"""
        try:
            import openai
            api_key = os.getenv('DEEPSEEK_API_KEY')
            base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/')
            
            if not api_key:
                self.available_models['deepseek'] = False
                self.initialization_errors['deepseek'] = "DEEPSEEK_API_KEY not found in environment"
                print("❌ DEEPSEEK_API_KEY not found")
                return
            
            self.models['deepseek'] = openai.OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            self.available_models['deepseek'] = True
            print("✅ DeepSeek model initialized successfully (OpenAI-compatible)")
            
        except ImportError:
            self.available_models['deepseek'] = False
            self.initialization_errors['deepseek'] = "OpenAI library not installed"
            print("❌ OpenAI library not available for DeepSeek")
        except Exception as e:
            self.available_models['deepseek'] = False
            self.initialization_errors['deepseek'] = str(e)
            print(f"❌ Failed to initialize DeepSeek: {e}")
    
    def _init_claude(self):
        """Initialize Claude models (Anthropic API)"""
        try:
            import anthropic
            api_key = os.getenv('ANTHROPIC_API_KEY')
            
            if not api_key:
                self.available_models['claude'] = False
                self.available_models['claude-opus-4-0'] = False
                self.available_models['claude-sonnet-4-0'] = False
                self.available_models['claude-3-7-sonnet-latest'] = False
                self.initialization_errors['claude'] = "ANTHROPIC_API_KEY not found in environment"
                self.initialization_errors['claude-opus-4-0'] = "ANTHROPIC_API_KEY not found in environment"
                self.initialization_errors['claude-sonnet-4-0'] = "ANTHROPIC_API_KEY not found in environment"
                self.initialization_errors['claude-3-7-sonnet-latest'] = "ANTHROPIC_API_KEY not found in environment"
                print("❌ ANTHROPIC_API_KEY not found")
                return
            
            # Initialize all Claude models with the same client
            self.models['claude'] = anthropic.Anthropic(api_key=api_key)
            self.models['claude-opus-4-0'] = anthropic.Anthropic(api_key=api_key)
            self.models['claude-sonnet-4-0'] = anthropic.Anthropic(api_key=api_key)
            self.models['claude-3-7-sonnet-latest'] = anthropic.Anthropic(api_key=api_key)
            
            self.available_models['claude'] = True
            self.available_models['claude-opus-4-0'] = True
            self.available_models['claude-sonnet-4-0'] = True
            self.available_models['claude-3-7-sonnet-latest'] = True
            
            print("✅ Claude 3.5 Sonnet model initialized successfully (Anthropic API)")
            print("✅ Claude Opus 4.0 model initialized successfully (Anthropic API)")
            print("✅ Claude Sonnet 4.0 model initialized successfully (Anthropic API)")
            print("✅ Claude 3.7 Sonnet Latest model initialized successfully (Anthropic API)")
            
        except ImportError:
            self.available_models['claude'] = False
            self.available_models['claude-opus-4-0'] = False
            self.available_models['claude-sonnet-4-0'] = False
            self.available_models['claude-3-7-sonnet-latest'] = False
            self.initialization_errors['claude'] = "Anthropic library not installed (pip install anthropic)"
            self.initialization_errors['claude-opus-4-0'] = "Anthropic library not installed (pip install anthropic)"
            self.initialization_errors['claude-sonnet-4-0'] = "Anthropic library not installed (pip install anthropic)"
            self.initialization_errors['claude-3-7-sonnet-latest'] = "Anthropic library not installed (pip install anthropic)"
            print("❌ Anthropic library not available")
        except Exception as e:
            self.available_models['claude'] = False
            self.available_models['claude-opus-4-0'] = False
            self.available_models['claude-sonnet-4-0'] = False
            self.available_models['claude-3-7-sonnet-latest'] = False
            self.initialization_errors['claude'] = str(e)
            self.initialization_errors['claude-opus-4-0'] = str(e)
            self.initialization_errors['claude-sonnet-4-0'] = str(e)
            self.initialization_errors['claude-3-7-sonnet-latest'] = str(e)
            print(f"❌ Failed to initialize Claude models: {e}")
    
    def set_preferred_model(self, model_name: str):
        """Set the preferred model for API calls"""
        self.preferred_model = model_name
        print(f"🎯 Preferred model set to: {model_name}")
    
    def get_available_models(self) -> Dict[str, bool]:
        """Get the availability status of all models"""
        return self.available_models.copy()
    
    def get_initialization_errors(self) -> Dict[str, str]:
        """Get initialization errors for debugging"""
        return self.initialization_errors.copy()
    
    def _call_openai_compatible(self, client, model_name: str, prompt: str, timeout: int = 60) -> str:
        """Call OpenAI-compatible models (OpenAI, Gemini, DeepSeek)"""
        try:
            print(f"📡 Calling {model_name} model (OpenAI-compatible, timeout: {timeout}s)")
            start_time = time.time()
            
            # Model mapping
            model_map = {
                'openai': 'gpt-4o',
                'gpt-4o-mini': 'gpt-4o-mini',
                'gpt-4.1': 'gpt-4.1',
                'o4': 'o4',
                'o3-mini': 'o3-mini',
                'gemini': 'gemini-2.0-flash',
                'deepseek': 'deepseek-chat',
                'codex-gateway': os.getenv('CODEX_GATEWAY_MODEL', 'openai-codex/gpt-5.6-luna')
            }
            
            actual_model = model_map.get(model_name, model_name)
            
            response = client.chat.completions.create(
                model=actual_model,
                messages=[
                    {"role": "system", "content": "You are a smart contract security auditor with expertise in identifying vulnerabilities, analyzing code patterns, and providing detailed security assessments."},
                    {"role": "user", "content": prompt}
                ],
                stream=False,
                timeout=timeout
            )
            
            duration = time.time() - start_time
            result = response.choices[0].message.content
            
            print(f"✅ {model_name.title()} model call successful in {duration:.2f}s ({len(result)} characters)")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"{model_name.title()} API call failed after {duration:.2f}s: {str(e)}"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
    
    def _call_claude(self, client, prompt: str, timeout: int = 60, model_name: str = 'claude') -> str:
        """Call Claude model (Anthropic API)"""
        try:
            print(f"📡 Calling {model_name} model (Anthropic API, timeout: {timeout}s)")
            start_time = time.time()
            
            # Model mapping for Claude models
            model_map = {
                'claude': 'claude-3-5-sonnet-20241022',
                'claude-opus-4-0': 'claude-3-opus-20240229',  # Using available Claude Opus
                'claude-sonnet-4-0': 'claude-3-5-sonnet-20241022',  # Using latest Sonnet
                'claude-3-7-sonnet-latest': 'claude-3-5-sonnet-20241022'  # Using latest available
            }
            
            actual_model = model_map.get(model_name, 'claude-3-5-sonnet-20241022')
            
            message = client.messages.create(
                model=actual_model,
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": f"You are a smart contract security auditor with expertise in identifying vulnerabilities, analyzing code patterns, and providing detailed security assessments.\n\n{prompt}"}
                ],
                timeout=timeout
            )
            
            duration = time.time() - start_time
            result = message.content[0].text if message.content else ""
            
            print(f"✅ {model_name} model call successful in {duration:.2f}s ({len(result)} characters)")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"{model_name} API call failed after {duration:.2f}s: {str(e)}"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
    
    def call_model_sync(self, prompt: str, preferred_model: str = None, timeout: int = 60) -> str:
        """
        Call AI model synchronously with timeout protection
        
        Args:
            prompt: The prompt to send to the model
            preferred_model: Preferred model to use ('auto', 'openai', 'gpt-4o-mini', 'gpt-4.1', 'o4', 'o3-mini', 'gemini', 'deepseek', 'claude', 'claude-opus-4-0', 'claude-sonnet-4-0', 'claude-3-7-sonnet-latest')
            timeout: Timeout in seconds for the API call
            
        Returns:
            Model response as string
        """
        model_choice = preferred_model or self.preferred_model
        
        print(f"🤖 Starting AI model call (preferred: {model_choice}, timeout: {timeout}s)")
        
        # Define fallback order based on preference
        if model_choice == 'auto':
            model_order = ['gemini', 'openai', 'gpt-4o-mini', 'gpt-4.1', 'o4', 'o3-mini', 'deepseek', 'claude', 'claude-opus-4-0', 'claude-sonnet-4-0', 'claude-3-7-sonnet-latest']
        elif model_choice == 'codex-gateway':
            # Explicit selection is fail-closed: never fall back to another
            # provider, which could unexpectedly consume a paid API key.
            model_order = ['codex-gateway']
        elif model_choice in self.available_models:
            model_order = [model_choice, 'gemini', 'openai', 'gpt-4o-mini', 'gpt-4.1', 'o4', 'o3-mini', 'deepseek', 'claude', 'claude-opus-4-0', 'claude-sonnet-4-0', 'claude-3-7-sonnet-latest']
            model_order = list(dict.fromkeys(model_order))  # Remove duplicates while preserving order
        else:
            model_order = ['gemini', 'openai', 'gpt-4o-mini', 'gpt-4.1', 'o4', 'o3-mini', 'deepseek', 'claude', 'claude-opus-4-0', 'claude-sonnet-4-0', 'claude-3-7-sonnet-latest']
        
        last_error = None
        
        for model_name in model_order:
            if not self.available_models.get(model_name, False):
                print(f"⏭️ Skipping {model_name} (not available)")
                continue
            
            try:
                print(f"🔥 Trying {model_name} model...")
                
                client = self.models[model_name]
                
                # Use ThreadPoolExecutor for timeout protection
                with ThreadPoolExecutor(max_workers=1) as executor:
                    if model_name in ['claude', 'claude-opus-4-0', 'claude-sonnet-4-0', 'claude-3-7-sonnet-latest']:
                        future = executor.submit(self._call_claude, client, prompt, timeout, model_name)
                    else:
                        future = executor.submit(self._call_openai_compatible, client, model_name, prompt, timeout)
                    
                    try:
                        result = future.result(timeout=timeout + 5)  # Add 5 seconds buffer
                        print(f"🎉 Successfully used {model_name} model")
                        return result
                        
                    except TimeoutError:
                        error_msg = f"{model_name.title()} API call timed out after {timeout} seconds"
                        print(f"⏰ {error_msg}")
                        last_error = error_msg
                        continue
                        
            except Exception as e:
                error_msg = f"{model_name.title()} model call attempt failed: {str(e)}"
                print(f"❌ {error_msg}")
                last_error = error_msg
                continue
        
        # If all models failed
        error_message = f"All AI models failed. Last error: {last_error}"
        print(f"💥 {error_message}")
        raise Exception(error_message)

# Global model manager instance
global_model_manager = None

def get_model_manager() -> ModelManager:
    """Get or create the global model manager instance"""
    global global_model_manager
    if global_model_manager is None:
        global_model_manager = ModelManager()
        print("🤖 Global model manager initialized")
    return global_model_manager
