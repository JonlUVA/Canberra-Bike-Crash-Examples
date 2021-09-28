# this is a working file where I will export some data for a better view
import openpyxl


from cycling_load_data import *
data_index_path = Path(DATA_FOLDER) / DATA_INDEX

working = load_data(data_index_path)

#working['rainfall']['canberra airport'].to_excel(r"C:\Users\Admin\OneDrive\Documents\assignment 2 working\rainfall.xlsx")
working['crash'].to_excel(r"C:\Users\Admin\OneDrive\Documents\assignment 2 working\crash.xlsx")
working['streetlight'].to_excel(r"C:\Users\Admin\OneDrive\Documents\assignment 2 working\streetlight.xlsx")
#print(working['cyclist'])