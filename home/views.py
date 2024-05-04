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

def oncall(request):
    directory = settings.EXCEL_FILES_DIR
    excel_files = [f for f in os.listdir(directory) if f.endswith('.xlsx')]
    print("Excel files found:", excel_files)  # Debug output

    all_data = []

    for file in excel_files:
        file_path = os.path.join(directory, file)
        try:
            data = pd.read_excel(file_path, header=0, dtype=str)  # Add dtype=str parameter
            data.columns = pd.to_datetime(data.columns, errors='ignore')
            all_data.append(data)
        except Exception as e:
            messages.error(request, f"Failed to read file {file}: {str(e)}")

    if not all_data:
        messages.error(request, "No data found in Excel files")  # Error message
        return render(request, 'oncall.html')

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
        '9 AM - 9 AM': 'OnCall'
    }

    # Map names to their respective teams
    team_mapping = {
        'Shweta Chopde': {'team': 'DevOps Team', 'first_escalation': first_escalation, 'second_escalation': second_escalation, 'third_escalation': third_escalation},
        'Anjul Singh': {'team': 'Windows Team', 'first_escalation': first_escalation, 'second_escalation': second_escalation, 'third_escalation': third_escalation},
        'Sonali Mohapatra': {'team': 'DevOps Team', 'first_escalation': first_escalation, 'second_escalation': second_escalation, 'third_escalation': third_escalation},
        'Devi Vara Prasad Goddi': {'team': 'DevOps Team', 'first_escalation': first_escalation, 'second_escalation': second_escalation, 'third_escalation': third_escalation},
        'Vaibhav Thodsare': {'team': 'DevOps Team', 'first_escalation': first_escalation, 'second_escalation': second_escalation, 'third_escalation': third_escalation},
        'Rutuja Bajare': {'team': 'DevOps Team', 'first_escalation': first_escalation, 'second_escalation': second_escalation, 'third_escalation': third_escalation}
        # Add more mappings as needed
    }

    # Convert today's date to string in the format "Sat, May 4"
    today_str = datetime.today().strftime('%a, %b %d')
    print("Today's date string:", today_str)

    # Splitting date string to adjust the format
    parts = today_str.split(', ')
    date_parts = parts[1].split(' ')
    day = date_parts[1].lstrip('0')  # Remove leading zero if present
    today_str = f"{parts[0]}, {date_parts[0]} {day}"
    print("Adjusted Today's date string:", today_str)

    if today_str in all_data_df.columns:
        if request.method == 'POST':
            shift = request.POST.get('shift', '')  # Default to Morning if no shift selected
        else:
            shift = ""  # Default to Morning if no shift selected

        print("Selected shift:", shift)  # Debugging statement

        column_index = all_data_df.columns.get_loc(today_str)

        # Create a dictionary to store names for each team
        teams = {}
        for name, team_info in team_mapping.items():
            if team_info['team'] not in teams:
                teams[team_info['team']] = {'members': [], 'first_escalation': team_info['first_escalation'], 'second_escalation': team_info['second_escalation'], 'third_escalation': team_info['third_escalation']}
        
        for index, row in all_data_df.iterrows():
            shift_value = str(row.iloc[column_index])
            if shift_value == 'nan':
                continue
            mapped_shift = shift_labels.get(shift_value, None)
            if mapped_shift == shift:
                name = row['Name']
                if name in team_mapping:
                    team_info = team_mapping[name]
                    teams[team_info['team']]['members'].append({'name': name, 'contact': row['Contact Number'], 'first_escalation': team_info['first_escalation'], 'second_escalation': team_info['second_escalation'], 'third_escalation': team_info['third_escalation']})

        team_lists = [{'team': team, 'members': members['members'], 'first_escalation': members['first_escalation'], 'second_escalation': members['second_escalation'], 'third_escalation': members['third_escalation']} for team, members in teams.items()]

    else:
        messages.info(request, f"No data for {today_str}")
        team_lists = []

    selected_shift = request.POST.get('shift', '') if request.method == 'POST' else ''

    return render(request, 'oncall.html', {'team_lists': team_lists, 'selected_shift': selected_shift})

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