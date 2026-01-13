import os
import pythoncom
import win32com.client
from threading import Thread

def convert(
    input_dir_name,
    output_subdir_name='converted',
    fast=True,
    chunk_size=4,
    skip_completed=True
):
    """
    input_subdir_name: absolute path containing input files in .ppt or .pptx formats
    output_subdir_name: sub-directory name which will be created within input_subdir_name
    fast: Uses threading if set to True, else not
    chunk_size: if set to None, creates threads for all files in dir, else only creates atmost chunk_size threads at a time
    skip_completed: skips converted files if found in output dir and match the filenames from the input dir
    """

    get_new_path = lambda f: os.path.join(os.path.dirname(f), output_subdir_name, os.path.basename(f)).replace('.pptx', '').replace('.ppt', '')
    get_file_name = lambda x: os.path.splitext(os.path.basename(x))[0]

    if not os.path.isdir(input_dir_name):
        raise OSError(f"No directory found with name: {input_dir_name}")

    output_dir_name = os.path.join(input_dir_name, output_subdir_name)
    if not os.path.isdir(output_dir_name):
        os.mkdir(output_dir_name)

    files = [os.path.join(input_dir_name, i) for i in os.listdir(input_dir_name)]
    files = [i for i in files if os.path.isfile(i) and '.ppt' in os.path.splitext(i)[1]]

    out_files = [
        os.path.join(output_dir_name, i) for i in os.listdir(output_dir_name)
        if os.path.isfile(os.path.join(output_dir_name, i)) and
        os.path.splitext(os.path.join(output_dir_name, i))[1] == '.pdf'
    ]
    out_files = [get_file_name(i) for i in out_files]

    unconverted_files = [i for i in files if get_file_name(i) not in out_files]
    unconverted_files = [i for i in unconverted_files if not os.path.splitext(os.path.basename(i))[0].startswith('~$')]

    print(f"Input Directory: {input_dir_name}")
    print(f"Output Directory: {output_dir_name}\n")
    # print(unconverted_files)

    # return

    if fast:
        file_chunks = [unconverted_files[i:i + chunk_size] for i in range(0, len(unconverted_files), chunk_size)]

        # Start all threads

        for fci, files in enumerate(file_chunks):
            print(f"Processing chunk {fci+1} of {len(file_chunks)}")

            threads = []
            for idx, file in enumerate(files):
                print(f"  > Processing {idx+1} of {len(files)}")
                thread = Thread(target=PPTtoPDF, args=(file, get_new_path(file)))
                threads.append(thread)
                thread.start()

            # Wait for all threads to finish
            for thread in threads:
                thread.join()
    else:
        # Standard iterative loop
        for idx, file in enumerate(files):
            print(f"> Processing {idx+1} of {len(files)}")
            PPTtoPDF(file, get_new_path(file))

def PPTtoPDF(inputFileName, outputFileName, formatType=32):
    # Initialize COM in this thread
    pythoncom.CoInitialize()
    try:
        powerpoint = win32com.client.DispatchEx("Powerpoint.Application")
        powerpoint.Visible = 1

        if not outputFileName.endswith('.pdf'):
            outputFileName += ".pdf"

        deck = powerpoint.Presentations.Open(inputFileName)
        deck.SaveAs(outputFileName, formatType)  # formatType = 32 for ppt to pdf
        deck.Close()
        print(f"Saved {inputFileName} as {outputFileName}")
    except Exception as e:
        print(f"Error converting {inputFileName}: {e}")
    finally:
        powerpoint.Quit()
        pythoncom.CoUninitialize()  # Uninitialize COM

# Example usage
dir_ = r'D:\OneDrive - Manipal University Jaipur\Clg Studies\Sem 7\NLP\NLP-PPTs'
convert(dir_, fast=True)
