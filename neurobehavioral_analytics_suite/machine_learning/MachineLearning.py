import os

from neurobehavioral_analytics_suite.data_engine.data_processing.DataExtractor import DataExtractor
from neurobehavioral_analytics_suite.data_engine.data_processing.DataLoader import DataLoader
from neurobehavioral_analytics_suite.machine_learning import Model, Preprocessor, MLTrainingOperation, \
    MLEvaluationOperation, Predictor
from neurobehavioral_analytics_suite.operation_manager.operations.Operation import Operation
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler
import asyncio


class MachineLearning(Operation):
    def __init__(self, operation_control, data=None, error_handler=ErrorHandler, model_type="logistic_regression",
                 name="MachineLearningOperation"):
        super().__init__(name=name, error_handler=error_handler, func=self.evaluate_model)
        self.name = name
        self.data = data
        self.operation_control = operation_control
        self.target = None
        self.model = Model(model_type=model_type)
        self.preprocessor = Preprocessor()
        self.preprocessed_data = None
        self.data_loader_operation = None
        self.data_extractor_operation = None
        self.transformed_data = None
        self.train_operation = None
        self.eval_operation = None

    async def load_data(self, file_path=None, data_destination=os.path.join(os.getcwd(), "../data")):
        """Initialize DataLoader operation."""
        try:
            self.data_loader_operation = await self.operation_control.operation_manager.add_operation(
                operation_type=DataLoader, name="ML_dataLoader", error_handler=self._error_handler,
                transformed_data=self.transformed_data, data_destination=data_destination)
            print("MachineLearningOperation.load_data: Loading data...")
            return self.data_loader_operation
        except Exception as e:
            self._error_handler.handle_error(e, self.name)

    async def extract_data(self, file_path):
        """Extract data from the given file path."""
        self.data_extractor_operation = await self.operation_control.operation_manager.add_operation(
            operation_type=DataExtractor, error_handler=self._error_handler, data_source=file_path, data_format='csv')
        return await self.data_extractor_operation.execute()

    def preprocess_data(self, data):
        """Preprocess the data using the Preprocessor."""
        preprocessed_data = self.preprocessor.fit_transform(data)
        self.data_loader_operation.transformed_data = preprocessed_data
        return preprocessed_data

    def split_data(self, data, target_column, test_size=0.2, random_state=42):
        """Split the data into training and validation sets."""
        self.target = data[target_column]
        self.data = data.drop(columns=[target_column])
        self.train_operation = MLTrainingOperation(
            error_handler=self._error_handler,
            model=self.model,
            data=self.data,
            target=self.target,
            test_size=test_size,
            random_state=random_state
        )
        self.add_child_operation(self.train_operation)

    async def execute(self):
        """Execute the machine learning operations in sequence."""
        print("MachineLearningOperation.execute: Executing machine learning operations...")
        await super().execute()

    async def evaluate_model(self, test_data, test_target):
        """Initialize and evaluate the machine learning model."""
        self.eval_operation = MLEvaluationOperation(
            error_handler=self._error_handler,
            model=self.model,
            test_data=test_data,
            test_target=test_target
        )
        return await self._evaluate_model()

    async def _evaluate_model(self):
        await self.eval_operation.start()
        await self.eval_operation.execute()
        return self.eval_operation.result

    def predict(self, data):
        """Make predictions using the trained model."""
        return Predictor.predict(self.model, data)

    def get_model(self):
        """Get the trained model."""
        return self.model
