# LastFM-Color-Sort
Python script that downloads all LastFM album images for a user, and creates mosaics from the artwork

# Getting Started

1. Install requirements in requirements.txt
2. Create a .env file with the following content:

```
API_KEY = "LASTFM_API_KEY"
API_SECRET = "LASTFM_API_SECRET"
USER_AGENT = "YOUR_USERAGENT"
TARGET_USER = "YOUR_USERNAME" 
```


You can create a LastFM key and secret [here](https://www.last.fm/api/account/create?_pjax=%23content).

3. Create the cache of image files and color mappings by running `python color_sort.py download`.
4. Run a sort or recolor on the cached files by using `python color_sort.py sort [output.png]  or `python color_sort.py recolor [base_image] [output.png]`

![image](https://user-images.githubusercontent.com/3819844/221431353-c9c9520e-3b8f-4c14-a6db-d92a2adb5001.png)
