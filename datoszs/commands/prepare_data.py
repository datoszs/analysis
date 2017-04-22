from datoszs.db import global_connection
from datoszs.model import load_cases, load_documents, load_advocates
import frogress
import datoszs.output as output
import pandas as pd


def execute():
    with global_connection():
        result = []
        for adv in frogress.bar(load_advocates()):
            result.append(adv.public_info)
        result = pd.DataFrame(result)
        output.save_csv(result, 'cestiadvokati_advocates')
        result = []
        for case in frogress.bar(load_cases()):
            result.append(case.public_info)
        result = pd.DataFrame(result)
        output.save_csv(result, 'cestiadvokati_cases')
        result = []
        for doc in frogress.bar(load_documents()):
            result.append(doc.public_info)
        result = pd.DataFrame(result)
        output.save_csv(result, 'cestiadvokati_documents')
