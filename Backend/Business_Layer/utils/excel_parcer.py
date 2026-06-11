import pandas as pd
import numpy as np


def parse_excel(file):

    df = pd.read_excel(file.file)

    # Convert NaN to None
    df = df.replace({np.nan: None})

    return df.to_dict(orient="records")
