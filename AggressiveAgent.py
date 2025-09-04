import numpy as np
import json
import os
class AggressiveAgent:
    def __init__(self, n_features, lr=0.01, save_file="aggressive_agent.json"):
        self.lr = lr
        self.save_file = save_file

        if os.path.exists(self.save_file):
            try:
                self.load()
                if any(np.isnan(b) for b in self.beta):
                    raise ValueError("NaN encontrado")
            except:
                self.beta = np.random.randn(n_features + 1).tolist()
        else:
            self.beta = np.random.randn(n_features + 1).tolist()


    def predict(self, X):
        X = np.insert(X, 0, 1)
        return float(np.dot(self.beta, X))

    def decide_action(self, state):
        dx, dy = state
        norm = np.linalg.norm([dx, dy])
        if norm < 1e-8:
            return np.array([0, 0])
        return 1.5 * np.array([dx / norm, dy / norm])

    def update(self, X, y_true):
        X_with_bias = np.insert(X, 0, 1)
        y_pred = np.dot(self.beta, X_with_bias)
        
        error = y_true - y_pred
        error = np.clip(error, -1.0, 1.0)  # limita erro
        
        gradient = self.lr * error * X_with_bias
        new_beta = np.array(self.beta) + gradient
        
        # Evita NaN
        if np.any(np.isnan(new_beta)) or np.any(np.isinf(new_beta)):
            print("Atualização inválida detectada (NaN/Inf). Ignorando.")
            return
        
        self.beta = new_beta.tolist()

    def save(self):
        with open(self.save_file, "w") as f:
            json.dump({"beta": self.beta}, f)

    def load(self):
        try:
            with open(self.save_file, "r") as f:
                data = json.load(f)
                self.beta = data["beta"]
        except:
            raise FileNotFoundError()
