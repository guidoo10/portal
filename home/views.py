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
    directory = r'C:\Users\anjulsi\OneDrive - AMDOCS\Backup Folders\Desktop\djangoproject\Cloudportal\template\excel'
    excel_files = [f for f in os.listdir(directory) if f.endswith('.xlsx')]
    all_data = []  # Initialize the list

    for file in excel_files:
        file_path = os.path.join(directory, file)
        data = pd.read_excel(file_path, header=0)
        data.columns = pd.to_datetime(data.columns, errors='ignore')

        print("Data after reading from file:")
        print(data)

        all_data.append(data)

    all_data_df = pd.concat(all_data, ignore_index=True)

    print("All data combined:")
    print(all_data_df)



    # Create a dictionary with shift times as keys and labels as values
    shift_labels = {
        '7 AM - 4 PM': 'Morning',
        '9 AM - 6 PM': 'General',
        '9 AM - 9 AM': 'On call',
        '1 PM - 10 PM': 'Evening'
    }

# Get today's date
    today = datetime.today().strftime('%a, %b %#d')

# Filter data based on '9 AM - 9 AM' shift on today's date
    if today in all_data_df.columns:
    # Filter data based on '9 AM - 9 AM' shift on today's date
        all_data_df[today] = all_data_df[today].map(shift_labels)
        filtered_data = all_data_df[all_data_df[today] == 'On call']

        print("Filtered data:")
        print(filtered_data)

    # Prepare data for rendering
        teams = []
        for index, row in filtered_data.iterrows():
            teams.append({
                'name': row.iloc[0],
                'shift': row[today]
        })
    else:
        print(f"No data for {today}")
        teams = []

    return render(request, 'oncall.html', {'teams': teams})

def upload_file(request):
    if request.method == 'POST':
        try:
            myfile = request.FILES['myfile']
            directory = r'C:\Users\anjulsi\OneDrive - AMDOCS\Backup Folders\Desktop\djangoproject\Cloudportal\template\excel'
            fs = FileSystemStorage(location=directory)
            filename = fs.save(myfile.name, myfile)
            messages.success(request, 'File uploaded successfully!')
        except Exception as e:
            messages.error(request, 'File upload failed: ' + str(e))
        return redirect('oncall')
    else:
        return redirect('oncall')