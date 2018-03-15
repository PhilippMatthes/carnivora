# carnivora

![Showcase](MOCKUP.jpg?raw=true "DragTimer App")

## Installation
(Optional) Activate a virtual environment.

Install the needed dependencies:
```
sudo pip3 install scikit-image
sudo pip3 install tensorflow
sudo pip3 install selenium
sudo pip3 install urllib
sudo pip3 install urllib3
sudo pip3 install pandas
```

Next up, clone this repository with `sudo git clone https://github.com/PhilippMatthes/carnivora`.

Run the server with `sudo path/to/your/python3 manage.py runserver 127.0.0.1:8000 --noreload`

On the first start, the server will not be configured yet. Please follow the instructions in your command prompt to configure your server.

Before you can use the server properly, you must create a superuser. Type in `python manage.py createsuperuser` and follow the instructions.

Once you finished, you can now run the server with `sudo path/to/your/python3 manage.py runserver 127.0.0.1:8000 --noreload`. To see the web interface with your browser, navigate to 127.0.0.1:8000. Login with your superuser username and password.

## Deployment
Please follow the instructions on the Django website to deploy your server. Keep in mind to activate SSH before deployment. Otherwise user information like instagram passwords are transmitted insecurely.

## Links

This Project uses [tensorflow-open_nsfw](https://github.com/mdietrichstein/tensorflow-open_nsfw) by Marc Dietrichstein
for image classification and Semantic UI.

Carnivora uses the following libraries:
- skimage
- TensorFlow
- Selenium Webdriver
- urllib
- urllib3
