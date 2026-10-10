"""Data providers. Each returns a ProviderResult and never invents data: if a call fails, the
result says why (needs-key, blocked-by-network, rate-limited, http-error, bad-response)."""
