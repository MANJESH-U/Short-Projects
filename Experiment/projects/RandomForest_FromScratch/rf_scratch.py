import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

iris = load_iris()
X, y = iris.data, iris.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

class DecisionStump:
    def fit(self, X, y):
        self.feature_index = 0
        self.threshold = np.mean(X[:,0])
        self.label_left = 0
        self.label_right = 1
    def predict(self, X):
        return np.where(X[:, self.feature_index] < self.threshold, self.label_left, self.label_right)

class RandomForest:
    def __init__(self, n_trees=5):
        self.trees = [DecisionStump() for _ in range(n_trees)]
    def fit(self, X, y):
        for tree in self.trees:
            indices = np.random.choice(len(X), len(X))
            tree.fit(X[indices], y[indices])
    def predict(self, X):
        preds = np.array([tree.predict(X) for tree in self.trees])
        return np.apply_along_axis(lambda x: np.bincount(x).argmax(), axis=0, arr=preds)

rf = RandomForest(n_trees=10)
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)
print('Accuracy:', accuracy_score(y_test, y_pred))
