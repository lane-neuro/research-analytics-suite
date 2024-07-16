import os

from research_analytics_suite.commands import link_class_commands, command
from research_analytics_suite.utils import CustomLogger


# from research_analytics_suite.operation_manager import BaseOperation


@link_class_commands
class MachineLearning:
    def __init__(self, data=None, model_type="logistic_regression",
                 name="MachineLearningOperation"):
        # super().__init__(name=name, func=self.evaluate_model)
        self._logger = CustomLogger()
        self.name = name
        self.data = data

        from research_analytics_suite.operation_manager.control.OperationControl import OperationControl
        self.operation_control = OperationControl()

        self.target = None

        from research_analytics_suite.analytics import Model
        self.model = Model(model_type=model_type)

        from research_analytics_suite.analytics import Preprocessor
        self.preprocessor = Preprocessor()

        self.preprocessed_data = None
        self.data_loader_operation = None
        self.data_extractor_operation = None
        self.transformed_data = None
        self.train_operation = None
        self.eval_operation = None

    @command
    async def load_data(self, file_path=None, data_destination=os.path.join(os.getcwd(), "../data")):
        """Initialize DataLoader operation."""
        try:
            '''
            self.data_loader_operation = await self._operation_control.operation_manager.add_operation(
                operation_type=DataLoader, name="ML_dataLoader",
                transformed_data=self.transformed_data, data_destination=data_destination)'''
            return self.data_loader_operation
        except Exception as e:
            self._logger.error(e, self.name)

    @command
    async def extract_data(self, file_path):
        """Extract data from the given file path."""
        # self.data_extractor_operation = await self._operation_control.operation_manager.add_operation(
        #    operation_type=DataExtractor, data_source=file_path, data_format='csv')
        return await self.data_extractor_operation.execute()

    @command
    def preprocess_data(self, data):
        """Preprocess the data using the Preprocessor."""
        # preprocessed_data = self.preprocessor.fit_transform(data)
        # self.data_loader_operation.transformed_data = preprocessed_data
        # return preprocessed_data
        pass

    @command
    def split_data(self, data, target_column, test_size=0.2, random_state=42):
        """Split the data into training and validation sets."""
        self.target = data[target_column]
        self.data = data.drop(columns=[target_column])

        from research_analytics_suite.analytics import MLTrainingOperation
        self.train_operation = MLTrainingOperation(
            model=self.model,
            data=self.data,
            target=self.target,
            test_size=test_size,
            random_state=random_state
        )
        # self.add_child_operation(self.train_operation)

    @command
    async def evaluate_model(self, test_data, test_target):
        """Initialize and evaluate the machine learning model."""

        # from research_analytics_suite.analytics import MLEvaluationOperation
        # self.eval_operation = MLEvaluationOperation(
        #     model=self.model,
        #     test_data=test_data,
        #     test_target=test_target
        # )

        return None

    async def _evaluate_model(self):
        await self.eval_operation.start()
        await self.eval_operation.execute()
        return self.eval_operation.result

    @command
    def predict(self, data):
        """Make predictions using the trained model."""

        from research_analytics_suite.analytics import Predictor
        return Predictor.predict(self.model, data)

    @command
    def get_model(self):
        """Get the trained model."""
        return self.model
