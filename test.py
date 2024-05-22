result_MENO has 46 columns result_MEOR has 36 columns both have empty values result_MENO has 13 empty values at last 13 columns whereas result_MEOR has four empty columns value but generating csv file showing both has 13 columns value which si empty

Edit
If the columns of the two DataFrames are different and you want to concatenate them while maintaining their distinct structures (and handling the missing values appropriately), you can follow these steps:

1. **Align columns**: Ensure both DataFrames have all possible columns, filling with `NaN` where columns are missing.
2. **Concatenate DataFrames**: Perform the concatenation.
3. **Save the resulting DataFrame to a CSV without headers**: Use `header=False`.

Here's how you can do it:

 meor_columns = ['Order Event', 'Fix_Col_0', 'FirmROID', 'MsgType', 'CAT_IM_ID', 'Date', 'Order ID',
                            'Symbol',
                            'Fix_Col_1', 'TimeStamp', 'Fix_Col_2', 'Fix_Col_3', 'Fix_Col_4', 'Fix_Col_5', 'SideType',
                            'Price',
                            'Quantity', 'Fix_Col_6', 'OrderType', 'TIF', 'Trading_Session', 'FDID', 'Fix_Col_7',
                            'Fix_Col_8',
                            'Fix_Col_9', 'Fix_Col_10', 'Fix_Col_11', 'Fix_Col_12', 'Fix_Col_13', 'Fix_Col_14',
                            'Fix_Col_15',
                            'Fix_Col_16']

            meno_columns = ['Order Event', 'Fix_Col_0', 'FirmROID', 'MsgType', 'CAT_IM_ID',
                       'Date', 'Order ID', 'Symbol', 'TimeStamp', 'Fix_Col_1', 'Fix_Col_2', 'Fix_Col_3', 'Fix_Col_4',
                       'Fix_Col_5', 'Fix_Col_6', 'Fix_Col_7', 'Fix_Col_8', 'SideType', 'Price', 'Quantity', 'Fix_Col_9',
                       'OrderType', 'TIF', 'Trading_Session', 'Fix_Col_10', 'Fix_Col_11', 'FDID', 'Acc Type',
                       'Fix_Col_12',
                       'Fix_Col_13', 'Fix_Col_14', 'Fix_Col_15', 'Fix_Col_16', 'Fix_Col_17', 'Fix_Col_18', 'Fix_Col_19',
                       'Fix_Col_20', 'Fix_Col_21', 'Fix_Col_22', 'Fix_Col_23', 'Fix_Col_24', 'Fix_Col_25', 'Fix_Col_26',
                       'Fix_Col_27', 'Fix_Col_28', 'Fix_Col_29']

```python
import pandas as pd

# Sample DataFrames with different columns
result_MENO = pd.DataFrame({
    'A': [1, 2, 3],
    'B': [4, 5, 6],
    'C': [7, 8, 9],
    # Assuming the last 13 columns are empty
    'Empty1': [None, None, None],
    'Empty2': [None, None, None],
    # Add more empty columns as necessary
})

result_MEOR = pd.DataFrame({
    'D': [10, 11, 12],
    'E': [13, 14, 15],
    # Assuming there are only 4 empty columns
    'Empty1': [None, None, None],
    'Empty2': [None, None, None],
    'Empty3': [None, None, None],
    'Empty4': [None, None, None]
})

# Find the union of all columns
all_columns = list(set(result_MENO.columns) | set(result_MEOR.columns))

# Reindex DataFrames to ensure they have the same columns, filling missing values with NaN
result_MENO = result_MENO.reindex(columns=all_columns)
result_MEOR = result_MEOR.reindex(columns=all_columns)

# Concatenate the DataFrames
result_concat = pd.concat([result_MENO, result_MEOR])

# Save the resulting DataFrame to a CSV file without headers
result_concat.to_csv('output.csv', header=False, index=False)
```

In this script:

1. **Union of all columns**: `all_columns` contains all unique columns from both `result_MENO` and `result_MEOR`.
2. **Reindexing**: Both DataFrames are reindexed to have the same set of columns, filling in `NaN` where necessary. This ensures that when concatenated, all columns align correctly.
3. **Concatenation**: The two DataFrames are concatenated along the rows.
4. **Saving to CSV**: The concatenated DataFrame is saved to `output.csv` without column headers or row indices.

This approach ensures that the DataFrames are aligned correctly, and empty columns are handled as expected in the resulting CSV file.
