from sklearn.linear_model import LogisticRegression


class Model:
    def __init__(self, model_type="logistic_regression"):
        if model_type == "logistic_regression":
            self.model = LogisticRegression()
        else:
            raise ValueError(f"Model type {model_type} is not supported")

    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)

    def predict(self, X_test):
        return self.model.predict(X_test)
