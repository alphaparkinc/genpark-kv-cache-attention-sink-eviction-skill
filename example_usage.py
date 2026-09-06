"""
Demonstration of genpark-kv-cache-attention-sink-eviction-skill
"""

from client import AttentionSinkKVCacheClient

def main():
    cache = AttentionSinkKVCacheClient(sink_size=3, window_size=5)

    # Stream 25 tokens
    for i in range(25):
        cache.append_token(token_id=100 + i, text=f"tok_{i}")

    active = cache.get_active_cache()
    stats = cache.get_cache_stats()

    print("=== STREAMING ATTENTION SINK CACHE ACTIVE ===")
    print("Sink Tokens:", [t["text"] for t in active[:3]])
    print("Recent Window Tokens:", [t["text"] for t in active[3:]])
    print(f"Total Processed: {stats['total_tokens_streamed']}")
    print(f"Tokens Evicted: {stats['tokens_evicted']}")
    print(f"Compression Factor: {stats['compression_ratio']}x")

if __name__ == "__main__":
    main()
