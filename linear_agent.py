import numpy as np
import json

class LinearAgent:
    def __init__(self, n_features, lr=0.01, save_file="agent.json"):
        self.beta = np.random.randn(n_features + 1).tolist()  # começa como lista
        self.lr = lr
        self.save_file = save_file

    def predict(self, X):
        X = np.insert(X, 0, 1)  # adiciona bias
        return float(np.dot(self.beta, X))

    def decide_action(self, state):
        dx, dy = state
        score_x = self.predict([dx, 0])
        score_y = self.predict([0, dy])
        move = np.array([np.sign(score_x), np.sign(score_y)])
        return move

    def update(self, X, y_true):
        X = np.insert(X, 0, 1)
        y_pred = np.dot(self.beta, X)
        error = y_true - y_pred
        self.beta = (np.array(self.beta) + self.lr * error * X).tolist()

    def save(self):
        """Salva os pesos em JSON"""
        with open(self.save_file, "w") as f:
            json.dump({"beta": self.beta}, f)

    def load(self):
        """Carrega pesos do JSON"""
        try:
            with open(self.save_file, "r") as f:
                data = json.load(f)
                self.beta = data["beta"]
        except FileNotFoundError:
            print("Arquivo de pesos não encontrado, iniciando com valores aleatórios.")
