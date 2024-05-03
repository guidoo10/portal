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
    return render(request, 'base.html')
    #return HttpResponse("This will be first page. JODDDDDDD!!!!!!!!!!!!!!!!!!!")

def about(request):
    #return HttpResponse("This will be ABOUT page. JODDDDDDD!!!!!!!!!!!!!!!!!!!")
    return render(request, 'about.html')

@login_required
def oncall(request, message=''):
    teams = []

    if request.method == 'POST':
        shift_input = request.POST.get('shift')
        shifts = [shift.strip() for shift in shift_input.split(',')]

        directory = r'C:\Users\anjulsi\OneDrive - AMDOCS\Backup Folders\Desktop\djangoproject\Cloudportal\template\excel'

        excel_files = [f for f in os.listdir(directory) if f.endswith('.xlsx')]

        all_data = []

        for file in excel_files:
            file_path = os.path.join(directory, file)
            data = pd.read_excel(file_path)
            all_data.append(data)

        all_data_df = pd.concat(all_data, ignore_index=True)

        today = pd.to_datetime(datetime.today().strftime('%Y-%m-%d'))

        filtered_data = all_data_df[(all_data_df['Shift'].str.lower().isin([shift.lower() for shift in shifts])) &
                                    (all_data_df['Start Date'] <= today) & (all_data_df['End Date'] >= today)]

        grouped_data = filtered_data.groupby('Team')

        for team, data in grouped_data:
            teams.append({
                'team': team,
                'data': data[['Name', 'Start Date', 'End Date', 'Contact', 'First Escalation', 'Second Escalation']].values.tolist()
            })

    return render(request, 'oncall.html', {'message': message, 'teams': teams})

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