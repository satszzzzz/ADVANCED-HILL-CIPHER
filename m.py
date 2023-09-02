import requests
x= requests.post('http://localhost:8000/api/upload-image/',files={'image':'C:/Users/LENOVO/OneDrive/Desktop/DJANGO PROJECTS/dog.jpg', 'key':'wuhjwfe', 'key2':'hfhgf'},  data={'mode':'-d','block_size':3,'complex_key': ''})
print(x)