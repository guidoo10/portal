from django.shortcuts import render, HttpResponse
import pandas as pd
import os
from datetime import datetime
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):
    return render(request, 'index.html')
    #return HttpResponse("This will be first page. JODDDDDDD!!!!!!!!!!!!!!!!!!!")

def about(request):
    #return HttpResponse("This will be ABOUT page. JODDDDDDD!!!!!!!!!!!!!!!!!!!")
    return render(request, 'about.html')

@login_required

def oncall(request, message=''):
    directory = settings.EXCEL_FILES_DIR  # Assuming settings is imported
    excel_files = [f for f in os.listdir(directory) if f.endswith('.xlsx')]
    all_data = []  # Initialize the list

    for file in excel_files:
        file_path = os.path.join(directory, file)
        try:
            data = pd.read_excel(file_path, header=0)
            data.columns = pd.to_datetime(data.columns, errors='ignore')
            all_data.append(data)
        except Exception as e:
            messages.error(request, f"Failed to read file {file}: {str(e)}")

    all_data_df = pd.concat(all_data, ignore_index=True)

    # Define static values for first, second, and third escalation
    first_escalation = "Shweta Chopde(9763958955),Anjul Singh(7275177775)"
    second_escalation = "Praveen Kumar Tiwari (9972590103),Shivaji Bhosle(9689374727),Abhishek kumar singh (8586000516)"
    third_escalation = "Sunil Kumar(9767831024)"

    # Define shift label mapping dictionary
    shift_labels = {
        '7 AM - 4 PM': 'Morning',
        '9 AM - 6 PM': 'General',
        '1 PM - 10 PM': 'Evening',
        '9 AM - 9 AM': 'Oncall'
    }

    # Convert today's date to string in the format "Sat, May 4"
    today_str = datetime.today().strftime('%a, %b %d')

    if today_str in all_data_df.columns:
        if request.method == 'POST':
            shift = request.POST.get('shift', '')  # Default to Morning if no shift selected
        else:
            shift = ""  # Default to Morning if no shift selected

        print("Selected shift:", shift)  # Debugging statement

        column_index = all_data_df.columns.get_loc(today_str)

        names = []
        contacts = []

        for index, row in all_data_df.iterrows():
            shift_value = str(row.iloc[column_index])
            if shift_value == 'nan':
                continue
            mapped_shift = shift_labels.get(shift_value, None)
            if mapped_shift == shift:
                names.append(row['Name'])
                contacts.append(row['Contact Number'])

        # Add static escalation values for all rows
        first_escalations = [first_escalation] * len(names)
        second_escalations = [second_escalation] * len(names)
        third_escalations = [third_escalation] * len(names)

        teams = list(zip(names, contacts, first_escalations, second_escalations, third_escalations))
    else:
        messages.info(request, f"No data for {today_str}")
        teams = []

    return render(request, 'oncall.html', {'teams': teams})

def upload_file(request):
    if request.method == 'POST':
        try:
            myfile = request.FILES['myfile']
            directory = settings.EXCEL_FILES_DIR
            fs = FileSystemStorage(location=directory)
            filename = fs.save(myfile.name, myfile)
            messages.success(request, 'File uploaded successfully!')
        except Exception as e:
            messages.error(request, 'File upload failed: ' + str(e))
        return redirect('oncall')
    else:
        return redirect('oncall')
