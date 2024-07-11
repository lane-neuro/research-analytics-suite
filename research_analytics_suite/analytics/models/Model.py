from sklearn.linear_model import LogisticRegression

from research_analytics_suite.commands import command, register_commands


@register_commands
class Model:
    def __init__(self, model_type="logistic_regression"):
        if model_type == "logistic_regression":
            self.model = LogisticRegression()
        else:
            raise ValueError(f"Model type {model_type} is not supported")

    @command
    def train(self, x_train, y_train):
        self.model.fit(x_train, y_train)

    @command
    def predict(self, x_test):
        return self.model.predict(x_test)
