import torch
import torch.nn as nn
import torch.nn.functional as F


class CoralLayer(nn.Module):
    def __init__(self, input_dim, num_classes):
        super().__init__()
        self.fc = nn.Linear(input_dim, 1, bias=False)
        self.bias = nn.Parameter(torch.arange(num_classes - 1).float())

    def forward(self, x):
        # x: (B, input_dim)
        # logits: (B, 1)
        logits = self.fc(x)
        # bias: (num_classes - 1)
        # result: (B, num_classes - 1)
        return logits + self.bias


class GolfSwingModel(nn.Module):
    def __init__(self):
        super().__init__()

        # Joint Branch
        self.joint_fc = nn.Sequential(nn.Linear(429, 128), nn.ReLU(), nn.LayerNorm(128))

        # Global Branch
        self.global_mlp = nn.Sequential(nn.Linear(3, 128), nn.ReLU(), nn.LayerNorm(128))

        # LSTM
        self.lstm = nn.LSTM(
            input_size=128, hidden_size=128, batch_first=True, bidirectional=True
        )

        # Attention
        self.attn = nn.Sequential(
            nn.Linear(256, 128), nn.Tanh(), nn.Dropout(0.35), nn.Linear(128, 1)
        )

        # Gate
        self.gate = nn.Sequential(nn.Linear(128, 128), nn.Sigmoid())

        # Fused FC
        self.fused_fc = nn.Sequential(
            nn.Linear(384, 128),  # 256 (LSTM) + 128 (Global)
            nn.ReLU(),
            nn.LayerNorm(128),
        )

        # Heads
        self.coral = CoralLayer(128, 5)
        self.cls_head = nn.Linear(128, 5)

    def forward(self, joint_features, global_features):
        # joint_features: (B, T, 429)
        # global_features: (B, T, 3) -> We might only need the last one or average?
        # Based on feature_engineering, global_features is (T, 3).
        # Usually global features are constant or we take the mean/max.
        # Let's assume we take the mean of global features over time or just use the sequence.
        # But global_mlp takes (3). If input is (B, T, 3), we probably process per frame or pool first.
        # Given the structure, it's likely we pool global features or they are expanded.
        # Let's assume global_features is (B, 3) passed in, or we pool it here.

        if global_features.dim() == 3:
            # Take mean over time
            global_emb = global_features.mean(dim=1)
        else:
            global_emb = global_features

        # Process Global
        global_emb = self.global_mlp(global_emb)

        # Gate Global
        gate = self.gate(global_emb)
        global_emb = global_emb * gate

        # Process Joint
        x = self.joint_fc(joint_features)  # (B, T, 128)

        # LSTM
        lstm_out, _ = self.lstm(x)  # (B, T, 256)

        # Attention
        attn_weights = self.attn(lstm_out)  # (B, T, 1)
        attn_weights = F.softmax(attn_weights, dim=1)

        context = torch.sum(lstm_out * attn_weights, dim=1)  # (B, 256)

        # Fusion
        fused = torch.cat([context, global_emb], dim=1)  # (B, 384)
        embedding = self.fused_fc(fused)  # (B, 128)

        # Heads
        coral_logits = self.coral(embedding)
        cls_logits = self.cls_head(embedding)

        return coral_logits, cls_logits


def load_model(model_path):
    model = GolfSwingModel()
    state_dict = torch.load(model_path, map_location="cpu")

    # Handle if state_dict is inside a key (e.g. 'model_state_dict')
    if "model_state_dict" in state_dict:
        state_dict = state_dict["model_state_dict"]

    model.load_state_dict(state_dict)
    model.eval()
    return model
