"""
F1 Lap Time Analysis Script

Description:
    This script analyzes Formula 1 lap times from a PDF file. It extracts lap time data for specified drivers,
    processes this data, and then generates two plots:
    1. Lap times for selected drivers over the course of the race.
    2. Lap times for selected drivers as a percentage of the fastest lap in the race.

Input PDF Format:
    The script expects a text-based PDF file as input. Scanned image PDFs will not work.
    The PDF should contain race lap information where driver names are clearly listed, followed by their
    lap times. The lap times are expected to be in the format M.SS.mmm (e.g., 1.23.456), where M is minutes,
    SS is seconds, and mmm is milliseconds. The script uses regular expressions to find driver names
    (from a predefined list) and these lap time patterns.

    The DRIVERS list in the script may need to be updated based on the specific race season/PDF content
    to ensure all relevant drivers are captured.

Command-Line Usage:
    python F1_lap_analysis.py <path_to_pdf_file.pdf>

    Example:
        python F1_lap_analysis.py "C:/Users/YourName/Downloads/2023_Bahrain_GP_Laps.pdf"

Key Dependencies:
    - PyPDF2: For reading and extracting text from PDF files.
    - matplotlib: For generating plots.

Ensure these dependencies are installed in your Python environment.
You can typically install them using pip:
    pip install PyPDF2 matplotlib
"""
import PyPDF2
import argparse # Added for command-line argument parsing
import os # Added to extract filename for plot titles
import re
import matplotlib.pyplot as plt

FIG_SIZE = (8,6)
# FILE = 'N:/Downloads/race_laps.pdf' # Removed hardcoded file path
# List of drivers, may need updates for different F1 seasons
DRIVERS = ['Daniel RICCIARDO', 'Lando NORRIS', 
                'Sebastian VETTEL', 'Kimi RAIKKONEN',
                'Romain GROSJEAN', 'Pierre GASLY',
                'Sergio PEREZ', 'Charles LECLERC',
                'Lance STROLL', 'Kevin MAGNUSSEN',
                'Alexander ALBON', 'Daniil KVYAT',
                'Nico HULKENBERG', 'Max VERSTAPPEN',
                'Lewis HAMILTON', 'Carlos SAINZ',
                'George RUSSELL', 'Valtteri BOTTAS',
                'Robert KUBICA', 'Antonio GIOVINAZZI']

def get_lap_times(pdfReader, drivers):
    num_pages =  pdfReader.numPages
    lap_times_raw = [] # Renamed to avoid confusion with the output dict
    for i in range(num_pages):
        pageObj = pdfReader.getPage(i)
        text = pageObj.extractText()
        # Lap time regex expects M.SS.mmm format (e.g., 1.23.456)
        # Driver names are joined by '|' for the regex
        lap_times_raw += re.findall('|'.join(drivers)+
                                r'|[0-9]\.[0-9]{2}\.[0-9]{3}', text) # Corrected regex for M.SS.mmm
        
    driver_lap_times = {}
    # Initialize all drivers from DRIVERS list to handle cases where some drivers might not have times
    for driver_name in drivers:
        driver_lap_times[driver_name] = []

    if not lap_times_raw: # Handle case where no data is extracted
        print("Warning: No drivers or lap times found in the PDF. Check PDF content and DRIVERS list.")
        return driver_lap_times # Return initialized empty dict

    curr_driver = ""
    # Attempt to find the first driver to start processing
    first_driver_found = False
    for item_index, item in enumerate(lap_times_raw):
        if item in drivers:
            curr_driver = item
            lap_times_raw = lap_times_raw[item_index:] # Start processing from the first found driver
            first_driver_found = True
            break
    
    if not first_driver_found:
        print("Error: No recognized driver names found in extracted data. Cannot process lap times.")
        return driver_lap_times # Return initialized empty dict if no driver is found

    for lap_data in lap_times_raw:
        if lap_data in drivers:
            curr_driver = lap_data
        else:
            # Attempt to parse as lap time
            try:
                # Lap time format is M.SS.mmm
                parts = lap_data.split('.')
                if len(parts) == 3: # Ensure it's in the expected M.SS.mmm format
                    minutes = int(parts[0])
                    # secs_milliseconds = float(f"{parts[1]}.{parts[2]}") # Original approach
                    seconds = int(parts[1])
                    milliseconds = int(parts[2])
                    total_seconds = (minutes * 60) + seconds + (milliseconds / 1000.0)
                    
                    if curr_driver: # Ensure there's a current driver context
                        driver_lap_times[curr_driver].append(round(total_seconds, 3))
                    else:
                        print(f"Warning: Skipping lap time {lap_data} as no current driver is set.")
                else:
                    print(f"Warning: Skipping unrecognized data or malformed time (not M.SS.mmm): {lap_data}")

            except ValueError: 
                # This might happen if lap_data is not a time and also not a listed driver
                print(f"Warning: Skipping unrecognized data or malformed time: {lap_data}")
            except IndexError:
                 print(f"Warning: Malformed time string encountered: {lap_data}")

    return driver_lap_times

def plot_times(lap_times, pdf_filename):
    drivers_of_interest = ['Sebastian VETTEL', 'Charles LECLERC',
                       'Lewis HAMILTON', 'Valtteri BOTTAS',
                       'Max VERSTAPPEN']
    
    plt.style.use('tableau-colorblind10')
    plt.figure(figsize=FIG_SIZE)
    plt.xlabel('Lap Number')
    plt.ylabel('Lap Time (seconds)')
    plt.title(f'F1 Lap Time Analysis for {pdf_filename}') # Updated title
    
    max_laps = 0
    for driver_name in drivers_of_interest:
        if driver_name in lap_times and lap_times[driver_name]:
            if len(lap_times[driver_name]) > max_laps:
                max_laps = len(lap_times[driver_name])
    
    if max_laps > 0:
        plt.xticks([i for i in range(0, max_laps + 1, 5)], rotation=90)
    # Removed plt.ylim to allow auto-scaling

    for driver, times in lap_times.items():
        if driver in drivers_of_interest and times: 
            plt.plot([i+1 for i in range(len(times))], times, 'o-', # Lap numbers start from 1
                      linewidth=1, markersize=2.5,
                      label=driver.split(' ')[-1][:3]) # Use last name for label
    
    plt.grid(axis='y', linestyle='--')
    plt.legend()
    
def plot_percent_times(lap_times, pdf_filename):
    drivers_of_interest = ['Sebastian VETTEL', 'Charles LECLERC',
                       'Lewis HAMILTON', 'Valtteri BOTTAS',
                       'Max VERSTAPPEN']
    
    fastest_lap = float('inf')
    valid_lap_times_exist = False
    for driver_name in lap_times: # Check all drivers in lap_times for the actual fastest lap
        if lap_times[driver_name]: 
            current_min_lap = min(lap_times[driver_name])
            if current_min_lap < fastest_lap:
                fastest_lap = current_min_lap
            valid_lap_times_exist = True # Mark that at least one valid lap time was found
            
    percent_times = {}
    # Initialize percent_times for all drivers to ensure structure
    for driver_name in drivers:
        percent_times[driver_name] = []

    if not valid_lap_times_exist or fastest_lap == float('inf'):
        print("No valid lap times found to calculate percentages or the fastest lap.")
    else:
        for driver, times in lap_times.items():
            if not times: 
                continue
            for curr_lap_time in times:
                if fastest_lap == 0: 
                    percent_times[driver].append(0)
                else:
                    percent_times[driver].append(curr_lap_time/fastest_lap*100)
            
    plt.style.use('tableau-colorblind10')
    plt.figure(figsize=FIG_SIZE)
    plt.xlabel('Lap Number')
    plt.ylabel('Percent of fastest lap (%)') # Added unit
    plt.title(f'F1 Lap Time Analysis for {pdf_filename} (vs Fastest Lap)')

    max_laps = 0
    for driver_name in drivers_of_interest:
        if driver_name in percent_times and percent_times[driver_name]:
            if len(percent_times[driver_name]) > max_laps:
                max_laps = len(percent_times[driver_name])

    if max_laps > 0:
        plt.xticks([i for i in range(0, max_laps + 1, 5)], rotation=90)
    # Removed plt.ylim for auto-scaling

    for driver, times in percent_times.items():
        if driver in drivers_of_interest and times: 
            plt.plot([i+1 for i in range(len(times))], times, 'o-', # Lap numbers start from 1
                      linewidth=1, markersize=2.5,
                      label=driver.split(' ')[-1][:3]) # Use last name for label
        
    plt.grid(axis='y', linestyle='--')
    plt.legend()
    
    return percent_times # Return even if empty for consistency
            

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze F1 lap times from a PDF file.')
    parser.add_argument('pdf_file', type=str, help='Path to the PDF file containing lap times.')
    args = parser.parse_args()

    try:
        with open(args.pdf_file, 'rb') as pdfFileObj:
            pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
            if pdfReader.isEncrypted:
                print(f"Error: PDF file {args.pdf_file} is encrypted. Please decrypt it first.")
            else:
                lap_times = get_lap_times(pdfReader, DRIVERS)

                if not lap_times or all(not l for l in lap_times.values()):
                    print(f"No lap times could be extracted or processed from {args.pdf_file}. Exiting.")
                else:
                    pdf_filename_for_title = os.path.basename(args.pdf_file)
                    
                    plot_times(lap_times, pdf_filename_for_title)
                    percent_times = plot_percent_times(lap_times, pdf_filename_for_title)
                    
                    if not plt.get_fignums(): 
                        print("No data to plot.")
                    else:
                        plt.show()

    except FileNotFoundError:
        print(f"Error: PDF file not found at {args.pdf_file}")
    except PyPDF2.utils.PdfReadError: 
        print(f"Error: Could not read PDF file {args.pdf_file}. It might be corrupted or not a valid PDF.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
