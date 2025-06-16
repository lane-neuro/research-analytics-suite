from sklearn.metrics import accuracy_score, precision_score, recall_score


class Metrics:
    @staticmethod
    def calculate_metrics(y_true, y_pred):
        """Calculate and return evaluation metrics."""
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average='weighted')
        recall = recall_score(y_true, y_pred, average='weighted')
        return {"accuracy": accuracy, "precision": precision, "recall": recall}
