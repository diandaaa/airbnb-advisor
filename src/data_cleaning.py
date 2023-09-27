def convert_tf_columns_to_bool(df):
    """
    Convert columns in a DataFrame containing 't' and 'f' to boolean.

    Parameters:
    df (DataFrame): DataFrame to modify
    """
    for col in df.columns:
        unique_vals = df[col].dropna().unique()
        if set(unique_vals) == {"t", "f"}:
            df[col] = df[col].apply(lambda val: 1 if val == "t" else 0)

def convert_percent_columns_to_float(df):
    """
    Convert columns in a DataFrame containing percentages (e.g., "50%") to float (e.g., 0.5).

    Parameters:
    df (DataFrame): DataFrame to modify
    """
    for col in df.columns:
        if df[col].dtype == 'O':  # Check if column type is object (typically for strings)
            if all(df[col].dropna().apply(lambda x: str(x).endswith('%'))):
                df[col] = df[col].str.rstrip('%').astype(float) / 100.0