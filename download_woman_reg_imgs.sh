apt update

# Define the target directory
target_dir="/workspace/regimages"

# Create the target directory if it doesn't exist
mkdir -p "$target_dir"

# List of zip file URLs
zip_urls=(
    #"https://huggingface.co/MonsterMMORPG/SECourses/resolve/main/woman_3847_imgs_raw.zip"
    "https://huggingface.co/MonsterMMORPG/SECourses/resolve/main/woman_3791_imgs_512x512px.zip"
	"https://huggingface.co/MonsterMMORPG/SECourses/resolve/main/woman_3791_imgs_768x768px.zip"
	"https://huggingface.co/MonsterMMORPG/SECourses/resolve/main/woman_3791_imgs_1024x1024px.zip"
	"https://huggingface.co/MonsterMMORPG/SECourses/resolve/main/woman_3791_imgs_1536x1536px.zip"
	"https://huggingface.co/MonsterMMORPG/SECourses/resolve/main/woman_3811_imgs_512x768px.zip"
	"https://huggingface.co/MonsterMMORPG/SECourses/resolve/main/woman_3824_imgs_768x512px.zip"
	"https://huggingface.co/MonsterMMORPG/SECourses/resolve/main/woman_3826_imgs_1024x768px.zip"
	"https://huggingface.co/MonsterMMORPG/SECourses/resolve/main/woman_3826_imgs_768x1024px.zip"
	"https://huggingface.co/MonsterMMORPG/SECourses/resolve/main/woman_3822_imgs_1280x1024px.zip"
	"https://huggingface.co/MonsterMMORPG/SECourses/resolve/main/woman_3816_imgs_1024x1280px.zip"
	"https://huggingface.co/MonsterMMORPG/SECourses/resolve/main/woman_3824_imgs_1536x1024px.zip"
	"https://huggingface.co/MonsterMMORPG/SECourses/resolve/main/woman_3811_imgs_1024x1536px.zip"
	"https://huggingface.co/MonsterMMORPG/SECourses/resolve/main/woman_3812_imgs_1536x1280px.zip"
	"https://huggingface.co/MonsterMMORPG/SECourses/resolve/main/woman_3797_imgs_1280x1536px.zip"
)

# Install p7zip-full package
yes | apt-get install p7zip-full

# Loop through the zip URLs and download/extract
for url in "${zip_urls[@]}"; do
    # Get the filename from the URL
    file_name=$(basename "$url")
    
    # Download the zip file
    wget "$url" -P "$target_dir"
    
    # Extract the zip file with password
    7z x -psecourses "$target_dir/$file_name" -o"$target_dir"
    
    # Remove the downloaded zip file
    rm "$target_dir/$file_name"
done

echo "All zip files downloaded and extracted."