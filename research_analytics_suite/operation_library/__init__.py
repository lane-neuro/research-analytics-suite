# This file serves as a registry for all operation classes in the operation_library package

from .MeanCalculation import MeanCalculation
from .ChiSquareTest import ChiSquareTest
from .CSVFileLoading import CSVFileLoading
from .DescriptiveStatistics import DescriptiveStatistics
from .FieldObservation import FieldObservation
from .FrequencyCount import FrequencyCount
from .GroupByOperations import GroupByOperations
from .InferentialStatistics import InferentialStatistics
from .ModeCalculation import ModeCalculation
from .MongoDBOperations import MongoDBOperations
from .MovingAverageCalculation import MovingAverageCalculation
from .RegressionAnalysis import RegressionAnalysis
from .SQLQueryExecution import SQLQueryExecution
from .StandardDeviationCalculation import StandardDeviationCalculation
from .SumCalculation import SumCalculation
from .SurveyResponseAnalysis import SurveyResponseAnalysis
from .T_test import T_test
from .Tokenization import Tokenization
from .TrainTestSplit import TrainTestSplit
from .WordCount import WordCount

# Export a simple registry the manifest can iterate
OPERATIONS = [
    MeanCalculation,
    ChiSquareTest,
    CSVFileLoading,
    DescriptiveStatistics,
    FieldObservation,
    FrequencyCount,
    GroupByOperations,
    InferentialStatistics,
    ModeCalculation,
    MongoDBOperations,
    MovingAverageCalculation,
    RegressionAnalysis,
    SQLQueryExecution,
    StandardDeviationCalculation,
    SumCalculation,
    SurveyResponseAnalysis,
    T_test,
    Tokenization,
    TrainTestSplit,
    WordCount,
]
