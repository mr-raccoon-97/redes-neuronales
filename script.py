from torch.nn import CrossEntropyLoss
from torch.optim import Adam

from models.classifiers import MLP as MLPCLS
from models.classifiers import GLU as GLUCLS

from src.adapters import register
from src.adapters.experiments import Experiments, Settings
from src.application.commands import TrainOverEpochs, CreateExperiment
from src.application.messagebus import Messagebus
from src.application.handlers import handle_create_experiment
from logging import basicConfig, INFO, getLogger

basicConfig(level=INFO)
logger = getLogger(__name__)

register('nn','mlp-cls-784-128-10-0.5-relu', lambda: MLPCLS(784, 128, 10, 0.5))
register('nn','mlp-cls-784-256-10-0.5-relu', lambda: MLPCLS(784, 256, 10, 0.5))
register('nn','mlp-cls-784-512-10-0.5-relu', lambda: MLPCLS(784, 512, 10, 0.5))

register('nn','glu-cls-784-128-10-0.5-relu', lambda: GLUCLS(784, 128, 10, 0.5))
register('nn','glu-cls-784-256-10-0.5-relu', lambda: GLUCLS(784, 256, 10, 0.5))
register('nn','glu-cls-784-512-10-0.5-relu', lambda: GLUCLS(784, 512, 10, 0.5))

register('criterion', 'cross-entropy', lambda: CrossEntropyLoss())
register('optimizer', 'adam-0.001', lambda model: Adam(model.parameters(), lr=0.001))

if __name__ == '__main__':
    from uvicorn import run
    from pymongo import MongoClient
    mongo_client = MongoClient('mongodb://localhost:27017')
    database = mongo_client['tests']
    directory = 'data/tests/weights'
    settings = Settings(device='cuda', workers=4, database=database, directory=directory)
    experiments = Experiments(settings)
    messagebus = Messagebus(experiments)

    try:

        handle_create_experiment(CreateExperiment(
            name='1234',
            nn='mlp-cls-784-128-10-0.5-relu',
            criterion='cross-entropy',
            optimizer='adam-0.001',
            batch_size=64
        ) , experiments)

        messagebus.enqueue(TrainOverEpochs(
            experiment='1234',
            dataset='mnist',
            epochs=10
        ))

    finally:
        messagebus.stop()
        mongo_client.close()