import os
import shutil
from datetime import datetime

#TODO: Agent wrote this, so I'm not sure if its validity
def save_csv_file(csv_file, filename=None):
    """
    Saves a CSV file to the imported_files folder.
    
    Args:
        csv_file: The CSV file (can be a file path string or file object)
        filename: Optional custom filename. If not provided, uses original name or timestamp
    
    Returns:
        str: Path to the saved file
    """
    if not os.path.exists('imported_files'):
        os.makedirs('imported_files')
    
    if filename is None:
        if isinstance(csv_file, str):
            filename = os.path.basename(csv_file)
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'imported_{timestamp}.csv'
    
    if not filename.endswith('.csv'):
        filename += '.csv'
    
    destination_path = os.path.join('imported_files', filename)
    
    if isinstance(csv_file, str):
        shutil.copy(csv_file, destination_path)
    else:
        with open(destination_path, 'wb') as dest_file:
            shutil.copyfileobj(csv_file, dest_file)
    
    print("good morning")
    
    return destination_path

"""
from services.csv_file_services import save_csv_file

# Save a CSV file from a file path
saved_path = save_csv_file('/path/to/file.csv')

# Or save with a custom filename
saved_path = save_csv_file(csv_file_object, filename='my_data.csv')
"""