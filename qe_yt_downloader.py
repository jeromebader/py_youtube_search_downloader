# QD Yt searcher and donwloader v0.1

# Importing the Libraries
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
from io import BytesIO
from tkinter import messagebox
import youtube_dl
import pytube
import os



# Function to fetch a thumbnail from the given image URL
def get_thumbnail(url):
    """
    Get a thumbnail image from the provided URL.

    Args:
        url (str): URL of the thumbnail image.

    Returns:
        ImageTk.PhotoImage: Thumbnail image in PhotoImage format.
    """
       
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img.thumbnail((120, 120))
    return ImageTk.PhotoImage(img)


# Function to render a thumbnail and title to the GUI widget
def add_thumbnail(img_url, i, title_duration):
    """
    Add a thumbnail image, title, and duration to the GUI widget.

    Args:
        img_url (str): URL of the thumbnail image.
        i (int): Index for placement in the grid.
        title_duration (str): Title, duration, and video ID as a semicolon-separated string.
    """

    img = get_thumbnail(img_url)
   
    title, duration, video_id = title_duration.split(';')
    max_chars_per_line = 40
    title_lines = [title[i:i+max_chars_per_line] for i in range(0, len(title), max_chars_per_line)]
    formatted_title = '\n'.join(title_lines)

    
    
    frame = ttk.Frame(root)
    frame.grid(row=i//3, column=i%3, padx=5, pady=5)  # Use the frame as the main widget in the grid
    
    title_label = ttk.Label(frame, text=f"{formatted_title}")
    title_label.pack(pady=5)  # Use some padding for better spacing

    btn = ttk.Button(frame, image=img, command=lambda: download_video(img_url))  # Button is a child of frame
    btn.photo = img
   
    btn.pack(pady=5)  # Use some padding for better spacing
    duration_label = ttk.Label(frame, text=f"Duration: {duration} ")
    duration_label.pack(pady=5)  # Use some padding for better spacing


# Download the selected video
def download_video(img_url):
    """
    Initiate the download of the selected video.

    Args:
        img_url (str): URL of the thumbnail image.
    """
    

    def extract_video_id(url):
        # Extracting the part of the URL between 'vi/' and '/0.jpg'
        start = url.find('vi/') + 3
        end = url.find('/0.jpg', start)
        video_id = url[start:end]
        return video_id
    
    video_id = extract_video_id(img_url)


    def hide_progress():
        # Hide the progress bar and label or reset their values
        progress_bar.grid_remove()  # or progress_bar['value'] = 0
        download_status_label.config(text="")

    def progress_function(stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage_of_completion = bytes_downloaded / total_size * 1000
        progress_bar['value'] = percentage_of_completion
        download_status_label.config(text=f"{int(percentage_of_completion)}% downloaded")
        root.update_idletasks()

        if percentage_of_completion == 100:
            download_status_label.config(text="Download complete!")
            root.after(5000, hide_progress)


    if not img_url:
        messagebox.showinfo("Info", "Please select a video first.")
        return 
    
    else:
        
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        yt = pytube.YouTube(url)
        yt.register_on_progress_callback(progress_function)

          # Create a frame for the progress bar and download status
        progress_frame = ttk.Frame(root)
        progress_frame.grid(row=6, column=0, columnspan=3, pady=5)  # Adjust the row and column

        # Create the progress bar
        progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=200, mode="determinate")
        progress_bar.grid(row=0, column=0, pady=5)
        messagebox.showinfo("Info", f"Downloading {url}...")

        # Create a label to display the download status
        download_status_label = ttk.Label(progress_frame, text="0% downloaded")
        download_status_label.grid(row=0, column=1, pady=5)

        current_directory = os.getcwd()
        yt.streams.get_highest_resolution().download(output_path=current_directory)
        

      
# Function to update the thumbnail display page
def update_display(page):
    """
    Update the GUI with a new page of thumbnails.

    Args:
        page (int): Page number to display.
    """
  
    global all_first_thumbnails
    global title_duration_thumbnail

    

    for widget in root.winfo_children():
        widget.grid_forget()

    start_index = page * 9  # Adjusting this for 3x3 grid (9 images per page)
    end_index = start_index + 9

    all_image_urls = all_first_thumbnails

   

    for i, (img_url, title_duration) in enumerate(zip(all_image_urls[start_index:end_index], title_duration_thumbnail[start_index:end_index])):
        add_thumbnail(img_url, i, title_duration)
    
    if page > 0:
        prev_button = ttk.Button(root, text="Previous", command=lambda: change_page(-1))
        prev_button.grid(row=3, column=0, pady=20)  # Adjusting the row to 3 to place navigation below the thumbnails
    
    if end_index < len(all_image_urls):
        next_button = ttk.Button(root, text="Next", command=lambda: change_page(1))
        next_button.grid(row=3, column=2, pady=20)  # Adjusting the row to 3 to place navigation below the thumbnails


# Start page for video search    !!! TO IMPROVE UX
def start_page ():
    """
    Create the start page for video search input.
    """

    def video_search():
        global all_first_thumbnails
        global title_duration_thumbnail
        all_first_thumbnails = []
        title_duration_thumbnail = []

        global current_page
        
        # Configuration for youtube_dl to only extract information, not download
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'force_generic_extractor': True,
        }

        # Get the text from the input field
        query = input_box.get()
        query_url = f"ytsearch100:{query}"  # This tells youtube_dl to search on YouTube for 100 results

    
        

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(query_url, download=False)
            print(info_dict)
            
            # Check if 'entries' key exists in the info_dict. If it does, it means videos were found.
            if 'entries' in info_dict:
                videos = info_dict['entries']

                print(videos)
                print('Videos found:')
                
                for video in videos:
                    title = video['title']
                    
                    duration = int(video.get('duration', 0))
                    formatted_duration = f"{duration // 60}:{duration % 60:02}"  # Convert seconds to "min:sec" format
                    

                    video_id = video['id']
                    title_duration_thumbnail.append(f"{title};{formatted_duration};{video_id}")

                    # The 'thumbnails' attribute in youtube_dl typically contains multiple thumbnails with different resolutions, we use the very first one
                    thumbnail_url = f'https://img.youtube.com/vi/{video_id}/0.jpg'
                    all_first_thumbnails.append(thumbnail_url)

        
            if all_first_thumbnails:
                     update_display(current_page)
            else:
                print ('error updating ')

            

    input_frame = ttk.Frame(root)
    input_frame.grid(row=5, column=0, columnspan=3, pady=5)

    input_label = ttk.Label(input_frame, text="Enter something:")
    input_label.grid(row=0, column=0, pady=5)
    input_box = ttk.Entry(input_frame)
    input_box.grid(row=0, column=1, pady=5)
    confirm_button = ttk.Button(input_frame, text="Confirm", command=video_search)
    confirm_button.grid(row=0, column=2, pady=5)
  

def change_page(direction):
    """
    Change the current page of thumbnails.

    Args:
        direction (int): Direction to navigate (1 for next, -1 for previous).
    """
    global current_page
    current_page += direction
    update_display(current_page)
    if current_page == 0:
        start_page()



# Variable to track the current thumbnail page
current_page = 0
root = tk.Tk()
root.title("QD Yt Downloader")

# Frame for thumbnails
thumbnails_frame = ttk.Frame(root)
thumbnails_frame.grid(row=1, column=0, columnspan=3)


# Initiate the search and thumbnail display page
start_page()

root.mainloop()









