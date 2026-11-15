"""
Simulated Generation LLM
Constructs answers from the provided context chunk.
"""

from .models import DocumentChunk

class AnswerGenerator:
    @staticmethod
    def generate_answer(query: str, chunk: DocumentChunk) -> str:
        """
        Generates an authoritative answer conditioned strictly on the provided chunk.
        """
        c = chunk.content.lower()

        # E-commerce return policy
        if "returns accepted within" in c or "return" in c and "days" in c:
            if "7 days" in c:
                return "Under the current store policy, returns are accepted within 7 days of purchase. Items returned after 7 days receive store credit only."
            elif "30 days" in c:
                return "Returns are accepted within 30 days of purchase with original receipt for a full refund."

        # Python asyncio
        if "asyncio.get_event_loop()" in c:
            if "deprecated" in c or "no longer implicitly" in c:
                return "In modern Python (3.10+ and 3.12), asyncio.get_event_loop() is deprecated for implicit loop creation. If no loop is running, you must call asyncio.run() or asyncio.new_event_loop()."
            else:
                return "Call asyncio.get_event_loop() to obtain the current event loop. If no loop is active in the current OS thread, a new loop is automatically instantiated."

        # Kubernetes Ingress
        if "ingress" in c:
            if "networking.k8s.io/v1" in c:
                return "For Kubernetes Ingress resources, you must use 'apiVersion: networking.k8s.io/v1' with the 'defaultBackend' structure."
            else:
                return "Declare 'apiVersion: extensions/v1beta1' for your Kubernetes Ingress specification with 'backend.serviceName'."

        # Wikipedia Rebranding
        if "twitter" in c or "x corp" in c or "brand identity" in c:
            if "officially named x" in c:
                return "The platform is officially named X, operated by X Corp, and the blue bird has been replaced by the stylized X glyph."
            else:
                return "The official brand identity of the platform is Twitter, symbolized by Larry the blue bird."

        # STALE chat
        if "seattle" in c or "austin" in c:
            if "austin" in c:
                return "The user currently resides in Austin, Texas (relocated in late 2025) and operates an AI analytics startup."
            else:
                return "The user lives in Seattle, Washington and works remotely for an e-commerce firm."

        # Fallback
        return f"Based on the provided documentation ({chunk.version}): {chunk.content}"
