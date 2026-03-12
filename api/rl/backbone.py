"""
Shared backbone encoder - federated weights, uploaded to server.
Small MLP: context_dim → 64 → 32 latent embedding.
CPU-only; no GPU dependency.
"""
from __future__ import annotations

import torch
import torch.nn as nn

class BackboneEncoder(nn.Module):
    """
    Encodes a variable-length float context vector into a fixed 32-dim latent.
    Weights are shared across devices via FedAvg.
    """

    def __init__(self, input_dim: int, latent_dim: int = 32):
        super().__init__()
        self.input_dim = input_dim
        self.latent_dim = latent_dim
        self.backbone = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, latent_dim),
            nn.Tanh(),  # Bounded output stabilises LinTS
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.backbone(x)

    def encode(self, context_vec: list[float]) -> torch.Tensor:
        """Convenience: encode a single context vector (no grad)."""
        with torch.no_grad():
            x = torch.tensor(context_vec, dtype=torch.float32).unsqueeze(0)
            return self.forward(x).squeeze(0)