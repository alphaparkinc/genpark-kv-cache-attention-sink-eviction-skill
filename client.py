"""
Attention Sink Preservation and Sliding Window KV Cache Eviction.
Zero external dependencies, standard library only.
"""

from typing import Dict, List, Any, Optional

class AttentionSinkKVCacheClient:
    """
    Implements StreamingLLM attention sink cache eviction:
    - Retains initial sink tokens (typically initial system prompt tokens)
    - Applies sliding window FIFO retention over recent tokens
    - Discards intermediate tokens to maintain fixed GPU/memory budget
    """

    def __init__(self, sink_size: int = 4, window_size: int = 16):
        self.sink_size = sink_size
        self.window_size = window_size
        self.sink_tokens: List[Dict[str, Any]] = []
        self.recent_tokens: List[Dict[str, Any]] = []
        self.total_processed: int = 0

    def append_token(self, token_id: int, text: str, kv_state: Optional[List[float]] = None):
        """Appends a new token to KV cache with attention sink retention."""
        entry = {"id": token_id, "text": text, "step": self.total_processed}
        self.total_processed += 1

        if len(self.sink_tokens) < self.sink_size:
            self.sink_tokens.append(entry)
            return

        self.recent_tokens.append(entry)
        if len(self.recent_tokens) > self.window_size:
            self.recent_tokens.pop(0) # Evict oldest non-sink token

    def get_active_cache(self) -> List[Dict[str, Any]]:
        """Returns ordered active tokens in cache: sink tokens + recent window."""
        return self.sink_tokens + self.recent_tokens

    def get_cache_stats(self) -> Dict[str, Any]:
        """Returns telemetry on eviction efficiency and memory utilization."""
        active = len(self.sink_tokens) + len(self.recent_tokens)
        max_capacity = self.sink_size + self.window_size
        evicted = max(0, self.total_processed - active)
        return {
            "total_tokens_streamed": self.total_processed,
            "active_cache_tokens": active,
            "max_cache_capacity": max_capacity,
            "tokens_evicted": evicted,
            "compression_ratio": round(self.total_processed / active, 2) if active > 0 else 1.0
        }
