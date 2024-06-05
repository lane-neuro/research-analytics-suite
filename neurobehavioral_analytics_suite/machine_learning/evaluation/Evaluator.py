from sklearn.metrics import accuracy_score, precision_score, recall_score


class Evaluator:
    @staticmethod
    def evaluate(model, test_data, test_target):
        predictions = model.predict(test_data)
        accuracy = accuracy_score(test_target, predictions)
        precision = precision_score(test_target, predictions, average='weighted')
        recall = recall_score(test_target, predictions, average='weighted')
        return {"accuracy": accuracy, "precision": precision, "recall": recall}
