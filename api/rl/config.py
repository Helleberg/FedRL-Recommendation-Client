"""
Configuration constants for the RL package.

Central place for shared hyperparameters and feature dimensions so that
`backbone.py`, `context.py`, `model_manager.py`, etc. stay in sync.
"""

# Dimension of the context vector produced by ContextExtractor and consumed
# by BackboneEncoder.
CONTEXT_DIM: int = 28

# Default model hyperparameters
DEFAULT_BACKBONE_DIM: int = 32
DEFAULT_ALGORITHM: str = "ts"  # ts = Thompson Sampling, dqn = Deep Q-Network
DEFAULT_COLD_START_RECS: int = 8

# How many past interactions to keep in ContextExtractor session history
MAX_SESSION_HISTORY: int = 20