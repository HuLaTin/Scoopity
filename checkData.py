# import libraries
import pandas as pd
from pandas.api.types import is_numeric_dtype

# select data to check
dataCheck = pd.read_csv(r'Data\songLyricData.csv')

# print column names and shape
print(dataCheck.columns)
print(dataCheck.shape)

# check to confirm if correct columns are numeric
for i in dataCheck.columns:
    print(i + ': ' + str(is_numeric_dtype(dataCheck[i])))
    #is_numeric_dtype(dataCheck[i])
    #print(i + ' ' + is_numeric_dtype(dataCheck[i]))